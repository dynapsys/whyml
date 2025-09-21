"""
Test suite for whyml_converters.php_converter module

Tests for:
- PHPConverter functionality
- PHP template generation
- Database integration
- Session management
- API endpoint creation
- Security features

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_converters.php_converter import PHPConverter
from whyml_converters.base_converter import ConversionResult


class TestPHPConverter:
    """Test cases for PHPConverter class."""
    
    @pytest.fixture
    def converter(self):
        """Create a PHPConverter instance for testing."""
        return PHPConverter()
    
    @pytest.fixture
    def simple_manifest(self) -> Dict[str, Any]:
        """Create a simple manifest for PHP conversion."""
        return {
            "metadata": {
                "title": "TestPage",
                "description": "A test PHP page",
                "version": "1.0.0"
            },
            "structure": {
                "page": {
                    "title": "<?= $title ?>",
                    "body": {
                        "div": {
                            "class": "container",
                            "children": [
                                {"h1": "<?= $heading ?>"},
                                {"p": "<?= $content ?>"}
                            ]
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def dynamic_manifest(self) -> Dict[str, Any]:
        """Create a manifest with PHP dynamic features."""
        return {
            "metadata": {
                "title": "DynamicPage",
                "description": "PHP page with database integration"
            },
            "php": {
                "variables": {
                    "user_id": "$_SESSION['user_id'] ?? null",
                    "posts": "$this->getPosts()",
                    "current_time": "date('Y-m-d H:i:s')"
                },
                "functions": {
                    "getPosts": {
                        "params": ["limit = 10"],
                        "body": """
                        $pdo = Database::connect();
                        $stmt = $pdo->prepare("SELECT * FROM posts LIMIT ?");
                        $stmt->execute([$limit]);
                        return $stmt->fetchAll(PDO::FETCH_ASSOC);
                        """
                    }
                },
                "includes": [
                    "config/database.php",
                    "includes/header.php"
                ]
            },
            "structure": {
                "page": {
                    "body": {
                        "div": {
                            "class": "posts",
                            "children": [
                                {
                                    "foreach": {
                                        "array": "$posts",
                                        "key": "$key",
                                        "value": "$post",
                                        "element": {
                                            "article": {
                                                "children": [
                                                    {"h2": "<?= htmlspecialchars($post['title']) ?>"},
                                                    {"p": "<?= htmlspecialchars($post['content']) ?>"}
                                                ]
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    
    def test_converter_initialization(self, converter):
        """Test PHPConverter initialization."""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'generate_php')
    
    def test_simple_php_conversion(self, converter, simple_manifest):
        """Test basic PHP page conversion."""
        result = converter.convert(simple_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'php'
        assert 'TestPage.php' in result.filename
        
        # Check PHP content
        php_content = result.content
        assert '<?php' in php_content
        assert '<?= $title ?>' in php_content
        assert '<?= $heading ?>' in php_content
        assert '<?= $content ?>' in php_content
    
    def test_php_variables(self, converter, simple_manifest):
        """Test PHP variable handling."""
        result = converter.convert(simple_manifest)
        
        php_content = result.content
        assert '$title' in php_content
        assert '$heading' in php_content
        assert '$content' in php_content
    
    def test_dynamic_content_generation(self, converter, dynamic_manifest):
        """Test dynamic PHP content generation."""
        result = converter.convert(dynamic_manifest)
        
        php_content = result.content
        assert '$_SESSION[\'user_id\']' in php_content
        assert 'function getPosts' in php_content
        assert 'PDO::FETCH_ASSOC' in php_content
        assert 'foreach' in php_content
    
    def test_database_integration(self, converter, dynamic_manifest):
        """Test database integration features."""
        result = converter.convert(dynamic_manifest)
        
        php_content = result.content
        assert 'Database::connect()' in php_content
        assert 'prepare(' in php_content
        assert 'execute(' in php_content
        assert 'fetchAll(' in php_content
    
    def test_security_features(self, converter, dynamic_manifest):
        """Test PHP security features."""
        result = converter.convert(dynamic_manifest)
        
        php_content = result.content
        assert 'htmlspecialchars(' in php_content
        assert '$_SESSION' in php_content
        # Should use prepared statements
        assert 'prepare(' in php_content
    
    def test_includes_and_requires(self, converter, dynamic_manifest):
        """Test PHP includes and requires."""
        result = converter.convert(dynamic_manifest)
        
        php_content = result.content
        assert 'include' in php_content or 'require' in php_content
        assert 'config/database.php' in php_content
        assert 'includes/header.php' in php_content
    
    def test_form_handling(self, converter):
        """Test PHP form handling."""
        form_manifest = {
            "metadata": {"title": "ContactForm"},
            "php": {
                "post_handler": {
                    "validate": {
                        "name": "required|min:2",
                        "email": "required|email",
                        "message": "required|min:10"
                    },
                    "process": """
                    $name = filter_input(INPUT_POST, 'name', FILTER_SANITIZE_STRING);
                    $email = filter_input(INPUT_POST, 'email', FILTER_VALIDATE_EMAIL);
                    $message = filter_input(INPUT_POST, 'message', FILTER_SANITIZE_STRING);
                    
                    if ($name && $email && $message) {
                        // Send email or save to database
                        $success = true;
                    }
                    """
                }
            },
            "structure": {
                "page": {
                    "body": {
                        "form": {
                            "method": "POST",
                            "action": "",
                            "children": [
                                {"input": {"name": "name", "type": "text", "required": True}},
                                {"input": {"name": "email", "type": "email", "required": True}},
                                {"textarea": {"name": "message", "required": True}},
                                {"button": {"type": "submit", "text": "Send"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(form_manifest)
        
        php_content = result.content
        assert '$_POST' in php_content or 'INPUT_POST' in php_content
        assert 'filter_input(' in php_content
        assert 'FILTER_SANITIZE_STRING' in php_content
        assert 'FILTER_VALIDATE_EMAIL' in php_content
    
    def test_session_management(self, converter):
        """Test PHP session management."""
        session_manifest = {
            "metadata": {"title": "UserDashboard"},
            "php": {
                "session": {
                    "start": True,
                    "check_auth": True,
                    "variables": {
                        "user": "$_SESSION['user'] ?? null",
                        "is_logged_in": "isset($_SESSION['user_id'])"
                    }
                },
                "auth_check": """
                if (!isset($_SESSION['user_id'])) {
                    header('Location: login.php');
                    exit;
                }
                """
            },
            "structure": {
                "page": {
                    "body": {
                        "div": {
                            "condition": "$is_logged_in",
                            "children": [
                                {"h1": "Welcome, <?= htmlspecialchars($user['name']) ?>"},
                                {"a": {"href": "logout.php", "text": "Logout"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(session_manifest)
        
        php_content = result.content
        assert 'session_start()' in php_content
        assert '$_SESSION' in php_content
        assert 'isset($_SESSION[' in php_content
        assert 'header(\'Location:' in php_content
    
    def test_api_endpoint_generation(self, converter):
        """Test PHP API endpoint generation."""
        api_manifest = {
            "metadata": {"title": "UserAPI"},
            "php": {
                "api": True,
                "endpoints": {
                    "GET /users": {
                        "function": "getUsers",
                        "params": ["limit", "offset"],
                        "response": "json"
                    },
                    "POST /users": {
                        "function": "createUser",
                        "params": ["name", "email"],
                        "validate": {
                            "name": "required|min:2",
                            "email": "required|email"
                        },
                        "response": "json"
                    }
                },
                "functions": {
                    "getUsers": {
                        "params": ["$limit = 10", "$offset = 0"],
                        "body": """
                        $pdo = Database::connect();
                        $stmt = $pdo->prepare("SELECT * FROM users LIMIT ? OFFSET ?");
                        $stmt->execute([$limit, $offset]);
                        return $stmt->fetchAll(PDO::FETCH_ASSOC);
                        """
                    }
                }
            }
        }
        
        result = converter.convert(api_manifest)
        
        php_content = result.content
        assert 'header(\'Content-Type: application/json\')' in php_content
        assert '$_SERVER[\'REQUEST_METHOD\']' in php_content
        assert 'json_encode(' in php_content
        assert 'function getUsers' in php_content
    
    def test_template_inheritance(self, converter):
        """Test PHP template inheritance."""
        template_manifest = {
            "metadata": {"title": "ExtendedPage"},
            "php": {
                "extends": "layouts/base.php",
                "sections": {
                    "content": """
                    <h1><?= $title ?></h1>
                    <p><?= $content ?></p>
                    """,
                    "sidebar": """
                    <div class="sidebar">
                        <h3>Navigation</h3>
                        <ul>
                            <li><a href="/">Home</a></li>
                        </ul>
                    </div>
                    """
                }
            }
        }
        
        result = converter.convert(template_manifest)
        
        php_content = result.content
        assert 'include' in php_content or 'extend' in php_content
        assert 'layouts/base.php' in php_content
        assert '$content' in php_content or 'yield(' in php_content
    
    def test_mvc_structure(self, converter):
        """Test MVC structure generation."""
        mvc_manifest = {
            "metadata": {"title": "UserController"},
            "php": {
                "controller": "UserController",
                "model": "User",
                "actions": {
                    "index": {
                        "method": "GET",
                        "view": "users/index.php"
                    },
                    "show": {
                        "method": "GET",
                        "params": ["id"],
                        "view": "users/show.php"
                    },
                    "create": {
                        "method": "POST",
                        "validate": {
                            "name": "required",
                            "email": "required|email"
                        },
                        "redirect": "users/index"
                    }
                }
            }
        }
        
        result = converter.convert(mvc_manifest)
        
        php_content = result.content
        assert 'class UserController' in php_content
        assert 'function index()' in php_content
        assert 'function show(' in php_content
        assert 'function create()' in php_content
    
    def test_error_handling(self, converter):
        """Test PHP error handling."""
        error_manifest = {
            "metadata": {"title": "ErrorHandling"},
            "php": {
                "error_handling": {
                    "display_errors": False,
                    "log_errors": True,
                    "custom_handler": True
                },
                "try_catch": {
                    "try": """
                    $result = Database::query($sql);
                    """,
                    "catch": {
                        "PDOException": "$e",
                        "body": "error_log($e->getMessage()); return false;"
                    }
                }
            }
        }
        
        result = converter.convert(error_manifest)
        
        php_content = result.content
        assert 'try {' in php_content
        assert 'catch (PDOException $e)' in php_content
        assert 'error_log(' in php_content
    
    def test_caching_features(self, converter):
        """Test PHP caching features."""
        cache_manifest = {
            "metadata": {"title": "CachedPage"},
            "php": {
                "cache": {
                    "type": "file",
                    "duration": 3600,
                    "key": "page_" + "<?= $page_id ?>"
                },
                "cache_logic": """
                $cache_key = 'page_' . $page_id;
                $cached = Cache::get($cache_key);
                if ($cached) {
                    echo $cached;
                    exit;
                }
                """
            }
        }
        
        result = converter.convert(cache_manifest)
        
        php_content = result.content
        assert 'Cache::get(' in php_content
        assert '$cache_key' in php_content
        assert 'exit' in php_content or 'return' in php_content


class TestPHPConverterAdvanced:
    """Advanced test cases for PHPConverter."""
    
    @pytest.fixture
    def advanced_converter(self):
        """Create PHPConverter with advanced options."""
        return PHPConverter(
            framework='laravel',
            strict_types=True,
            optimize_output=True,
            security_level='high'
        )
    
    def test_framework_integration(self, advanced_converter):
        """Test framework-specific code generation."""
        framework_manifest = {
            "metadata": {"title": "LaravelController"},
            "php": {
                "framework": "laravel",
                "controller": {
                    "name": "PostController",
                    "extends": "Controller",
                    "middleware": ["auth", "throttle:60,1"],
                    "methods": {
                        "index": {
                            "return": "Post::paginate(15)"
                        }
                    }
                }
            }
        }
        
        result = advanced_converter.convert(framework_manifest)
        
        php_content = result.content
        assert 'namespace App\\Http\\Controllers' in php_content
        assert 'extends Controller' in php_content
        assert 'middleware(' in php_content
    
    def test_strict_types(self, advanced_converter):
        """Test strict types declaration."""
        result = advanced_converter.convert({
            "metadata": {"title": "StrictTypesTest"},
            "php": {"functions": {"test": {"params": ["string $name"], "return": "string"}}}
        })
        
        php_content = result.content
        assert 'declare(strict_types=1)' in php_content
        assert ': string' in php_content
    
    def test_security_hardening(self, advanced_converter):
        """Test security hardening features."""
        security_manifest = {
            "metadata": {"title": "SecureEndpoint"},
            "php": {
                "security": {
                    "csrf_protection": True,
                    "sql_injection_protection": True,
                    "xss_protection": True
                }
            }
        }
        
        result = advanced_converter.convert(security_manifest)
        
        php_content = result.content
        assert 'csrf_token()' in php_content or 'csrf_field()' in php_content
        assert 'htmlspecialchars(' in php_content
        assert 'prepare(' in php_content


if __name__ == "__main__":
    pytest.main([__file__])
