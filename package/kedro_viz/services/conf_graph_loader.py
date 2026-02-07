"""`kedro_viz.services.conf_graph_loader` loads graph data from conf/base YAML files."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

logger = logging.getLogger(__name__)


class ConfGraphLoader:
    """Loads graph nodes and edges from conf/base YAML files."""

    def __init__(self, conf_path: Path):
        """Initialize the loader with a path to the conf directory.
        
        Args:
            conf_path: Path to the conf directory (e.g., /path/to/project/conf)
        """
        self.conf_path = conf_path
        self.base_path = conf_path / "base"

    def discover_catalog_files(self) -> List[Path]:
        """Discover catalog YAML files in conf/base.
        
        Returns:
            List of Path objects for catalog files.
        """
        catalog_files = []
        
        # Pattern 1: fields_source_*.yml (preferred)
        catalog_files.extend(self.base_path.glob("fields_source_*.yml"))
        
        # Pattern 2: fields_canonical_*.yml (preferred)
        catalog_files.extend(self.base_path.glob("fields_canonical_*.yml"))
        
        # Pattern 3: catalog_source_*.yml (legacy)
        catalog_files.extend(self.base_path.glob("catalog_source_*.yml"))
        
        # Pattern 4: catalog_canonical_*.yml (legacy)
        catalog_files.extend(self.base_path.glob("catalog_canonical_*.yml"))
        
        # Pattern 5: fields*.yml (catch-all)
        for file in self.base_path.glob("fields*.yml"):
            if file not in catalog_files:
                catalog_files.append(file)
        
        logger.info(f"Discovered {len(catalog_files)} catalog files")
        return catalog_files

    def discover_lineage_files(self) -> List[Path]:
        """Discover lineage YAML files in conf/base/lineage.
        
        Returns:
            List of Path objects for lineage files.
        """
        lineage_dir = self.base_path / "lineage"
        if not lineage_dir.exists():
            logger.warning(f"Lineage directory not found: {lineage_dir}")
            return []
        
        lineage_files = list(lineage_dir.glob("*.yml"))
        logger.info(f"Discovered {len(lineage_files)} lineage files")
        return lineage_files

    def discover_groups_file(self) -> Optional[Path]:
        """Discover groups file in conf/base.
        
        Returns:
            Path to the groups file, or None if not found.
        """
        # Try viz_group.yml first
        groups_file = self.base_path / "viz_group.yml"
        if groups_file.exists():
            logger.info(f"Found groups file: {groups_file}")
            return groups_file
        
        # Try viz_groups.yml as alternative
        groups_file = self.base_path / "viz_groups.yml"
        if groups_file.exists():
            logger.info(f"Found groups file: {groups_file}")
            return groups_file
        
        logger.warning("No groups file found")
        return None

    def load_yaml(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a YAML file and return its contents.
        
        Args:
            file_path: Path to the YAML file.
            
        Returns:
            Dictionary containing the YAML contents, or None if loading failed.
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}")
            return None

    def load_catalog_fields(self) -> List[Dict[str, Any]]:
        """Load all field definitions from catalog files.
        
        Returns:
            List of field dictionaries with metadata.
        """
        all_fields = []
        
        for catalog_file in self.discover_catalog_files():
            data = self.load_yaml(catalog_file)
            if not data:
                continue
            
            fields = data.get("fields", [])
            namespace = data.get("namespace", "")
            
            # Enrich each field with catalog metadata
            for field in fields:
                field["_catalog_namespace"] = namespace
                field["_catalog_file"] = str(catalog_file.name)
                all_fields.append(field)
        
        logger.info(f"Loaded {len(all_fields)} fields from catalog files")
        return all_fields

    def load_lineage_mappings(self) -> List[Dict[str, Any]]:
        """Load all mapping definitions from lineage files.
        
        Returns:
            List of mapping dictionaries.
        """
        all_mappings = []
        
        for lineage_file in self.discover_lineage_files():
            data = self.load_yaml(lineage_file)
            if not data:
                continue
            
            mappings = data.get("mappings", [])
            
            # Enrich each mapping with source file info
            for mapping in mappings:
                mapping["_lineage_file"] = str(lineage_file.name)
                all_mappings.append(mapping)
        
        logger.info(f"Loaded {len(all_mappings)} mappings from lineage files")
        return all_mappings

    def load_group_sets(self) -> List[Dict[str, Any]]:
        """Load group definitions from groups file.
        
        Returns:
            List of group set dictionaries.
        """
        groups_file = self.discover_groups_file()
        if not groups_file:
            return []
        
        data = self.load_yaml(groups_file)
        if not data:
            return []
        
        group_sets = data.get("groupSets", [])
        logger.info(f"Loaded {len(group_sets)} group sets from {groups_file.name}")
        return group_sets
