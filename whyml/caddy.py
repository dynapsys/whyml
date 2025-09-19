"""
Caddy Integration for WhyML

Provides Caddy reverse proxy configuration generation for WhyML applications.
Supports automatic TLS, load balancing, and production deployment configurations.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict

from .exceptions import WhyMLError


@dataclass
class TLSConfig:
    """TLS configuration for Caddy."""
    provider: str = "internal"  # internal, letsencrypt, custom
    email: Optional[str] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None
    ca_root: Optional[str] = None


@dataclass
class UpstreamConfig:
    """Upstream server configuration."""
    host: str = "localhost"
    port: int = 8080
    weight: int = 1
    max_fails: int = 3
    fail_timeout: str = "30s"


@dataclass
class CacheConfig:
    """Cache configuration for static assets."""
    enabled: bool = True
    max_age: str = "1h"
    stale_while_revalidate: str = "5m"
    patterns: List[str] = None
    
    def __post_init__(self):
        if self.patterns is None:
            self.patterns = [
                "*.css", "*.js", "*.png", "*.jpg", "*.jpeg", 
                "*.gif", "*.svg", "*.ico", "*.woff", "*.woff2"
            ]


@dataclass
class SecurityConfig:
    """Security headers and configuration."""
    hsts_enabled: bool = True
    hsts_max_age: str = "31536000"
    content_security_policy: Optional[str] = None
    x_frame_options: str = "DENY"
    x_content_type_options: str = "nosniff"
    referrer_policy: str = "strict-origin-when-cross-origin"


class CaddyConfig:
    """Caddy configuration generator for WhyML applications."""
    
    def __init__(self):
        self.config = {
            "apps": {
                "http": {
                    "servers": {}
                }
            }
        }
    
    async def generate_config(
        self,
        manifest_file: str,
        host: str = "localhost",
        port: int = 8080,
        domain: Optional[str] = None,
        tls_provider: Optional[str] = None,
        upstreams: Optional[List[UpstreamConfig]] = None,
        cache_config: Optional[CacheConfig] = None,
        security_config: Optional[SecurityConfig] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Caddy configuration for WhyML application.
        
        Args:
            manifest_file: Path to the WhyML manifest
            host: Host to bind to
            port: Port to bind to
            domain: Domain name for production deployment
            tls_provider: TLS certificate provider
            upstreams: List of upstream servers for load balancing
            cache_config: Static asset caching configuration
            security_config: Security headers configuration
            custom_config: Additional custom Caddy configuration
            
        Returns:
            Caddy configuration as JSON string
        """
        
        # Load manifest to understand the application requirements
        manifest = await self._load_manifest(manifest_file)
        
        # Set up basic server configuration
        server_name = domain if domain else f"{host}:{port}"
        
        # Configure TLS
        tls_config = self._configure_tls(tls_provider, domain)
        
        # Configure upstreams (for load balancing)
        if not upstreams:
            upstreams = [UpstreamConfig(host=host, port=port)]
        
        # Build server configuration
        server_config = {
            "listen": [f":{port}"],
            "routes": self._build_routes(
                manifest, 
                upstreams, 
                cache_config or CacheConfig(),
                security_config or SecurityConfig()
            )
        }
        
        # Add TLS configuration if needed
        if tls_config:
            server_config["tls_connection_policies"] = [tls_config]
        
        # Add automatic HTTPS redirect for production
        if domain and tls_provider:
            server_config["automatic_https"] = {
                "disable": False,
                "disable_redirects": False
            }
        
        # Apply custom configuration
        if custom_config:
            server_config.update(custom_config)
        
        # Add to main configuration
        self.config["apps"]["http"]["servers"][server_name] = server_config
        
        return json.dumps(self.config, indent=2)
    
    async def _load_manifest(self, manifest_file: str) -> Dict[str, Any]:
        """Load and parse the WhyML manifest."""
        manifest_path = Path(manifest_file)
        
        if not manifest_path.exists():
            raise WhyMLError(f"Manifest file '{manifest_file}' not found")
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                if manifest_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            raise WhyMLError(f"Failed to load manifest: {e}")
    
    def _configure_tls(self, provider: Optional[str], domain: Optional[str]) -> Optional[Dict[str, Any]]:
        """Configure TLS based on provider and domain."""
        if not provider or not domain:
            return None
        
        tls_config = {
            "match": {
                "sni": [domain]
            }
        }
        
        if provider == "letsencrypt":
            tls_config["certificate_selection"] = {
                "any_tag": ["cert0"]
            }
            # Let's Encrypt configuration would be handled in the global config
            
        elif provider == "internal":
            tls_config["certificate_selection"] = {
                "any_tag": ["local"]
            }
            
        elif provider == "custom":
            # Custom certificates would be configured separately
            pass
        
        return tls_config
    
    def _build_routes(
        self,
        manifest: Dict[str, Any],
        upstreams: List[UpstreamConfig],
        cache_config: CacheConfig,
        security_config: SecurityConfig
    ) -> List[Dict[str, Any]]:
        """Build Caddy routes based on manifest configuration."""
        routes = []
        
        # Add security headers route (applies to all requests)
        security_route = {
            "match": [{"path": ["/*"]}],
            "handle": [{
                "handler": "headers",
                "response": {
                    "set": self._build_security_headers(security_config)
                }
            }]
        }
        routes.append(security_route)
        
        # Add static asset caching route
        if cache_config.enabled:
            static_route = {
                "match": [{"path_regexp": {"pattern": r"\.(css|js|png|jpg|jpeg|gif|svg|ico|woff|woff2)$"}}],
                "handle": [
                    {
                        "handler": "headers",
                        "response": {
                            "set": {
                                "Cache-Control": [f"public, max-age={self._parse_duration(cache_config.max_age)}"],
                                "Expires": ["{{http.time_format (http.time_add (now) (duration \"{}\"))}}".format(cache_config.max_age)]
                            }
                        }
                    },
                    {
                        "handler": "file_server",
                        "root": "./assets"
                    }
                ]
            }
            routes.append(static_route)
        
        # Add API routes if defined in manifest
        api_routes = manifest.get('api', {}).get('routes', {})
        for path, config in api_routes.items():
            api_route = {
                "match": [{"path": [f"/api{path}/*"]}],
                "handle": [{
                    "handler": "reverse_proxy",
                    "upstreams": [{"dial": f"{up.host}:{up.port}"} for up in upstreams]
                }]
            }
            routes.append(api_route)
        
        # Add WebSocket route for live reload
        ws_route = {
            "match": [{"path": ["/ws"]}],
            "handle": [{
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"{up.host}:{up.port}"} for up in upstreams],
                "headers": {
                    "Connection": ["Upgrade"],
                    "Upgrade": ["websocket"]
                }
            }]
        }
        routes.append(ws_route)
        
        # Add main application route (catch-all)
        app_route = {
            "match": [{"path": ["/*"]}],
            "handle": [{
                "handler": "reverse_proxy",
                "upstreams": [{"dial": f"{up.host}:{up.port}"} for up in upstreams],
                "load_balancing": {
                    "selection_policy": {
                        "policy": "weighted_round_robin"
                    }
                },
                "health_checks": {
                    "active": {
                        "path": "/api/health",
                        "interval": "30s",
                        "timeout": "5s"
                    }
                }
            }]
        }
        routes.append(app_route)
        
        return routes
    
    def _build_security_headers(self, security_config: SecurityConfig) -> Dict[str, List[str]]:
        """Build security headers configuration."""
        headers = {}
        
        if security_config.hsts_enabled:
            headers["Strict-Transport-Security"] = [
                f"max-age={self._parse_duration(security_config.hsts_max_age)}; includeSubDomains"
            ]
        
        if security_config.content_security_policy:
            headers["Content-Security-Policy"] = [security_config.content_security_policy]
        
        headers.update({
            "X-Frame-Options": [security_config.x_frame_options],
            "X-Content-Type-Options": [security_config.x_content_type_options],
            "Referrer-Policy": [security_config.referrer_policy],
            "X-XSS-Protection": ["1; mode=block"],
            "Permissions-Policy": ["geolocation=(), microphone=(), camera=()"]
        })
        
        return headers
    
    def _parse_duration(self, duration: str) -> str:
        """Parse duration string to seconds for cache headers."""
        duration = duration.lower().strip()
        
        multipliers = {
            's': 1, 'sec': 1, 'second': 1, 'seconds': 1,
            'm': 60, 'min': 60, 'minute': 60, 'minutes': 60,
            'h': 3600, 'hour': 3600, 'hours': 3600,
            'd': 86400, 'day': 86400, 'days': 86400,
            'w': 604800, 'week': 604800, 'weeks': 604800
        }
        
        import re
        match = re.match(r'(\d+)\s*([a-z]+)?', duration)
        if not match:
            return "3600"  # Default 1 hour
        
        value = int(match.group(1))
        unit = match.group(2) or 's'
        
        multiplier = multipliers.get(unit, 1)
        return str(value * multiplier)
    
    def generate_caddyfile(
        self,
        domain: str,
        upstreams: List[str],
        tls_email: Optional[str] = None,
        static_dir: str = "./assets"
    ) -> str:
        """
        Generate a Caddyfile (text format) for simple deployments.
        
        Args:
            domain: Domain name for the site
            upstreams: List of upstream servers (host:port)
            tls_email: Email for Let's Encrypt
            static_dir: Directory containing static assets
            
        Returns:
            Caddyfile content as string
        """
        
        caddyfile = f"""# WhyML Caddy Configuration
{domain} {{
    # TLS Configuration"""
        
        if tls_email:
            caddyfile += f"""
    tls {tls_email}"""
        else:
            caddyfile += """
    tls internal"""
        
        caddyfile += f"""
    
    # Security Headers
    header {{
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        X-XSS-Protection "1; mode=block"
        Permissions-Policy "geolocation=(), microphone=(), camera=()"
    }}
    
    # Static Assets with Caching
    @static {{
        path *.css *.js *.png *.jpg *.jpeg *.gif *.svg *.ico *.woff *.woff2
    }}
    handle @static {{
        header Cache-Control "public, max-age=3600"
        file_server {{
            root {static_dir}
        }}
    }}
    
    # WebSocket Support for Live Reload
    @websocket {{
        header Connection *Upgrade*
        header Upgrade websocket
        path /ws
    }}
    handle @websocket {{
        reverse_proxy {' '.join(upstreams)}
    }}
    
    # API Routes
    handle /api/* {{
        reverse_proxy {' '.join(upstreams)} {{
            health_path /api/health
            health_interval 30s
            health_timeout 5s
        }}
    }}
    
    # Main Application (SPA support)
    handle /* {{
        reverse_proxy {' '.join(upstreams)} {{
            health_path /api/health
            health_interval 30s
            health_timeout 5s
        }}
        
        # SPA fallback for client-side routing
        try_files {{path}} {{path}}/ /index.html
    }}
    
    # Logging
    log {{
        output file /var/log/caddy/{domain}.log {{
            roll_size 100mb
            roll_keep 5
            roll_keep_for 720h
        }}
    }}
}}

# HTTP to HTTPS redirect
http://{domain} {{
    redir https://{domain}{{path}} permanent
}}
"""
        
        return caddyfile
    
    def generate_docker_compose(
        self,
        domain: str,
        whyml_image: str = "whyml:latest",
        caddy_version: str = "2.7-alpine"
    ) -> str:
        """
        Generate Docker Compose configuration for production deployment.
        
        Args:
            domain: Domain name for the site
            whyml_image: WhyML Docker image name
            caddy_version: Caddy Docker image version
            
        Returns:
            Docker Compose YAML content
        """
        
        compose_config = {
            'version': '3.8',
            'services': {
                'whyml-app': {
                    'image': whyml_image,
                    'restart': 'unless-stopped',
                    'environment': [
                        'NODE_ENV=production',
                        'WHYML_HOST=0.0.0.0',
                        'WHYML_PORT=8080'
                    ],
                    'volumes': [
                        './manifests:/app/manifests:ro',
                        './assets:/app/assets:ro',
                        './config:/app/config:ro'
                    ],
                    'networks': ['whyml-network'],
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8080/api/health'],
                        'interval': '30s',
                        'timeout': '10s',
                        'retries': 3
                    }
                },
                'caddy': {
                    'image': f'caddy:{caddy_version}',
                    'restart': 'unless-stopped',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        './Caddyfile:/etc/caddy/Caddyfile:ro',
                        './assets:/srv/assets:ro',
                        'caddy-data:/data',
                        'caddy-config:/config',
                        '/var/log/caddy:/var/log/caddy'
                    ],
                    'networks': ['whyml-network'],
                    'depends_on': ['whyml-app'],
                    'environment': [
                        f'DOMAIN={domain}'
                    ]
                }
            },
            'networks': {
                'whyml-network': {
                    'driver': 'bridge'
                }
            },
            'volumes': {
                'caddy-data': {},
                'caddy-config': {}
            }
        }
        
        return yaml.dump(compose_config, default_flow_style=False, sort_keys=False)


