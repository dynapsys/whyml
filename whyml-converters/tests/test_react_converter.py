"""
Test suite for whyml_converters.react_converter module

Tests for:
- ReactConverter functionality
- JSX component generation
- React hooks integration
- TypeScript support
- Props handling
- State management

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_converters.react_converter import ReactConverter
from whyml_converters.base_converter import ConversionResult


class TestReactConverter:
    """Test cases for ReactConverter class."""
    
    @pytest.fixture
    def converter(self):
        """Create a ReactConverter instance for testing."""
        return ReactConverter()
    
    @pytest.fixture
    def simple_manifest(self) -> Dict[str, Any]:
        """Create a simple manifest for React conversion."""
        return {
            "metadata": {
                "title": "TestComponent",
                "description": "A test React component",
                "version": "1.0.0"
            },
            "structure": {
                "component": {
                    "name": "TestComponent",
                    "props": ["title", "content"],
                    "body": {
                        "div": {
                            "className": "test-container",
                            "children": [
                                {"h1": "{title}"},
                                {"p": "{content}"}
                            ]
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def component_with_state(self) -> Dict[str, Any]:
        """Create a manifest with React state management."""
        return {
            "metadata": {
                "title": "StatefulComponent",
                "description": "React component with state"
            },
            "structure": {
                "component": {
                    "name": "StatefulComponent",
                    "hooks": [
                        {
                            "type": "useState",
                            "name": "count",
                            "initial": 0
                        },
                        {
                            "type": "useEffect",
                            "dependencies": ["count"],
                            "callback": "console.log('Count changed:', count)"
                        }
                    ],
                    "body": {
                        "div": {
                            "children": [
                                {"h2": "Counter: {count}"},
                                {
                                    "button": {
                                        "onClick": "setCount(count + 1)",
                                        "text": "Increment"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
    
    def test_converter_initialization(self, converter):
        """Test ReactConverter initialization."""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'generate_jsx')
    
    def test_simple_react_conversion(self, converter, simple_manifest):
        """Test basic React component conversion."""
        result = converter.convert(simple_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'react'
        assert 'TestComponent.jsx' in result.filename or 'TestComponent.tsx' in result.filename
        
        # Check JSX content
        jsx_content = result.content
        assert 'function TestComponent' in jsx_content or 'const TestComponent' in jsx_content
        assert 'return (' in jsx_content
        assert 'className="test-container"' in jsx_content
        assert '{title}' in jsx_content
        assert '{content}' in jsx_content
    
    def test_props_handling(self, converter, simple_manifest):
        """Test React props handling."""
        result = converter.convert(simple_manifest)
        
        jsx_content = result.content
        assert '{ title, content }' in jsx_content or 'props' in jsx_content
        assert 'title' in jsx_content
        assert 'content' in jsx_content
    
    def test_typescript_conversion(self, converter, simple_manifest):
        """Test TypeScript React component conversion."""
        typescript_options = {
            'typescript': True,
            'strict_types': True
        }
        
        result = converter.convert(simple_manifest, **typescript_options)
        
        jsx_content = result.content
        assert '.tsx' in result.filename
        assert 'interface' in jsx_content or 'type' in jsx_content
        assert ': React.FC' in jsx_content or ': FC' in jsx_content
    
    def test_hooks_integration(self, converter, component_with_state):
        """Test React hooks integration."""
        result = converter.convert(component_with_state)
        
        jsx_content = result.content
        assert 'useState' in jsx_content
        assert 'useEffect' in jsx_content
        assert 'const [count, setCount]' in jsx_content
        assert 'setCount(count + 1)' in jsx_content
    
    def test_event_handlers(self, converter, component_with_state):
        """Test React event handler generation."""
        result = converter.convert(component_with_state)
        
        jsx_content = result.content
        assert 'onClick=' in jsx_content
        assert 'setCount' in jsx_content
    
    def test_component_imports(self, converter):
        """Test React import statements."""
        manifest_with_imports = {
            "metadata": {"title": "ComponentWithImports"},
            "structure": {
                "component": {
                    "name": "ComponentWithImports",
                    "imports": [
                        {"from": "react", "import": ["useState", "useEffect"]},
                        {"from": "./Button", "import": "Button"},
                        {"from": "styled-components", "import": "styled"}
                    ],
                    "body": {
                        "div": {
                            "children": [
                                {"Button": {"text": "Click me"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(manifest_with_imports)
        
        jsx_content = result.content
        assert "import { useState, useEffect } from 'react'" in jsx_content
        assert "import Button from './Button'" in jsx_content
        assert "import styled from 'styled-components'" in jsx_content
    
    def test_styled_components(self, converter):
        """Test styled-components integration."""
        styled_manifest = {
            "metadata": {"title": "StyledComponent"},
            "structure": {
                "component": {
                    "name": "StyledComponent",
                    "styles": {
                        "Container": {
                            "tag": "div",
                            "styles": {
                                "background": "#f0f0f0",
                                "padding": "20px",
                                "borderRadius": "8px"
                            }
                        }
                    },
                    "body": {
                        "Container": {
                            "children": [
                                {"h1": "Styled Content"}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(styled_manifest)
        
        jsx_content = result.content
        assert 'styled' in jsx_content
        assert 'const Container = styled.div' in jsx_content
        assert 'background: #f0f0f0' in jsx_content
        assert '<Container>' in jsx_content
    
    def test_functional_vs_class_components(self, converter, simple_manifest):
        """Test functional vs class component generation."""
        # Functional component (default)
        result_functional = converter.convert(simple_manifest, component_type='functional')
        func_content = result_functional.content
        assert 'function TestComponent' in func_content or 'const TestComponent' in func_content
        
        # Class component
        result_class = converter.convert(simple_manifest, component_type='class')
        class_content = result_class.content
        assert 'class TestComponent extends' in class_content
        assert 'render()' in class_content
    
    def test_jsx_fragments(self, converter):
        """Test JSX fragments generation."""
        fragment_manifest = {
            "metadata": {"title": "FragmentComponent"},
            "structure": {
                "component": {
                    "name": "FragmentComponent",
                    "body": {
                        "fragment": {
                            "children": [
                                {"h1": "Title"},
                                {"p": "Description"},
                                {"button": {"text": "Action"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(fragment_manifest)
        
        jsx_content = result.content
        assert '<>' in jsx_content and '</>' in jsx_content or \
               'React.Fragment' in jsx_content
    
    def test_conditional_rendering(self, converter):
        """Test conditional rendering patterns."""
        conditional_manifest = {
            "metadata": {"title": "ConditionalComponent"},
            "structure": {
                "component": {
                    "name": "ConditionalComponent",
                    "props": ["isVisible", "user"],
                    "body": {
                        "div": {
                            "children": [
                                {
                                    "condition": "isVisible",
                                    "element": {"h1": "Visible Content"}
                                },
                                {
                                    "condition": "user",
                                    "element": {"p": "Welcome, {user.name}"},
                                    "else": {"p": "Please log in"}
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(conditional_manifest)
        
        jsx_content = result.content
        assert 'isVisible &&' in jsx_content or 'isVisible ?' in jsx_content
        assert 'user ?' in jsx_content
        assert 'user.name' in jsx_content
    
    def test_list_rendering(self, converter):
        """Test list rendering with map function."""
        list_manifest = {
            "metadata": {"title": "ListComponent"},
            "structure": {
                "component": {
                    "name": "ListComponent",
                    "props": ["items"],
                    "body": {
                        "ul": {
                            "map": {
                                "array": "items",
                                "item": "item",
                                "element": {
                                    "li": {
                                        "key": "{item.id}",
                                        "text": "{item.name}"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        result = converter.convert(list_manifest)
        
        jsx_content = result.content
        assert 'items.map' in jsx_content
        assert 'key={item.id}' in jsx_content
        assert '{item.name}' in jsx_content
    
    def test_context_provider(self, converter):
        """Test React Context provider pattern."""
        context_manifest = {
            "metadata": {"title": "ContextProvider"},
            "structure": {
                "component": {
                    "name": "ContextProvider",
                    "context": {
                        "name": "ThemeContext",
                        "defaultValue": {"theme": "light"}
                    },
                    "props": ["children"],
                    "body": {
                        "ThemeContext.Provider": {
                            "value": "{contextValue}",
                            "children": ["{children}"]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(context_manifest)
        
        jsx_content = result.content
        assert 'createContext' in jsx_content
        assert 'ThemeContext' in jsx_content
        assert 'Provider' in jsx_content
    
    def test_error_boundaries(self, converter):
        """Test error boundary component generation."""
        error_boundary_manifest = {
            "metadata": {"title": "ErrorBoundary"},
            "structure": {
                "component": {
                    "name": "ErrorBoundary",
                    "type": "class",
                    "props": ["children"],
                    "state": {
                        "hasError": False
                    },
                    "methods": {
                        "componentDidCatch": {
                            "params": ["error", "errorInfo"],
                            "body": "this.setState({ hasError: true })"
                        }
                    },
                    "body": {
                        "condition": "this.state.hasError",
                        "element": {"h1": "Something went wrong."},
                        "else": "{this.props.children}"
                    }
                }
            }
        }
        
        result = converter.convert(error_boundary_manifest)
        
        jsx_content = result.content
        assert 'componentDidCatch' in jsx_content
        assert 'hasError' in jsx_content
        assert 'Something went wrong' in jsx_content
    
    def test_custom_hooks(self, converter):
        """Test custom hooks generation."""
        custom_hook_manifest = {
            "metadata": {"title": "useCounter"},
            "structure": {
                "hook": {
                    "name": "useCounter",
                    "params": ["initialValue = 0"],
                    "body": {
                        "useState": {
                            "name": "count",
                            "initial": "initialValue"
                        },
                        "methods": {
                            "increment": "() => setCount(count + 1)",
                            "decrement": "() => setCount(count - 1)",
                            "reset": "() => setCount(initialValue)"
                        },
                        "return": "{count, increment, decrement, reset}"
                    }
                }
            }
        }
        
        result = converter.convert(custom_hook_manifest)
        
        jsx_content = result.content
        assert 'function useCounter' in jsx_content
        assert 'useState' in jsx_content
        assert 'increment' in jsx_content
        assert 'return { count' in jsx_content


class TestReactConverterAdvanced:
    """Advanced test cases for ReactConverter."""
    
    @pytest.fixture
    def advanced_converter(self):
        """Create ReactConverter with advanced options."""
        return ReactConverter(
            typescript=True,
            optimize_output=True,
            include_prop_types=True
        )
    
    def test_performance_optimization(self, advanced_converter):
        """Test React performance optimization features."""
        optimized_manifest = {
            "metadata": {"title": "OptimizedComponent"},
            "structure": {
                "component": {
                    "name": "OptimizedComponent",
                    "memo": True,
                    "props": ["data", "onUpdate"],
                    "body": {
                        "div": {
                            "children": [
                                {"h1": "{data.title}"},
                                {
                                    "button": {
                                        "onClick": "onUpdate",
                                        "text": "Update"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        result = advanced_converter.convert(optimized_manifest)
        
        jsx_content = result.content
        assert 'React.memo' in jsx_content or 'memo(' in jsx_content
        assert 'useCallback' in jsx_content or 'useMemo' in jsx_content


if __name__ == "__main__":
    pytest.main([__file__])
