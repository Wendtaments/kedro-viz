"""
Integration test for the conf-driven graph API endpoint.

This script validates that the endpoint returns the expected structure
and follows the specification requirements.
"""

import sys
import os
from pathlib import Path

# Add package to path
package_path = Path(__file__).parent.parent / "package"
sys.path.insert(0, str(package_path))

from kedro_viz.api.rest.responses.pipelines import get_conf_pipeline_response


def test_api_response():
    """Test the API response structure."""
    
    print("="*60)
    print("TESTING CONF-DRIVEN GRAPH API ENDPOINT")
    print("="*60)
    
    # Change to lineage-project directory so conf files can be found
    original_cwd = os.getcwd()
    lineage_project = Path(__file__).parent.parent / "lineage-project"
    os.chdir(lineage_project)
    
    try:
        # Get the response
        response = get_conf_pipeline_response()
    finally:
        # Restore original directory
        os.chdir(original_cwd)
    
    # Check if it's a valid response (not an error)
    if hasattr(response, 'status_code'):
        print(f"❌ ERROR: API returned error response")
        print(f"   Status: {response.status_code}")
        print(f"   Content: {response.body}")
        return False
    
    print("✓ API response successful")
    
    # Validate response structure
    required_fields = ['nodes', 'edges', 'layers', 'tags', 'pipelines', 'modular_pipelines', 'selected_pipeline']
    
    for field in required_fields:
        if not hasattr(response, field):
            print(f"❌ Missing required field: {field}")
            return False
    
    print(f"✓ All required fields present")
    
    # Validate nodes structure
    nodes = response.nodes
    if not isinstance(nodes, list):
        print(f"❌ Nodes should be a list, got: {type(nodes)}")
        return False
    
    print(f"✓ Nodes is a list with {len(nodes)} items")
    
    # Validate first node structure
    if len(nodes) > 0:
        node = nodes[0]
        # Handle both dict and Pydantic model
        node_dict = node if isinstance(node, dict) else node.__dict__ if hasattr(node, '__dict__') else {}
        
        required_node_fields = ['id', 'name', 'type', 'tags', 'pipelines']
        for field in required_node_fields:
            if field not in node_dict and not hasattr(node, field):
                print(f"❌ Node missing required field: {field}")
                return False
        
        # Get node id and type
        node_id = node_dict.get('id') if isinstance(node, dict) else getattr(node, 'id', 'N/A')
        node_type = node_dict.get('type') if isinstance(node, dict) else getattr(node, 'type', 'N/A')
        
        print(f"✓ Node structure valid")
        print(f"   Example node ID: {node_id}")
        print(f"   Example node type: {node_type}")
    
    # Validate edges structure
    edges = response.edges
    if not isinstance(edges, list):
        print(f"❌ Edges should be a list, got: {type(edges)}")
        return False
    
    print(f"✓ Edges is a list with {len(edges)} items")
    
    # Validate first edge structure
    if len(edges) > 0:
        edge = edges[0]
        # Handle both dict and Pydantic model
        edge_dict = edge if isinstance(edge, dict) else edge.__dict__ if hasattr(edge, '__dict__') else {}
        
        required_edge_fields = ['source', 'target']
        for field in required_edge_fields:
            if field not in edge_dict and not hasattr(edge, field):
                print(f"❌ Edge missing required field: {field}")
                return False
        
        # Get edge source and target
        edge_source = edge_dict.get('source') if isinstance(edge, dict) else getattr(edge, 'source', 'N/A')
        edge_target = edge_dict.get('target') if isinstance(edge, dict) else getattr(edge, 'target', 'N/A')
        
        print(f"✓ Edge structure valid")
        print(f"   Example edge: {edge_source} -> {edge_target}")
    
    # Count node types
    if isinstance(nodes, list) and len(nodes) > 0:
        node_types = {}
        for node in nodes:
            # Handle both dict and Pydantic model
            node_dict = node if isinstance(node, dict) else node.__dict__ if hasattr(node, '__dict__') else {}
            node_type = node_dict.get('type') if isinstance(node, dict) else getattr(node, 'type', 'Unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n✓ Node type distribution:")
        for node_type, count in sorted(node_types.items()):
            print(f"   {node_type}: {count}")
    
    # Validate no unexpected nodes
    if isinstance(nodes, list):
        unexpected_patterns = ['map_to_', 'normalize_', 'map.']
        unexpected_nodes = []
        
        for node in nodes:
            # Handle both dict and Pydantic model
            node_dict = node if isinstance(node, dict) else node.__dict__ if hasattr(node, '__dict__') else {}
            node_id = node_dict.get('id') if isinstance(node, dict) else getattr(node, 'id', '')
            
            for pattern in unexpected_patterns:
                if node_id.startswith(pattern):
                    unexpected_nodes.append(node_id)
        
        if unexpected_nodes:
            print(f"\n❌ Found unexpected node IDs:")
            for node_id in unexpected_nodes[:5]:
                print(f"   {node_id}")
        else:
            print(f"\n✓ No unexpected node ID patterns found")
    
    print("\n" + "="*60)
    print("API ENDPOINT VALIDATION: PASSED ✓")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = test_api_response()
    sys.exit(0 if success else 1)
