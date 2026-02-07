"""Quick test to verify nodes have pipelines field."""
import sys
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "package"))

from kedro_viz.services.conf_graph_builder import ConfGraphNode

# Create a test node
node = ConfGraphNode(
    node_id="test.node",
    name="Test Node",
    node_type="sourcefield"
)

# Check pipelines
print(f"Node pipelines: {node.pipelines}")
print(f"Node to_dict: {node.to_dict()}")
print(f"Pipelines in dict: {node.to_dict()['pipelines']}")
