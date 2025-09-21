"""
WhyML Core Dependency Resolver - Dependency resolution and circular dependency detection

Handles complex dependency graphs with topological sorting and cycle detection.

Copyright 2025 Tom Sapletta
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, List, Set, Optional
from ..exceptions import WhyMLError


class DependencyError(WhyMLError):
    """Raised when dependency resolution fails."""
    
    def __init__(self, message: str, circular_dependencies: Optional[List[str]] = None):
        """Initialize dependency error.
        
        Args:
            message: Human-readable error message
            circular_dependencies: List of circular dependency chains
        """
        details = {}
        if circular_dependencies:
            details['circular_dependencies'] = circular_dependencies
        super().__init__(message, details)


class DependencyResolver:
    """Handles dependency resolution and circular dependency detection."""
    
    def __init__(self):
        """Initialize dependency resolver."""
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.resolution_order: List[str] = []
        self._resolved = False
    
    def add_dependency(self, module: str, depends_on: str) -> None:
        """Add a dependency relationship.
        
        Args:
            module: Module that has a dependency
            depends_on: Module that is depended upon
        """
        if module not in self.dependency_graph:
            self.dependency_graph[module] = set()
        self.dependency_graph[module].add(depends_on)
        self._resolved = False
    
    def add_dependencies(self, module: str, depends_on_list: List[str]) -> None:
        """Add multiple dependencies for a module.
        
        Args:
            module: Module that has dependencies
            depends_on_list: List of modules that are depended upon
        """
        if module not in self.dependency_graph:
            self.dependency_graph[module] = set()
        
        for dependency in depends_on_list:
            self.dependency_graph[module].add(dependency)
        
        self._resolved = False
    
    def remove_dependency(self, module: str, depends_on: Optional[str] = None) -> None:
        """Remove a dependency or all dependencies for a module.
        
        Args:
            module: Module to remove dependencies from
            depends_on: Specific dependency to remove, or None to remove all
        """
        if module in self.dependency_graph:
            if depends_on is None:
                del self.dependency_graph[module]
            else:
                self.dependency_graph[module].discard(depends_on)
                if not self.dependency_graph[module]:
                    del self.dependency_graph[module]
        
        self._resolved = False
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph.
        
        Returns:
            List of circular dependency chains
        """
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                try:
                    cycle_start = path.index(node)
                    cycle = path[cycle_start:] + [node]
                    if cycle not in cycles:
                        cycles.append(cycle)
                except ValueError:
                    # Node not in path, add full path as cycle
                    cycles.append(path + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def get_resolution_order(self) -> List[str]:
        """Get the topological order for dependency resolution.
        
        Returns:
            List of modules in dependency resolution order
            
        Raises:
            DependencyError: If circular dependencies are detected
        """
        if self._resolved and self.resolution_order:
            return self.resolution_order.copy()
        
        # Check for circular dependencies first
        cycles = self.detect_circular_dependencies()
        if cycles:
            cycle_strings = [" -> ".join(cycle) for cycle in cycles]
            raise DependencyError(
                "Circular dependencies detected",
                circular_dependencies=cycle_strings
            )
        
        # Get all nodes (modules)
        all_nodes = set(self.dependency_graph.keys())
        for deps in self.dependency_graph.values():
            all_nodes.update(deps)
        
        # Calculate in-degrees
        in_degree = {node: 0 for node in all_nodes}
        for node in self.dependency_graph:
            for dep in self.dependency_graph[node]:
                in_degree[dep] += 1
        
        # Kahn's algorithm for topological sorting
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Verify all nodes were processed (no cycles)
        if len(result) != len(all_nodes):
            cycles = self.detect_circular_dependencies()
            cycle_strings = [" -> ".join(cycle) for cycle in cycles]
            raise DependencyError(
                "Circular dependencies detected during resolution",
                circular_dependencies=cycle_strings
            )
        
        self.resolution_order = result
        self._resolved = True
        return result.copy()
    
    def get_dependencies(self, module: str) -> Set[str]:
        """Get direct dependencies of a module.
        
        Args:
            module: Module to get dependencies for
            
        Returns:
            Set of direct dependencies
        """
        return self.dependency_graph.get(module, set()).copy()
    
    def get_transitive_dependencies(self, module: str) -> Set[str]:
        """Get all transitive dependencies of a module.
        
        Args:
            module: Module to get transitive dependencies for
            
        Returns:
            Set of all transitive dependencies
        """
        visited = set()
        
        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            
            for dep in self.dependency_graph.get(node, set()):
                dfs(dep)
        
        # Get dependencies of the module
        for dep in self.dependency_graph.get(module, set()):
            dfs(dep)
        
        # Remove the module itself if it was added
        visited.discard(module)
        return visited
    
    def has_dependency(self, module: str, dependency: str) -> bool:
        """Check if a module has a specific dependency (direct or transitive).
        
        Args:
            module: Module to check
            dependency: Dependency to look for
            
        Returns:
            True if dependency exists (direct or transitive)
        """
        if module not in self.dependency_graph:
            return False
        
        # Check direct dependency
        if dependency in self.dependency_graph[module]:
            return True
        
        # Check transitive dependencies
        return dependency in self.get_transitive_dependencies(module)
    
    def get_dependents(self, module: str) -> Set[str]:
        """Get modules that depend on the given module.
        
        Args:
            module: Module to find dependents for
            
        Returns:
            Set of modules that depend on the given module
        """
        dependents = set()
        for node, deps in self.dependency_graph.items():
            if module in deps:
                dependents.add(node)
        return dependents
    
    def clear(self) -> None:
        """Clear all dependencies."""
        self.dependency_graph.clear()
        self.resolution_order.clear()
        self._resolved = False
    
    def get_stats(self) -> Dict[str, int]:
        """Get dependency graph statistics.
        
        Returns:
            Dictionary with graph statistics
        """
        total_nodes = len(set(self.dependency_graph.keys()) | 
                         set().union(*self.dependency_graph.values()) if self.dependency_graph else set())
        total_edges = sum(len(deps) for deps in self.dependency_graph.values())
        
        return {
            'total_modules': total_nodes,
            'total_dependencies': total_edges,
            'modules_with_dependencies': len(self.dependency_graph),
            'resolved': self._resolved
        }
    
    def __len__(self) -> int:
        """Get number of modules with dependencies."""
        return len(self.dependency_graph)
    
    def __contains__(self, module: str) -> bool:
        """Check if module is in the dependency graph."""
        return module in self.dependency_graph