# Utility functions
def create_production_config(
    domain: str,
    email: str,
    upstreams: Optional[List[str]] = None,
    output_dir: str = "./deploy"
) -> Dict[str, str]:
    """
    Create a complete production deployment configuration.
    
    Args:
        domain: Production domain name
        email: Email for Let's Encrypt certificates
        upstreams: List of upstream servers (defaults to localhost:8080)
        output_dir: Directory to write configuration files
        
    Returns:
        Dictionary of generated files and their paths
    """
    if not upstreams:
        upstreams = ["localhost:8080"]
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    caddy_config = CaddyConfig()
    
    # Generate Caddyfile
    caddyfile_content = caddy_config.generate_caddyfile(
        domain=domain,
        upstreams=upstreams,
        tls_email=email
    )
    
    # Generate Docker Compose
    compose_content = caddy_config.generate_docker_compose(domain=domain)
    
    # Write files
    files = {}
    
    caddyfile_path = output_path / "Caddyfile"
    with open(caddyfile_path, 'w') as f:
        f.write(caddyfile_content)
    files['caddyfile'] = str(caddyfile_path)
    
    compose_path = output_path / "docker-compose.yml"
    with open(compose_path, 'w') as f:
        f.write(compose_content)
    files['compose'] = str(compose_path)
    
    # Generate environment file template
    env_content = f"""# WhyML Production Environment
DOMAIN={domain}
TLS_EMAIL={email}
WHYML_HOST=0.0.0.0
WHYML_PORT=8080
NODE_ENV=production

# Database (if needed)
# DATABASE_URL=postgresql://user:pass@db:5432/whyml

# Redis (if needed) 
# REDIS_URL=redis://redis:6379/0

# Monitoring
# SENTRY_DSN=your_sentry_dsn_here
"""
    
    env_path = output_path / ".env.production"
    with open(env_path, 'w') as f:
        f.write(env_content)
    files['env'] = str(env_path)
    
    return files
