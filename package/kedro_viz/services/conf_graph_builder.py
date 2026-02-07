"""`kedro_viz.services.conf_graph_builder` builds graph nodes and edges from conf data."""

import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ConfGraphNode:
    """Represents a node in the conf-driven graph."""

    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str,
        viz_meta: Optional[Dict[str, Any]] = None,
        tags: Optional[Set[str]] = None,
    ):
        self.id = node_id
        self.name = name
        self.viz = {
            "nodeType": node_type,
            "meta": viz_meta or {},
        }
        self.tags = tags or set()
        self.pipelines = {"conf"}  # All conf-driven nodes belong to 'conf' pipeline

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary format for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.viz["nodeType"].lower(),  # Normalize to lowercase for consistency
            "tags": sorted(list(self.tags)),
            "pipelines": sorted(list(self.pipelines)),
            "modular_pipelines": [],
            "viz": self.viz,
        }


class ConfGraphEdge:
    """Represents an edge in the conf-driven graph."""

    def __init__(
        self,
        source: str,
        target: str,
        edge_type: str = "DERIVES_FROM",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.source = source
        self.target = target
        self.edge_type = edge_type
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary format for API response."""
        result = {
            "source": self.source,
            "target": self.target,
        }
        if self.edge_type:
            result["edgeType"] = self.edge_type
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class ConfGraphBuilder:
    """Builds a graph from conf-based field, lineage, and group definitions."""

    def __init__(self):
        self.nodes: Dict[str, ConfGraphNode] = {}
        self.edges: List[ConfGraphEdge] = []

    def build_graph(
        self,
        fields: List[Dict[str, Any]],
        mappings: List[Dict[str, Any]],
        group_sets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build the complete graph from loaded conf data.
        
        Args:
            fields: List of field definitions from catalogs.
            mappings: List of mapping definitions from lineage files.
            group_sets: List of group set definitions.
            
        Returns:
            Dictionary with 'nodes' and 'edges' lists.
        """
        # Step 1: Create field nodes
        self._create_field_nodes(fields)
        
        # Step 2: Process lineage mappings
        self._process_mappings(mappings)
        
        # Step 3: Create group nodes
        self._create_group_nodes(group_sets)
        
        # Convert to response format
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    def _create_field_nodes(self, fields: List[Dict[str, Any]]):
        """Create nodes for each field in the catalog.
        
        Args:
            fields: List of field definitions.
        """
        for field in fields:
            field_id = field.get("id")
            if not field_id:
                logger.warning(f"Field missing 'id', skipping: {field}")
                continue
            
            # Determine node name
            field_name = field.get("name")
            if not field_name:
                # Derive from id (last segment)
                field_name = field_id.split(".")[-1]
            
            # Determine node type based on id prefix
            node_type = self._determine_node_type(field_id)
            
            # Create node with full field metadata
            node = ConfGraphNode(
                node_id=field_id,
                name=field_name,
                node_type=node_type,
                viz_meta=field,  # Store entire field object in meta
            )
            
            self.nodes[field_id] = node
            
        logger.info(f"Created {len(self.nodes)} field nodes")

    def _determine_node_type(self, field_id: str) -> str:
        """Determine node type based on field ID prefix.
        
        Args:
            field_id: The field identifier.
            
        Returns:
            Node type string.
        """
        if field_id.startswith("source."):
            return "SourceField"
        elif field_id.startswith("canonical."):
            return "CanonicalField"
        else:
            return "Field"

    def _process_mappings(self, mappings: List[Dict[str, Any]]):
        """Process lineage mappings to create transformation nodes and edges.
        
        Args:
            mappings: List of mapping definitions.
        """
        for mapping in mappings:
            mapping_id = mapping.get("id")
            from_id = mapping.get("from")
            to_id = mapping.get("to")
            transform = mapping.get("transform")
            explicit_edges = mapping.get("edges")
            mapping_metadata = mapping.get("metadata", {})
            
            if not from_id or not to_id:
                logger.warning(f"Mapping {mapping_id} missing 'from' or 'to', skipping")
                continue
            
            # Validate referenced nodes exist (create placeholders if not)
            self._ensure_node_exists(from_id)
            self._ensure_node_exists(to_id)
            
            # If transform is defined, create the transform node first
            # (regardless of whether explicit edges are also defined)
            if transform:
                transform_id = transform.get("id")
                if transform_id:
                    # Create transform node
                    node_type = transform.get("nodeType", "Transformation")
                    transform_node = ConfGraphNode(
                        node_id=transform_id,
                        name=transform_id.split(".")[-1],  # Use last segment as name
                        node_type=node_type,
                        viz_meta=transform,  # Store transform metadata
                    )
                    self.nodes[transform_id] = transform_node
            
            # Case 1: Explicit edges defined
            if explicit_edges:
                for edge_def in explicit_edges:
                    edge_from = edge_def.get("from")
                    edge_to = edge_def.get("to")
                    edge_type = edge_def.get("type", "DERIVES_FROM")
                    edge_metadata = edge_def.get("metadata", {})
                    
                    # Merge mapping metadata with edge metadata (edge wins)
                    merged_metadata = {**mapping_metadata, **edge_metadata}
                    
                    # Ensure referenced nodes exist
                    self._ensure_node_exists(edge_from)
                    self._ensure_node_exists(edge_to)
                    
                    self.edges.append(
                        ConfGraphEdge(
                            source=edge_from,
                            target=edge_to,
                            edge_type=edge_type,
                            metadata=merged_metadata,
                        )
                    )
            
            # Case 2: Transform node defined (without explicit edges)
            elif transform:
                transform_id = transform.get("id")
                if not transform_id:
                    logger.warning(f"Transform in mapping {mapping_id} missing 'id', skipping")
                    continue
                
                # Create two edges: from -> transform, transform -> to
                self.edges.append(
                    ConfGraphEdge(
                        source=from_id,
                        target=transform_id,
                        edge_type="DERIVES_FROM",
                        metadata=mapping_metadata,
                    )
                )
                self.edges.append(
                    ConfGraphEdge(
                        source=transform_id,
                        target=to_id,
                        edge_type="DERIVES_FROM",
                        metadata=mapping_metadata,
                    )
                )
            
            # Case 3: Simple direct mapping
            else:
                self.edges.append(
                    ConfGraphEdge(
                        source=from_id,
                        target=to_id,
                        edge_type="DERIVES_FROM",
                        metadata=mapping_metadata,
                    )
                )
        
        logger.info(f"Processed {len(mappings)} mappings, created {len(self.edges)} edges")

    def _ensure_node_exists(self, node_id: str):
        """Ensure a node exists, creating a placeholder if necessary.
        
        Args:
            node_id: The node identifier.
        """
        if node_id not in self.nodes:
            logger.warning(f"Node {node_id} not found in catalogs, creating placeholder")
            placeholder = ConfGraphNode(
                node_id=node_id,
                name=node_id.split(".")[-1],
                node_type="Unknown",
                viz_meta={"missing": True},
            )
            self.nodes[node_id] = placeholder

    def _create_group_nodes(self, group_sets: List[Dict[str, Any]]):
        """Create group nodes from group set definitions.
        
        Args:
            group_sets: List of group set definitions.
        """
        for group_set in group_sets:
            group_set_id = group_set.get("id")
            group_set_label = group_set.get("label", "")
            group_set_kind = group_set.get("kind")
            namespace_prefixes = group_set.get("namespacePrefixes", [])
            groups = group_set.get("groups", [])
            
            for group in groups:
                group_id = group.get("id")
                if not group_id:
                    logger.warning(f"Group missing 'id' in group set {group_set_id}, skipping")
                    continue
                
                group_label = group.get("label", group_id)
                members = group.get("members", [])
                includes = group.get("includes", [])
                
                # Validate member IDs exist
                for member_id in members:
                    if member_id not in self.nodes:
                        logger.warning(f"Group {group_id} references non-existent member {member_id}")
                
                # Create group node
                group_meta = {
                    "groupSetId": group_set_id,
                    "groupSetLabel": group_set_label,
                    "kind": group_set_kind,
                    "namespacePrefixes": namespace_prefixes,
                    "members": members,
                    "includes": includes,
                }
                
                group_node = ConfGraphNode(
                    node_id=group_id,
                    name=group_label,
                    node_type="Group",
                    viz_meta=group_meta,
                )
                
                self.nodes[group_id] = group_node
        
        logger.info(f"Created group nodes")
