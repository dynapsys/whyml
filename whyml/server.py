"""
WhyML Development Server

Provides a development server for serving and live-reloading WhyML manifests.
Includes file watching, hot reload, and real-time conversion capabilities.
"""

import asyncio
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, Set
import time
import mimetypes
from urllib.parse import urlparse, parse_qs

import aiohttp
from aiohttp import web, WSMsgType
from aiofiles import open as aio_open
import yaml
try:
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    class Observer:
        def __init__(self):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
try:
    from watchdog.events import FileSystemEventHandler
except ImportError:
    class FileSystemEventHandler:
        def __init__(self):
            pass
        def on_modified(self, event):
            pass

from .processor import WhyMLProcessor
from .exceptions import WhyMLError
from . import __version__
from .api_handlers import APIHandlers


class ManifestFileHandler(FileSystemEventHandler):
    """File system event handler for manifest changes."""
    
    def __init__(self, server: 'WhyMLServer'):
        self.server = server
        self.debounce_time = 0.5  # 500ms debounce
        self.last_modified = {}
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        current_time = time.time()
        
        # Debounce rapid file changes
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
        
        self.last_modified[file_path] = current_time
        
        # Check if it's a file we care about
        if file_path.endswith(('.yaml', '.yml', '.json', '.html', '.css', '.js')):
            # Log the file change for RSS feed
            self.server._log_file_change(file_path, "modified")
            
            # Use thread-safe approach to schedule the coroutine
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.server._handle_file_change(file_path), loop)
                else:
                    # If no loop is running, store the change for later processing
                    self.server._pending_changes.append(file_path)
            except RuntimeError:
                # No event loop in current thread, store for later processing
                self.server._pending_changes.append(file_path)
    
    def on_created(self, event):
        """Handle file creation events."""
        self.on_modified(event)


