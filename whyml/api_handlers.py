"""
API endpoint handlers for WhyML Development Server
"""

import time
import os
import sys
from pathlib import Path
from typing import Dict, Any
import yaml
from aiohttp import web

from . import __version__


class APIHandlers:
    """API endpoint handlers for WhyML server."""
    
    def __init__(self, server):
        self.server = server
    
    async def handle_health(self, request: web.Request) -> web.Response:
        """Handle health check endpoint."""
        try:
            # Check if manifest file exists and is readable
            manifest_exists = self.server.manifest_file.exists()
            
            # Check if processor is working
            processor_status = "ok"
            try:
                # Test basic processor functionality
                test_manifest = {"metadata": {"title": "Health Check"}, "structure": {"div": {"text": "test"}}}
                await self.server.processor.convert_to_html(test_manifest)
            except Exception as e:
                processor_status = f"error: {e}"
            
            uptime = time.time() - getattr(self.server, '_start_time', time.time())
            
            health_data = {
                "status": "healthy" if manifest_exists and processor_status == "ok" else "unhealthy",
                "timestamp": time.time(),
                "uptime": uptime,
                "manifest_file": str(self.server.manifest_file),
                "manifest_exists": manifest_exists,
                "processor_status": processor_status,
                "watch_enabled": self.server.watch_enabled,
                "auto_reload": self.server.auto_reload,
                "version": __version__,
                "websocket_connections": len(self.server.websockets)
            }
            
            status_code = 200 if health_data["status"] == "healthy" else 503
            return web.json_response(health_data, status=status_code)
            
        except Exception as e:
            return web.json_response({
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }, status=500)
    
    async def handle_info(self, request: web.Request) -> web.Response:
        """Handle server info endpoint."""
        try:
            uptime = time.time() - getattr(self.server, '_start_time', time.time())
            
            info_data = {
                "server": {
                    "name": "WhyML Development Server",
                    "version": __version__,
                    "host": self.server.host,
                    "port": self.server.port,
                    "uptime": uptime,
                    "start_time": getattr(self.server, '_start_time', time.time())
                },
                "manifest": {
                    "file": str(self.server.manifest_file),
                    "exists": self.server.manifest_file.exists(),
                    "size": self.server.manifest_file.stat().st_size if self.server.manifest_file.exists() else 0,
                    "modified": self.server.manifest_file.stat().st_mtime if self.server.manifest_file.exists() else 0
                },
                "features": {
                    "watch_enabled": self.server.watch_enabled,
                    "auto_reload": self.server.auto_reload,
                    "websocket_connections": len(self.server.websockets),
                    "pending_changes": len(self.server._pending_changes)
                },
                "routes": [
                    {"method": "GET", "path": "/", "description": "Main page"},
                    {"method": "GET", "path": "/manifest", "description": "Get manifest content"},
                    {"method": "POST", "path": "/manifest", "description": "Update manifest"},
                    {"method": "GET", "path": "/convert/{format}", "description": "Convert manifest to format"},
                    {"method": "POST", "path": "/convert/{format}", "description": "Convert custom manifest"},
                    {"method": "GET", "path": "/api/health", "description": "Health check"},
                    {"method": "GET", "path": "/api/info", "description": "Server information"},
                    {"method": "GET", "path": "/api/debug/logs", "description": "Debug logs"},
                    {"method": "POST", "path": "/api/validate", "description": "Validate manifest"},
                    {"method": "GET", "path": "/ws", "description": "WebSocket for live reload"}
                ]
            }
            
            return web.json_response(info_data)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_validate(self, request: web.Request) -> web.Response:
        """Handle manifest validation endpoint."""
        try:
            # Get manifest content from request body or use default
            if request.method == 'POST':
                manifest_content = await request.text()
                
                # Parse YAML content
                try:
                    manifest_data = yaml.safe_load(manifest_content)
                except yaml.YAMLError as e:
                    return web.json_response({
                        "valid": False,
                        "errors": [f"YAML parsing error: {e}"],
                        "warnings": []
                    }, status=400)
            else:
                # Use default manifest file
                if not self.server.manifest_file.exists():
                    return web.json_response({
                        "valid": False,
                        "errors": [f"Manifest file not found: {self.server.manifest_file}"],
                        "warnings": []
                    }, status=404)
                
                manifest_data = await self.server.processor.load_manifest(str(self.server.manifest_file))
            
            # Validate using the processor
            try:
                validation_result = self.server.processor.processor.validate_manifest(manifest_data)
                
                return web.json_response({
                    "valid": validation_result.get("valid", True),
                    "errors": validation_result.get("errors", []),
                    "warnings": validation_result.get("warnings", []),
                    "manifest_data": manifest_data
                })
                
            except Exception as e:
                return web.json_response({
                    "valid": False,
                    "errors": [f"Validation error: {e}"],
                    "warnings": [],
                    "manifest_data": manifest_data
                }, status=400)
            
        except Exception as e:
            return web.json_response({
                "valid": False,
                "errors": [f"Server error: {e}"],
                "warnings": []
            }, status=500)
    
    async def handle_debug_logs(self, request: web.Request) -> web.Response:
        """Handle debug logs endpoint."""
        try:
            debug_info = {
                "timestamp": time.time(),
                "server_status": {
                    "uptime": time.time() - getattr(self.server, '_start_time', time.time()),
                    "manifest_file": str(self.server.manifest_file),
                    "manifest_exists": self.server.manifest_file.exists(),
                    "watch_enabled": self.server.watch_enabled,
                    "websocket_connections": len(self.server.websockets),
                    "pending_changes": self.server._pending_changes.copy()
                },
                "recent_activity": {
                    "file_changes": len(self.server._pending_changes),
                    "last_reload": getattr(self.server, '_last_reload', None)
                },
                "environment": {
                    "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                    "working_directory": str(Path.cwd()),
                    "whyml_version": __version__
                }
            }
            
            return web.json_response(debug_info)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
