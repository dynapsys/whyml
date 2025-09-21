"""
WhyML Core Inheritance Resolver - Template inheritance and dependency resolution

Handles complex template inheritance chains, circular dependency detection,
and manifest composition with proper inheritance order.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

import copy
from typing import Any, Dict, List, Optional, Set
from ..exceptions import TemplateInheritanceError, WhyMLError


class InheritanceResolver:
    """Resolves template inheritance and manifest composition."""
    
    def __init__(self):
        """Initialize inheritance resolver."""
        self.inheritance_chain: List[str] = []
        self.visited_templates: Set[str] = set()
        self.resolved_cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_inheritance(self, 
                          manifest: Dict[str, Any], 
                          manifest_id: str,
                          loader_func=None) -> Dict[str, Any]:
        """Resolve template inheritance for a manifest.
        
        Args:
            manifest: Manifest to resolve inheritance for
            manifest_id: Unique identifier for the manifest
            loader_func: Function to load parent manifests (optional)
            
        Returns:
            Resolved manifest with inheritance applied
            
        Raises:
            TemplateInheritanceError: If inheritance resolution fails
        """
        # Check cache first
        if manifest_id in self.resolved_cache:
            return copy.deepcopy(self.resolved_cache[manifest_id])
        
        # Reset state for new resolution
        self.inheritance_chain = []
        self.visited_templates = set()
        
        try:
            resolved = self._resolve_recursive(manifest, manifest_id, loader_func)
            
            # Cache the result
            self.resolved_cache[manifest_id] = copy.deepcopy(resolved)
            
            return resolved
            
        except Exception as e:
            if isinstance(e, TemplateInheritanceError):
                raise
            raise TemplateInheritanceError(
                f"Failed to resolve inheritance for {manifest_id}: {e}",
                template_chain=self.inheritance_chain
            )
    
    def _resolve_recursive(self, 
                          manifest: Dict[str, Any], 
                          manifest_id: str,
                          loader_func=None) -> Dict[str, Any]:
        """Recursively resolve inheritance chain.
        
        Args:
            manifest: Current manifest to resolve
            manifest_id: Unique identifier for current manifest
            loader_func: Function to load parent manifests
            
        Returns:
            Resolved manifest
        """
        # Check for circular inheritance
        if manifest_id in self.visited_templates:
            raise TemplateInheritanceError(
                f"Circular template inheritance detected: {manifest_id}",
                template_chain=self.inheritance_chain + [manifest_id]
            )
        
        # Add to chain and visited set
        self.inheritance_chain.append(manifest_id)
        self.visited_templates.add(manifest_id)
        
        # Check if manifest extends another template
        metadata = manifest.get('metadata', {})
        parent_template = metadata.get('extends')
        
        if not parent_template:
            # No inheritance, return as is
            return copy.deepcopy(manifest)
        
        # Load parent template
        if loader_func:
            try:
                parent_manifest = loader_func(parent_template)
            except Exception as e:
                raise TemplateInheritanceError(
                    f"Failed to load parent template '{parent_template}': {e}",
                    template_chain=self.inheritance_chain
                )
        else:
            raise TemplateInheritanceError(
                f"Cannot load parent template '{parent_template}': no loader function provided",
                template_chain=self.inheritance_chain
            )
        
        # Recursively resolve parent inheritance
        resolved_parent = self._resolve_recursive(parent_manifest, parent_template, loader_func)
        
        # Merge current manifest with resolved parent
        result = self._merge_manifests(resolved_parent, manifest)
        
        return result
    
    def _merge_manifests(self, parent: Dict[str, Any], child: Dict[str, Any]) -> Dict[str, Any]:
        """Merge child manifest with parent manifest.
        
        Args:
            parent: Parent manifest (base)
            child: Child manifest (override)
            
        Returns:
            Merged manifest
        """
        result = copy.deepcopy(parent)
        
        # Merge each section
        for section, content in child.items():
            if section == 'metadata':
                # Special handling for metadata - merge but preserve inheritance info
                result[section] = self._merge_metadata(
                    result.get(section, {}), 
                    content
                )
            elif section == 'template_slots':
                # Template slots override completely
                result[section] = copy.deepcopy(content)
            elif section == 'styles':
                # Merge styles - child overrides parent
                if section not in result:
                    result[section] = {}
                result[section].update(copy.deepcopy(content))
            elif section == 'structure':
                # Structure can be merged or overridden based on slots
                result[section] = self._merge_structure(
                    result.get(section, {}), 
                    content,
                    child.get('template_slots', {})
                )
            elif section == 'imports':
                # Merge imports - combine lists
                result[section] = self._merge_imports(
                    result.get(section, {}), 
                    content
                )
            else:
                # Other sections override completely
                result[section] = copy.deepcopy(content)
        
        return result
    
    def _merge_metadata(self, parent_meta: Dict[str, Any], child_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Merge metadata sections.
        
        Args:
            parent_meta: Parent metadata
            child_meta: Child metadata
            
        Returns:
            Merged metadata
        """
        result = copy.deepcopy(parent_meta)
        result.update(copy.deepcopy(child_meta))
        
        # Remove 'extends' from final result to avoid infinite inheritance
        if 'extends' in result:
            del result['extends']
        
        return result
    
    def _merge_structure(self, 
                        parent_structure: Dict[str, Any], 
                        child_structure: Dict[str, Any],
                        template_slots: Dict[str, Any]) -> Dict[str, Any]:
        """Merge structure sections with template slot support.
        
        Args:
            parent_structure: Parent structure
            child_structure: Child structure
            template_slots: Template slots for replacement
            
        Returns:
            Merged structure
        """
        if not template_slots:
            # No slots, child structure overrides parent completely
            return copy.deepcopy(child_structure)
        
        # Start with parent structure
        result = copy.deepcopy(parent_structure)
        
        # Replace template slots with child content
        result = self._replace_template_slots(result, template_slots)
        
        # Merge any additional child structure
        if child_structure:
            result = self._deep_merge_dict(result, child_structure)
        
        return result
    
    def _replace_template_slots(self, structure: Any, slots: Dict[str, Any]) -> Any:
        """Replace template slots in structure.
        
        Args:
            structure: Structure to process
            slots: Template slots to replace
            
        Returns:
            Structure with slots replaced
        """
        if isinstance(structure, dict):
            result = {}
            for key, value in structure.items():
                if key.startswith('{{slot:') and key.endswith('}}'):
                    # Extract slot name
                    slot_name = key[7:-2].strip()  # Remove {{slot: and }}
                    if slot_name in slots:
                        result.update(slots[slot_name])
                    # If slot not found, skip it (remove from structure)
                else:
                    result[key] = self._replace_template_slots(value, slots)
            return result
        elif isinstance(structure, list):
            return [self._replace_template_slots(item, slots) for item in structure]
        else:
            return structure
    
    def _merge_imports(self, parent_imports: Dict[str, Any], child_imports: Dict[str, Any]) -> Dict[str, Any]:
        """Merge imports sections.
        
        Args:
            parent_imports: Parent imports
            child_imports: Child imports
            
        Returns:
            Merged imports
        """
        result = copy.deepcopy(parent_imports)
        
        for import_type, imports_list in child_imports.items():
            if import_type not in result:
                result[import_type] = []
            
            # Combine lists and remove duplicates
            combined = result[import_type] + imports_list
            result[import_type] = list(dict.fromkeys(combined))  # Remove duplicates, preserve order
        
        return result
    
    def _deep_merge_dict(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            overlay: Overlay dictionary
            
        Returns:
            Merged dictionary
        """
        result = copy.deepcopy(base)
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge_dict(result[key], value)
            else:
                result[key] = copy.deepcopy(value)
        
        return result
    
    def detect_circular_inheritance(self, manifests: Dict[str, Dict[str, Any]]) -> List[List[str]]:
        """Detect circular inheritance in a collection of manifests.
        
        Args:
            manifests: Dictionary of {manifest_id: manifest} pairs
            
        Returns:
            List of circular inheritance chains
        """
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(manifest_id: str, path: List[str]) -> None:
            if manifest_id in rec_stack:
                # Found a cycle
                try:
                    cycle_start = path.index(manifest_id)
                    cycle = path[cycle_start:] + [manifest_id]
                    if cycle not in cycles:
                        cycles.append(cycle)
                except ValueError:
                    cycles.append(path + [manifest_id])
                return
            
            if manifest_id in visited or manifest_id not in manifests:
                return
            
            visited.add(manifest_id)
            rec_stack.add(manifest_id)
            path.append(manifest_id)
            
            # Check if this manifest extends another
            metadata = manifests[manifest_id].get('metadata', {})
            parent = metadata.get('extends')
            
            if parent:
                dfs(parent, path.copy())
            
            rec_stack.remove(manifest_id)
        
        for manifest_id in manifests:
            if manifest_id not in visited:
                dfs(manifest_id, [])
        
        return cycles
    
    def get_inheritance_chain(self, 
                             manifest: Dict[str, Any], 
                             manifest_id: str,
                             loader_func=None) -> List[str]:
        """Get the full inheritance chain for a manifest.
        
        Args:
            manifest: Manifest to analyze
            manifest_id: Manifest identifier
            loader_func: Function to load parent manifests
            
        Returns:
            List of manifest IDs in inheritance order (child to parent)
        """
        chain = [manifest_id]
        current = manifest
        
        while True:
            metadata = current.get('metadata', {})
            parent = metadata.get('extends')
            
            if not parent:
                break
            
            if parent in chain:
                raise TemplateInheritanceError(
                    f"Circular inheritance detected in chain: {' -> '.join(chain + [parent])}",
                    template_chain=chain
                )
            
            chain.append(parent)
            
            if loader_func:
                try:
                    current = loader_func(parent)
                except Exception as e:
                    # Can't load parent, break chain
                    break
            else:
                break
        
        return chain
    
    def clear_cache(self) -> None:
        """Clear the resolved manifest cache."""
        self.resolved_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_manifests': len(self.resolved_cache),
            'cache_keys': list(self.resolved_cache.keys())
        }