class WhyMLServer:
    """Development server for WhyML manifests."""
    
    def __init__(
        self,
        manifest_file: str = 'manifest.yaml',
        host: str = 'localhost',
        port: int = 8080,
        watch: bool = True,
        auto_reload: bool = True,
        api_debug: bool = False,
        rss_enabled: bool = False
    ):
        self.manifest_file = Path(manifest_file)
        self.host = host
        self.port = port
        self.watch_enabled = watch
        self.auto_reload = auto_reload
        self.api_debug = api_debug
        self.rss_enabled = rss_enabled
        
        self.processor = WhyMLProcessor()
        self.app = web.Application()
        self.websockets: Set[web.WebSocketResponse] = set()
        self._pending_changes = []  # Store file changes when no event loop is available
        self._file_changes_log = []  # Log of file changes for RSS feed
        
        self._observer: Optional[Observer] = None
        self.api_handlers = APIHandlers(self)  # Initialize API handlers
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure server routes."""
        # Main routes
        self.app.router.add_get('/', self._handle_index)
        self.app.router.add_get('/manifest', self._handle_manifest)
        self.app.router.add_post('/manifest', self._handle_manifest_update)
        
        # Conversion endpoints
        self.app.router.add_get('/convert/{format}', self._handle_convert)
        self.app.router.add_post('/convert/{format}', self._handle_convert_post)
        
        # WebSocket for live reload
        self.app.router.add_get('/ws', self._handle_websocket)
        
        # Static files and assets
        self.app.router.add_get('/assets/{path:.*}', self._handle_static)
        
        # API endpoints
        self.app.router.add_get('/api/health', self.api_handlers.handle_health)
        self.app.router.add_get('/api/info', self.api_handlers.handle_info)
        self.app.router.add_post('/api/validate', self.api_handlers.handle_validate)
        self.app.router.add_get('/api/debug/logs', self.api_handlers.handle_debug_logs)
        
        # RSS feed for file changes
        self.app.router.add_get('/rss/changes.xml', self._handle_rss_feed)
        
        # Catch-all for SPA routing
        self.app.router.add_get('/{path:.*}', self._handle_spa_fallback)
    
    async def _handle_index(self, request: web.Request) -> web.Response:
        """Serve the main page with converted manifest."""
        try:
            if not self.manifest_file.exists():
                return web.Response(
                    text=self._generate_error_page(f"Manifest file '{self.manifest_file}' not found"),
                    content_type='text/html'
                )
            
            # Convert manifest to HTML
            result = await self.processor.convert_to_html(str(self.manifest_file))
            
            # Inject live reload script if enabled
            html_content = result.content
            if self.auto_reload:
                html_content = self._inject_live_reload_script(html_content)
            
            return web.Response(text=html_content, content_type='text/html')
            
        except WhyMLError as e:
            return web.Response(
                text=self._generate_error_page(f"WhyML Error: {e}"),
                content_type='text/html'
            )
        except Exception as e:
            return web.Response(
                text=self._generate_error_page(f"Server Error: {e}"),
                content_type='text/html'
            )
    
    async def _handle_manifest(self, request: web.Request) -> web.Response:
        """Serve or update the raw manifest."""
        if request.method == 'GET':
            try:
                async with aio_open(self.manifest_file, 'r') as f:
                    content = await f.read()
                
                if self.manifest_file.suffix.lower() in ['.yaml', '.yml']:
                    return web.Response(text=content, content_type='application/x-yaml')
                else:
                    return web.Response(text=content, content_type='application/json')
                    
            except FileNotFoundError:
                return web.Response(
                    text=f"Manifest file '{self.manifest_file}' not found",
                    status=404
                )
    
    async def _handle_manifest_update(self, request: web.Request) -> web.Response:
        """Handle manifest updates via POST."""
        try:
            content = await request.text()
            
            # Validate the content
            if self.manifest_file.suffix.lower() in ['.yaml', '.yml']:
                yaml.safe_load(content)  # Validate YAML
            else:
                json.loads(content)  # Validate JSON
            
            # Write to file
            async with aio_open(self.manifest_file, 'w') as f:
                await f.write(content)
            
            # Notify connected clients
            await self._broadcast_reload()
            
            return web.json_response({"status": "success", "message": "Manifest updated"})
            
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            return web.json_response(
                {"status": "error", "message": f"Invalid format: {e}"},
                status=400
            )
        except Exception as e:
            return web.json_response(
                {"status": "error", "message": f"Update failed: {e}"},
                status=500
            )
    
    async def _handle_convert(self, request: web.Request) -> web.Response:
        """Handle format conversion requests."""
        format_type = request.match_info['format']
        
        try:
            converters = {
                'html': self.processor.convert_to_html,
                'react': self.processor.convert_to_react,
                'vue': self.processor.convert_to_vue,
                'php': self.processor.convert_to_php,
            }
            
            converter = converters.get(format_type)
            if not converter:
                return web.json_response(
                    {"error": f"Unsupported format: {format_type}"},
                    status=400
                )
            
            result = await converter(str(self.manifest_file))
            
            # Determine content type
            content_types = {
                'html': 'text/html',
                'react': 'text/javascript',
                'vue': 'text/javascript',
                'php': 'text/x-php',
            }
            
            content_type = content_types.get(format_type, 'text/plain')
            return web.Response(text=result.content, content_type=content_type)
            
        except WhyMLError as e:
            return web.json_response({"error": str(e)}, status=400)
        except Exception as e:
            return web.json_response({"error": f"Conversion failed: {e}"}, status=500)
    
    async def _handle_convert_post(self, request: web.Request) -> web.Response:
        """Handle POST conversion with custom manifest content."""
        format_type = request.match_info['format']
        
        try:
            # Get manifest content from POST body
            manifest_content = await request.text()
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(manifest_content)
                temp_file = f.name
            
            try:
                converters = {
                    'html': self.processor.convert_to_html,
                    'react': self.processor.convert_to_react,
                    'vue': self.processor.convert_to_vue,
                    'php': self.processor.convert_to_php,
                }
                
                converter = converters.get(format_type)
                if not converter:
                    return web.json_response(
                        {"error": f"Unsupported format: {format_type}"},
                        status=400
                    )
                
                result = await converter(temp_file)
                
                return web.json_response({
                    "status": "success",
                    "content": result.content,
                    "metadata": result.metadata
                })
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return web.json_response({"error": f"Conversion failed: {e}"}, status=500)
    
    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections for live reload."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.websockets.add(ws)
        
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    # Handle client messages (ping, etc.)
                    data = json.loads(msg.data)
                    if data.get('type') == 'ping':
                        await ws.send_str(json.dumps({"type": "pong"}))
                elif msg.type == WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
                    
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            self.websockets.discard(ws)
        
        return ws
    
    async def _handle_static(self, request: web.Request) -> web.Response:
        """Handle static file serving."""
        file_path = request.match_info['path']
        full_path = Path('assets') / file_path
        
        if not full_path.exists() or not full_path.is_file():
            return web.Response(status=404)
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(full_path))
        if not content_type:
            content_type = 'application/octet-stream'
        
        async with aio_open(full_path, 'rb') as f:
            content = await f.read()
        
        return web.Response(body=content, content_type=content_type)
    
    async def _handle_health(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response({
            "status": "healthy",
            "version": __version__,
            "manifest": str(self.manifest_file),
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        })
    
    async def _handle_info(self, request: web.Request) -> web.Response:
        """Server information endpoint."""
        return web.json_response({
            "whyml_version": __version__,
            "manifest_file": str(self.manifest_file),
            "host": self.host,
            "port": self.port,
            "watch_enabled": self.watch_enabled,
            "auto_reload": self.auto_reload,
            "connected_clients": len(self.websockets)
        })
    
    async def _handle_validate(self, request: web.Request) -> web.Response:
        """Validate manifest endpoint."""
        try:
            manifest_content = await request.text()
            
            # Create temporary file for validation
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(manifest_content)
                temp_file = f.name
            
            try:
                is_valid, errors = await self.processor.validate_manifest(temp_file)
                
                return web.json_response({
                    "valid": is_valid,
                    "errors": errors if not is_valid else []
                })
                
            finally:
                os.unlink(temp_file)
                
        except Exception as e:
            return web.json_response({
                "valid": False,
                "errors": [f"Validation error: {e}"]
            }, status=400)
    
    async def _handle_spa_fallback(self, request: web.Request) -> web.Response:
        """Handle SPA routing fallback."""
        # For SPA applications, serve the index page for unknown routes
        return await self._handle_index(request)
    
    def _inject_live_reload_script(self, html_content: str) -> str:
        """Inject live reload WebSocket script into HTML."""
        script = f"""
        <script>
        (function() {{
            const ws = new WebSocket('ws://{self.host}:{self.port}/ws');
            
            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.type === 'reload') {{
                    window.location.reload();
                }}
            }};
            
            ws.onclose = function() {{
                setTimeout(() => {{
                    window.location.reload();
                }}, 1000);
            }};
            
            // Send periodic pings to keep connection alive
            setInterval(() => {{
                if (ws.readyState === WebSocket.OPEN) {{
                    ws.send(JSON.stringify({{type: 'ping'}}));
                }}
            }}, 30000);
        }})();
        </script>
        """
        
        # Insert script before closing body tag or at the end
        if '</body>' in html_content:
            return html_content.replace('</body>', f'{script}\n</body>')
        else:
            return html_content + script
    
    def _generate_error_page(self, error_message: str) -> str:
        """Generate a styled error page."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>WhyML Server Error</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 2rem;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .error-container {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 3rem;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    max-width: 500px;
                }}
                h1 {{
                    margin-top: 0;
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }}
                .error-message {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 1rem;
                    border-radius: 10px;
                    margin: 1rem 0;
                    font-family: monospace;
                }}
                .server-info {{
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <div class="error-container">
                <h1>🚨 WhyML Error</h1>
                <div class="error-message">{error_message}</div>
                <div class="server-info">
                    WhyML Development Server v{__version__}<br>
                    Serving: {self.manifest_file}<br>
                    <a href="/" style="color: white;">↻ Reload Page</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def _handle_file_change(self, file_path: str):
        """Handle file system changes."""
        print(f"File changed: {file_path}")
        await self._broadcast_reload()
    
    async def _broadcast_reload(self):
        """Broadcast reload message to all connected WebSocket clients."""
        if not self.websockets:
            return
        
        message = json.dumps({"type": "reload"})
        
        # Remove closed connections and send to active ones
        active_sockets = set()
        for ws in self.websockets:
            if not ws.closed:
                try:
                    await ws.send_str(message)
                    active_sockets.add(ws)
                except Exception:
                    pass  # Connection closed
        
        self.websockets = active_sockets
    
    def _setup_file_watching(self):
        """Set up file system watching."""
        if not self.watch_enabled:
            return
        
        self._observer = Observer()
        handler = ManifestFileHandler(self)
        
        # Watch the manifest file's directory
        watch_path = self.manifest_file.parent.absolute()
        self._observer.schedule(handler, str(watch_path), recursive=True)
        
        # Also watch common asset directories if they exist
        for asset_dir in ['assets', 'static', 'public']:
            asset_path = Path(asset_dir)
            if asset_path.exists():
                self._observer.schedule(handler, str(asset_path), recursive=True)
        
        self._observer.start()
        print(f"📁 Watching files in: {watch_path}")
    
    async def start(self):
        """Start the development server."""
        self._start_time = time.time()
        
        # Setup file watching
        self._setup_file_watching()
        
        # Create and start the web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        print(f"🚀 WhyML Server started at http://{self.host}:{self.port}")
        print(f"📄 Manifest: {self.manifest_file}")
        if self.watch_enabled:
            print("👀 File watching enabled")
        if self.auto_reload:
            print("🔄 Auto-reload enabled")
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopping...")
        finally:
            if self._observer:
                self._observer.stop()
                self._observer.join()
            await runner.cleanup()

    async def _handle_rss_feed(self, request: web.Request) -> web.Response:
        """Handle RSS feed for file changes."""
        try:
            from datetime import datetime
            import xml.etree.ElementTree as ET
            
            # Create RSS XML structure
            rss = ET.Element("rss", version="2.0")
            channel = ET.SubElement(rss, "channel")
            
            # RSS channel metadata
            ET.SubElement(channel, "title").text = f"WhyML File Changes - {self.manifest_file.name}"
            ET.SubElement(channel, "description").text = "Real-time file changes from WhyML development server"
            ET.SubElement(channel, "link").text = f"http://{self.host}:{self.port}"
            ET.SubElement(channel, "lastBuildDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
            ET.SubElement(channel, "generator").text = f"WhyML Server v{__version__}"
            
            # Add recent file changes as RSS items (limit to last 50)
            recent_changes = self._file_changes_log[-50:] if self._file_changes_log else []
            
            for change in reversed(recent_changes):  # Most recent first
                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = f"File changed: {change['file']}"
                ET.SubElement(item, "description").text = f"File '{change['file']}' was {change['action']} at {change['timestamp']}"
                ET.SubElement(item, "pubDate").text = change['pub_date']
                ET.SubElement(item, "guid").text = f"{change['file']}#{change['timestamp']}"
                ET.SubElement(item, "link").text = f"http://{self.host}:{self.port}"
            
            # If no changes yet, add a placeholder item
            if not recent_changes:
                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = "WhyML Server Started"
                ET.SubElement(item, "description").text = f"WhyML development server started and watching {self.manifest_file}"
                ET.SubElement(item, "pubDate").text = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
                ET.SubElement(item, "guid").text = f"server-start#{getattr(self, '_start_time', time.time())}"
            
            # Convert to XML string
            xml_content = ET.tostring(rss, encoding='unicode', method='xml')
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_content}'
            
            return web.Response(
                text=xml_content,
                content_type='application/rss+xml; charset=utf-8'
            )
            
        except Exception as e:
            return web.Response(
                text=f"<?xml version='1.0' encoding='UTF-8'?>\n<error>RSS feed error: {e}</error>",
                content_type='application/xml; charset=utf-8',
                status=500
            )
    
    def _log_file_change(self, file_path: str, action: str = "modified"):
        """Log a file change for RSS feed."""
        from datetime import datetime
        
        change_entry = {
            'file': str(file_path),
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'pub_date': datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        }
        
        self._file_changes_log.append(change_entry)
        
        # Keep only last 100 changes to prevent memory issues
        if len(self._file_changes_log) > 100:
            self._file_changes_log = self._file_changes_log[-100:]


# Convenience function for quick server startup
async def serve_manifest(
    manifest_file: str = 'manifest.yaml',
    host: str = 'localhost',
    port: int = 8080,
    watch: bool = True
):
    """Convenience function to start serving a manifest."""
    server = WhyMLServer(
        manifest_file=manifest_file,
        host=host,
        port=port,
        watch=watch
    )
    await server.start()


if __name__ == '__main__':
    # Allow running server directly
    import sys
    
    manifest_file = sys.argv[1] if len(sys.argv) > 1 else 'manifest.yaml'
    asyncio.run(serve_manifest(manifest_file))
