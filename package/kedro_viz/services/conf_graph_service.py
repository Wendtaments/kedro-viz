"""`kedro_viz.services.conf_graph_service` provides high-level API for conf-driven graphs."""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from kedro_viz.services.conf_graph_loader import ConfGraphLoader
from kedro_viz.services.conf_graph_builder import ConfGraphBuilder

logger = logging.getLogger(__name__)


class ConfGraphService:
    """Service for building graphs from conf/base YAML files."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize the service.
        
        Args:
            project_path: Path to the Kedro project root. If None, will attempt
                         to discover from current working directory.
        """
        self.project_path = project_path
        if self.project_path:
            self.conf_path = self.project_path / "conf"
        else:
            self.conf_path = None

    def get_graph(self) -> Dict[str, Any]:
        """Build and return the conf-driven graph.
        
        Returns:
            Dictionary with 'nodes' and 'edges' lists.
        """
        if not self.conf_path or not self.conf_path.exists():
            logger.error(f"Conf path not found: {self.conf_path}")
            return {"nodes": [], "edges": []}
        
        try:
            # Load data from conf files
            loader = ConfGraphLoader(self.conf_path)
            fields = loader.load_catalog_fields()
            mappings = loader.load_lineage_mappings()
            group_sets = loader.load_group_sets()
            
            # Build graph
            builder = ConfGraphBuilder()
            graph = builder.build_graph(fields, mappings, group_sets)
            
            logger.info(
                f"Built conf-driven graph with {len(graph['nodes'])} nodes "
                f"and {len(graph['edges'])} edges"
            )
            
            return graph
            
        except Exception as e:
            logger.exception(f"Failed to build conf-driven graph: {e}")
            return {"nodes": [], "edges": []}
