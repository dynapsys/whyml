"""
Test suite for whyml_converters.vue_converter module

Tests for:
- VueConverter functionality
- Vue 3 SFC generation
- Composition API support
- Template compilation
- Reactive state management
- TypeScript integration

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from whyml_converters.vue_converter import VueConverter
from whyml_converters.base_converter import ConversionResult


class TestVueConverter:
    """Test cases for VueConverter class."""
    
    @pytest.fixture
    def converter(self):
        """Create a VueConverter instance for testing."""
        return VueConverter()
    
    @pytest.fixture
    def simple_manifest(self) -> Dict[str, Any]:
        """Create a simple manifest for Vue conversion."""
        return {
            "metadata": {
                "title": "TestComponent",
                "description": "A test Vue component",
                "version": "1.0.0"
            },
            "structure": {
                "component": {
                    "name": "TestComponent",
                    "props": ["title", "content"],
                    "template": {
                        "div": {
                            "class": "test-container",
                            "children": [
                                {"h1": "{{ title }}"},
                                {"p": "{{ content }}"}
                            ]
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def composition_api_manifest(self) -> Dict[str, Any]:
        """Create a manifest using Vue Composition API."""
        return {
            "metadata": {
                "title": "CompositionComponent",
                "description": "Vue component with Composition API"
            },
            "structure": {
                "component": {
                    "name": "CompositionComponent",
                    "api": "composition",
                    "props": ["initialCount"],
                    "setup": {
                        "reactive": {
                            "state": {
                                "count": "props.initialCount || 0"
                            }
                        },
                        "methods": {
                            "increment": "() => state.count++",
                            "decrement": "() => state.count--"
                        },
                        "computed": {
                            "doubleCount": "computed(() => state.count * 2)"
                        },
                        "return": ["state", "increment", "decrement", "doubleCount"]
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"h2": "Count: {{ state.count }}"},
                                {"p": "Double: {{ doubleCount }}"},
                                {"button": {"@click": "increment", "text": "+"}}
                            ]
                        }
                    }
                }
            }
        }
    
    def test_converter_initialization(self, converter):
        """Test VueConverter initialization."""
        assert converter is not None
        assert hasattr(converter, 'convert')
        assert hasattr(converter, 'generate_sfc')
    
    def test_simple_vue_conversion(self, converter, simple_manifest):
        """Test basic Vue SFC conversion."""
        result = converter.convert(simple_manifest)
        
        assert isinstance(result, ConversionResult)
        assert result.format_type == 'vue'
        assert 'TestComponent.vue' in result.filename
        
        # Check Vue SFC content
        vue_content = result.content
        assert '<template>' in vue_content
        assert '<script>' in vue_content
        assert 'export default' in vue_content
        assert '{{ title }}' in vue_content
        assert '{{ content }}' in vue_content
    
    def test_props_definition(self, converter, simple_manifest):
        """Test Vue props definition."""
        result = converter.convert(simple_manifest)
        
        vue_content = result.content
        assert 'props:' in vue_content or 'defineProps' in vue_content
        assert 'title' in vue_content
        assert 'content' in vue_content
    
    def test_options_api_conversion(self, converter, simple_manifest):
        """Test Vue Options API component generation."""
        result = converter.convert(simple_manifest, api_style='options')
        
        vue_content = result.content
        assert 'export default {' in vue_content
        assert 'name:' in vue_content
        assert 'props:' in vue_content
    
    def test_composition_api_conversion(self, converter, composition_api_manifest):
        """Test Vue Composition API component generation."""
        result = converter.convert(composition_api_manifest)
        
        vue_content = result.content
        assert 'setup(' in vue_content
        assert 'reactive(' in vue_content
        assert 'computed(' in vue_content
        assert 'return {' in vue_content
        assert 'state.count' in vue_content
    
    def test_typescript_support(self, converter, simple_manifest):
        """Test TypeScript Vue component generation."""
        typescript_options = {
            'typescript': True,
            'strict_types': True
        }
        
        result = converter.convert(simple_manifest, **typescript_options)
        
        vue_content = result.content
        assert '<script lang="ts">' in vue_content or '<script setup lang="ts">' in vue_content
        assert 'interface Props' in vue_content or 'defineProps<' in vue_content
    
    def test_scoped_styles(self, converter):
        """Test scoped CSS generation."""
        styled_manifest = {
            "metadata": {"title": "StyledComponent"},
            "structure": {
                "component": {
                    "name": "StyledComponent",
                    "template": {
                        "div": {
                            "class": "container",
                            "children": [
                                {"h1": {"class": "title", "text": "Styled Title"}}
                            ]
                        }
                    },
                    "styles": {
                        "scoped": True,
                        "css": """
                        .container {
                            padding: 20px;
                            background: #f5f5f5;
                        }
                        .title {
                            color: #333;
                            font-size: 2rem;
                        }
                        """
                    }
                }
            }
        }
        
        result = converter.convert(styled_manifest)
        
        vue_content = result.content
        assert '<style scoped>' in vue_content
        assert '.container {' in vue_content
        assert 'padding: 20px' in vue_content
    
    def test_reactive_data(self, converter):
        """Test reactive data handling."""
        reactive_manifest = {
            "metadata": {"title": "ReactiveComponent"},
            "structure": {
                "component": {
                    "name": "ReactiveComponent",
                    "data": {
                        "message": "Hello Vue!",
                        "count": 0,
                        "items": ["item1", "item2", "item3"]
                    },
                    "methods": {
                        "updateMessage": "this.message = 'Updated!'",
                        "addItem": "this.items.push(`Item ${this.items.length + 1}`)"
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"h1": "{{ message }}"},
                                {"p": "Count: {{ count }}"},
                                {"button": {"@click": "updateMessage", "text": "Update"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(reactive_manifest)
        
        vue_content = result.content
        assert 'data()' in vue_content or 'ref(' in vue_content
        assert 'message:' in vue_content
        assert 'methods:' in vue_content or 'function updateMessage' in vue_content
    
    def test_computed_properties(self, converter):
        """Test computed properties generation."""
        computed_manifest = {
            "metadata": {"title": "ComputedComponent"},
            "structure": {
                "component": {
                    "name": "ComputedComponent",
                    "props": ["firstName", "lastName"],
                    "computed": {
                        "fullName": "this.firstName + ' ' + this.lastName",
                        "initials": "this.firstName.charAt(0) + this.lastName.charAt(0)"
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"h1": "{{ fullName }}"},
                                {"p": "Initials: {{ initials }}"}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(computed_manifest)
        
        vue_content = result.content
        assert 'computed:' in vue_content or 'computed(' in vue_content
        assert 'fullName' in vue_content
        assert 'initials' in vue_content
    
    def test_event_handling(self, converter):
        """Test Vue event handling."""
        event_manifest = {
            "metadata": {"title": "EventComponent"},
            "structure": {
                "component": {
                    "name": "EventComponent",
                    "data": {"counter": 0},
                    "methods": {
                        "increment": "this.counter++",
                        "handleClick": "(event) => console.log('Clicked:', event)",
                        "handleInput": "(value) => this.inputValue = value"
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"button": {"@click": "increment", "text": "Count: {{ counter }}"}},
                                {"input": {"@input": "handleInput($event.target.value)"}},
                                {"div": {"@click": "handleClick", "text": "Click me"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(event_manifest)
        
        vue_content = result.content
        assert '@click=' in vue_content
        assert '@input=' in vue_content
        assert 'increment' in vue_content
    
    def test_watchers(self, converter):
        """Test Vue watchers generation."""
        watcher_manifest = {
            "metadata": {"title": "WatcherComponent"},
            "structure": {
                "component": {
                    "name": "WatcherComponent",
                    "data": {"searchTerm": "", "results": []},
                    "watch": {
                        "searchTerm": {
                            "handler": "this.performSearch(newVal)",
                            "immediate": True
                        }
                    },
                    "methods": {
                        "performSearch": "(term) => { /* search logic */ }"
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"input": {"v-model": "searchTerm", "placeholder": "Search..."}},
                                {"div": {"v-for": "result in results", "key": "result.id", "text": "{{ result.name }}"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(watcher_manifest)
        
        vue_content = result.content
        assert 'watch:' in vue_content or 'watchEffect(' in vue_content
        assert 'searchTerm' in vue_content
        assert 'immediate: true' in vue_content or 'immediate' in vue_content
    
    def test_lifecycle_hooks(self, converter):
        """Test Vue lifecycle hooks."""
        lifecycle_manifest = {
            "metadata": {"title": "LifecycleComponent"},
            "structure": {
                "component": {
                    "name": "LifecycleComponent",
                    "data": {"mounted": False},
                    "lifecycle": {
                        "mounted": "this.mounted = true; console.log('Component mounted')",
                        "beforeUnmount": "console.log('Component unmounting')",
                        "created": "console.log('Component created')"
                    },
                    "template": {
                        "div": {
                            "text": "Mounted: {{ mounted }}"
                        }
                    }
                }
            }
        }
        
        result = converter.convert(lifecycle_manifest)
        
        vue_content = result.content
        assert 'mounted()' in vue_content or 'onMounted(' in vue_content
        assert 'beforeUnmount()' in vue_content or 'onBeforeUnmount(' in vue_content
    
    def test_v_directives(self, converter):
        """Test Vue directives generation."""
        directives_manifest = {
            "metadata": {"title": "DirectivesComponent"},
            "structure": {
                "component": {
                    "name": "DirectivesComponent",
                    "data": {
                        "showElement": True,
                        "items": ["item1", "item2", "item3"],
                        "inputValue": ""
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"div": {"v-if": "showElement", "text": "Conditional element"}},
                                {"div": {"v-else": True, "text": "Alternative element"}},
                                {"input": {"v-model": "inputValue", "placeholder": "Type here"}},
                                {"ul": {
                                    "children": [
                                        {"li": {"v-for": "item in items", "key": "item", "text": "{{ item }}"}}
                                    ]
                                }},
                                {"button": {"v-on:click": "showElement = !showElement", "text": "Toggle"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(directives_manifest)
        
        vue_content = result.content
        assert 'v-if=' in vue_content
        assert 'v-else' in vue_content
        assert 'v-model=' in vue_content
        assert 'v-for=' in vue_content
        assert 'v-on:click=' in vue_content or '@click=' in vue_content
    
    def test_component_composition(self, converter):
        """Test Vue component composition and imports."""
        composition_manifest = {
            "metadata": {"title": "ParentComponent"},
            "structure": {
                "component": {
                    "name": "ParentComponent",
                    "components": {
                        "ChildComponent": "./ChildComponent.vue",
                        "BaseButton": "@/components/BaseButton.vue"
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"ChildComponent": {"prop1": "value1"}},
                                {"BaseButton": {"@click": "handleClick", "text": "Click me"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = converter.convert(composition_manifest)
        
        vue_content = result.content
        assert 'import ChildComponent from' in vue_content
        assert 'import BaseButton from' in vue_content
        assert 'components:' in vue_content
        assert '<ChildComponent' in vue_content
        assert '<BaseButton' in vue_content


class TestVueConverterAdvanced:
    """Advanced test cases for VueConverter."""
    
    @pytest.fixture
    def advanced_converter(self):
        """Create VueConverter with advanced options."""
        return VueConverter(
            vue_version=3,
            typescript=True,
            composition_api=True,
            optimize_output=True
        )
    
    def test_vue3_script_setup(self, advanced_converter):
        """Test Vue 3 script setup syntax."""
        setup_manifest = {
            "metadata": {"title": "ScriptSetupComponent"},
            "structure": {
                "component": {
                    "name": "ScriptSetupComponent",
                    "setup_syntax": True,
                    "props": {"message": "string"},
                    "emits": ["update", "change"],
                    "template": {
                        "div": {
                            "children": [
                                {"h1": "{{ message }}"},
                                {"button": {"@click": "$emit('update')", "text": "Update"}}
                            ]
                        }
                    }
                }
            }
        }
        
        result = advanced_converter.convert(setup_manifest)
        
        vue_content = result.content
        assert '<script setup' in vue_content
        assert 'defineProps<' in vue_content or 'defineProps({' in vue_content
        assert 'defineEmits<' in vue_content or 'defineEmits(' in vue_content
    
    def test_pinia_state_management(self, advanced_converter):
        """Test Pinia store integration."""
        pinia_manifest = {
            "metadata": {"title": "PiniaComponent"},
            "structure": {
                "component": {
                    "name": "PiniaComponent",
                    "stores": ["useUserStore", "useCartStore"],
                    "setup": {
                        "stores": {
                            "userStore": "useUserStore()",
                            "cartStore": "useCartStore()"
                        }
                    },
                    "template": {
                        "div": {
                            "children": [
                                {"h1": "User: {{ userStore.name }}"},
                                {"p": "Cart items: {{ cartStore.itemCount }}"}
                            ]
                        }
                    }
                }
            }
        }
        
        result = advanced_converter.convert(pinia_manifest)
        
        vue_content = result.content
        assert 'useUserStore' in vue_content
        assert 'useCartStore' in vue_content
        assert 'userStore.' in vue_content


if __name__ == "__main__":
    pytest.main([__file__])
