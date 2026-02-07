"""Test the conf-driven graph loader and builder with lineage-project."""

import sys
from pathlib import Path

# Add package to path
package_path = Path(__file__).parent.parent / "package"
sys.path.insert(0, str(package_path))

from kedro_viz.services.conf_graph_service import ConfGraphService

def test_lineage_project():
    """Test loading the lineage-project conf files."""
    
    # Path to lineage-project
    lineage_project_path = Path(__file__).parent.parent / "lineage-project"
    
    print(f"Testing conf-driven graph with project: {lineage_project_path}")
    print(f"Project exists: {lineage_project_path.exists()}")
    
    # Create service and load graph
    service = ConfGraphService(lineage_project_path)
    graph = service.get_graph()
    
    # Display results
    print(f"\n{'='*60}")
    print(f"GRAPH SUMMARY")
    print(f"{'='*60}")
    print(f"Total nodes: {len(graph['nodes'])}")
    print(f"Total edges: {len(graph['edges'])}")
    
    # Count nodes by type
    node_types = {}
    for node in graph['nodes']:
        node_type = node.get('viz', {}).get('nodeType', 'Unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print(f"\nNode types:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")
    
    # Show some example nodes
    print(f"\n{'='*60}")
    print(f"EXAMPLE NODES (first 5)")
    print(f"{'='*60}")
    for i, node in enumerate(graph['nodes'][:5]):
        print(f"\n{i+1}. {node['id']}")
        print(f"   Name: {node['name']}")
        print(f"   Type: {node['type']}")
        print(f"   NodeType: {node['viz']['nodeType']}")
    
    # Show edges
    print(f"\n{'='*60}")
    print(f"EDGES (first 10)")
    print(f"{'='*60}")
    for i, edge in enumerate(graph['edges'][:10]):
        source = edge['source']
        target = edge['target']
        edge_type = edge.get('edgeType', 'N/A')
        print(f"{i+1}. {source} -> {target} [{edge_type}]")
    
    # Validation checks
    print(f"\n{'='*60}")
    print(f"VALIDATION CHECKS")
    print(f"{'='*60}")
    
    # Check for unexpected node names
    unexpected_nodes = []
    for node in graph['nodes']:
        node_id = node['id']
        if node_id.startswith('map_to_') or node_id.startswith('normalize_'):
            unexpected_nodes.append(node_id)
    
    if unexpected_nodes:
        print(f"❌ FAIL: Found unexpected nodes:")
        for node_id in unexpected_nodes:
            print(f"   - {node_id}")
    else:
        print(f"✓ PASS: No unexpected 'map_to_' or 'normalize_' nodes found")
    
    # Check for transform nodes
    transform_nodes = [n for n in graph['nodes'] if 'xform' in n['id'].lower()]
    print(f"✓ Transform nodes found: {len(transform_nodes)}")
    for node in transform_nodes:
        print(f"   - {node['id']} ({node['viz']['nodeType']})")
    
    # Check for group nodes
    group_nodes = [n for n in graph['nodes'] if n['viz']['nodeType'] == 'Group']
    print(f"✓ Group nodes found: {len(group_nodes)}")
    for node in group_nodes[:5]:  # Show first 5
        print(f"   - {node['id']}: {node['name']}")
    
    # Check edge connectivity
    node_ids = {n['id'] for n in graph['nodes']}
    invalid_edges = []
    for edge in graph['edges']:
        if edge['source'] not in node_ids:
            invalid_edges.append(f"Source missing: {edge['source']}")
        if edge['target'] not in node_ids:
            invalid_edges.append(f"Target missing: {edge['target']}")
    
    if invalid_edges:
        print(f"❌ FAIL: Found edges referencing non-existent nodes:")
        for msg in invalid_edges[:10]:  # Show first 10
            print(f"   - {msg}")
    else:
        print(f"✓ PASS: All edges reference valid nodes")
    
    print(f"\n{'='*60}")
    print(f"TEST COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_lineage_project()
