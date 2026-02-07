"""
Simple example demonstrating conf-driven graph API usage.

This script shows how to programmatically use the ConfGraphService
to build a graph from conf/base YAML files.
"""

from pathlib import Path
import json
import sys

# Add package to path
package_path = Path(__file__).parent.parent / "package"
sys.path.insert(0, str(package_path))

from kedro_viz.services.conf_graph_service import ConfGraphService


def example_usage():
    """Example: Load graph from lineage-project."""
    
    # Path to your Kedro project
    project_path = Path(__file__).parent.parent / "lineage-project"
    
    # Create service and load graph
    service = ConfGraphService(project_path)
    graph = service.get_graph()
    
    # Access nodes and edges
    print(f"Loaded {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    
    # Find specific nodes
    source_fields = [n for n in graph['nodes'] if n['viz']['nodeType'] == 'SourceField']
    canonical_fields = [n for n in graph['nodes'] if n['viz']['nodeType'] == 'CanonicalField']
    transform_nodes = [n for n in graph['nodes'] if 'Transform' in n['viz']['nodeType']]
    group_nodes = [n for n in graph['nodes'] if n['viz']['nodeType'] == 'Group']
    
    print(f"\nNode breakdown:")
    print(f"  Source fields: {len(source_fields)}")
    print(f"  Canonical fields: {len(canonical_fields)}")
    print(f"  Transform nodes: {len(transform_nodes)}")
    print(f"  Group nodes: {len(group_nodes)}")
    
    # Example: Find a specific field
    field_id = "source.creditTransfer.instructedAmount"
    field = next((n for n in graph['nodes'] if n['id'] == field_id), None)
    
    if field:
        print(f"\nExample field: {field_id}")
        print(f"  Name: {field['name']}")
        print(f"  Type: {field['viz']['nodeType']}")
        print(f"  Metadata keys: {list(field['viz']['meta'].keys())}")
    
    # Example: Trace lineage
    if graph['edges']:
        print(f"\nExample lineage:")
        for edge in graph['edges']:
            print(f"  {edge['source']}")
            print(f"    → [{edge.get('edgeType', 'N/A')}] →")
            print(f"  {edge['target']}")
            if edge.get('metadata'):
                print(f"    Metadata: {edge['metadata']}")
    
    # Export to JSON (for inspection)
    output_file = Path(__file__).parent / "example_graph_output.json"
    with open(output_file, 'w') as f:
        json.dump(graph, f, indent=2)
    
    print(f"\nFull graph exported to: {output_file}")


if __name__ == "__main__":
    example_usage()
