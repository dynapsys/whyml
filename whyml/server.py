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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .processor import WhyMLProcessor
from .exceptions import WhyMLError
from . import __version__


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
            asyncio.create_task(self.server._handle_file_change(file_path))
    
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
        auto_reload: bool = True
    ):
        self.manifest_file = Path(manifest_file)
        self.host = host
        self.port = port
        self.watch_enabled = watch
        self.auto_reload = auto_reload
        
        self.processor = WhyMLProcessor()
        self.app = web.Application()
        self.websockets: Set[web.WebSocketResponse] = set()
        
        self._observer: Optional[Observer] = None
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
        self.app.router.add_get('/api/health', self._handle_health)
        self.app.router.add_get('/api/info', self._handle_info)
        self.app.router.add_post('/api/validate', self._handle_validate)
        
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
