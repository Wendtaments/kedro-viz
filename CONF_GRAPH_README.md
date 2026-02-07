# Conf-Driven Graph Provider

## Overview

The conf-driven graph mode allows kedro-viz to build visualization graphs purely from `conf/base` YAML files (catalog + lineage + groups), without relying on Kedro pipelines.

## API Endpoint

### Query Parameter Approach (Implemented)

```
GET /api/main?source=conf
```

- `source=conf`: Returns graph built from conf/base YAML files
- Default (no parameter): Returns standard Kedro pipeline graph

## File Structure

The conf-driven graph provider expects the following file structure in your project:

```
project/
  conf/
    base/
      catalog_source_*.yml           # Source field catalogs
      catalog_canonical_*.yml        # Canonical field catalogs
      catalog*.yml                   # Other catalog files (optional)
      lineage/
        *.yml                        # Lineage mapping files
      viz_group.yml                  # Group definitions (or viz_groups.yml)
```

## YAML Schemas

### 1. Catalog Files

Catalog files define field nodes (datasets/columns):

```yaml
version: 1
namespace: source.creditTransfer  # Optional namespace prefix
fields:
  - id: source.creditTransfer.id  # Unique identifier (REQUIRED)
    name: id                       # Display name (optional; derived from id if missing)
    alias: transaction_id          # Optional alias
    displayName: Transaction ID    # Optional display name
    # ... any other metadata (avroPath, sqlColumn, iso20022, etc.)
```

**Node Creation Rules:**
- One node per `fields[]` entry
- `node.id` = `field.id`
- `node.name` = `field.name` OR last segment of `field.id`
- `node.viz.nodeType` determined by id prefix:
  - `source.*` → "SourceField"
  - `canonical.*` → "CanonicalField"
  - Otherwise → "Field"
- Full field object stored in `node.viz.meta`

### 2. Lineage Files

Lineage files define transformations and edges:

```yaml
version: 1
mappings:
  - id: map.source_to_canonical         # Mapping identifier (NOT a node)
    from: source.field.a                # Source node id
    to: canonical.field.b               # Target node id
    
    # Option 1: Define a transformation node
    transform:
      id: xform.normalize.field_a       # Transform node id (REQUIRED)
      nodeType: TransformationNormalize # Node type (REQUIRED)
      domain: transactions              # Optional metadata
      ruleId: norm.v1                   # Optional metadata
      logicRef: sql/normalize.sql       # Optional metadata
    
    # Option 2: Explicit edges (takes precedence)
    edges:
      - type: DERIVES_FROM              # Edge type
        from: source.field.a            # Source node
        to: xform.normalize.field_a     # Target node
        metadata:                       # Optional edge metadata
          confidence: high
      - type: DERIVES_FROM
        from: xform.normalize.field_a
        to: canonical.field.b
    
    # Mapping-level metadata (applied to all edges)
    metadata:
      lifecycle: Booking
      confidence: final
      owner: payments
```

**Edge Inference Rules:**

1. **If `edges` exists:** Use exactly those edges (no inference)
2. **Else if `transform` exists:** Infer two edges:
   - `from` → `transform.id`
   - `transform.id` → `to`
3. **Else:** Infer one edge:
   - `from` → `to`

**Transform Node Creation:**
- If `transform.id` exists, create exactly one node
- `node.id` = `transform.id`
- `node.viz.nodeType` = `transform.nodeType`
- Transform metadata stored in `node.viz.meta`

**CRITICAL: Preventing Unexpected Nodes**
- `mappings[].id` is NOT materialized as a node
- `transform.nodeType` is NOT materialized as a separate node
- Only nodes explicitly referenced by id are created

### 3. Groups File

Groups file defines collapsible groupings:

```yaml
version: 1
groupSets:
  - id: groups.source.creditTransfer
    label: "Source: Credit Transfer"
    kind: source                          # "source" | "canonical" | other
    namespacePrefixes:
      - source.creditTransfer.
    groups:
      - id: group.source.creditor         # Group node id (use "group." prefix)
        label: "Creditor Information"     # Display label
        members:                          # Field node ids in this group
          - source.creditTransfer.creditor_name
          - source.creditTransfer.creditor_account
        includes:                         # Nested group ids (optional)
          - group.source.creditor_address
```

**Group Node Creation:**
- One node per `groups[]` entry
- `node.id` = `group.id` (should use "group." prefix to avoid collisions)
- `node.name` = `group.label`
- `node.viz.nodeType` = "Group"
- Members and includes stored in `node.viz.meta`

## Implementation

### Components

1. **ConfGraphLoader** (`kedro_viz/services/conf_graph_loader.py`)
   - Discovers and loads YAML files from conf/base
   - Parses catalogs, lineage, and groups

2. **ConfGraphBuilder** (`kedro_viz/services/conf_graph_builder.py`)
   - Builds graph nodes and edges from loaded data
   - Handles node type inference and validation
   - Creates placeholder nodes for missing references

3. **ConfGraphService** (`kedro_viz/services/conf_graph_service.py`)
   - High-level API combining loader and builder
   - Error handling and logging

4. **API Integration** (`kedro_viz/api/rest/`)
   - Updated router to support `?source=conf` parameter
   - New response function `get_conf_pipeline_response()`

### Graph Response Format

```json
{
  "nodes": [
    {
      "id": "source.creditTransfer.id",
      "name": "id",
      "type": "sourcefield",
      "tags": [],
      "pipelines": [],
      "modular_pipelines": [],
      "viz": {
        "nodeType": "SourceField",
        "meta": {
          "id": "source.creditTransfer.id",
          "name": "id",
          "avroPath": "id",
          "avroType": "long",
          "nullable": false
        }
      }
    }
  ],
  "edges": [
    {
      "source": "source.creditTransfer.instructedAmount",
      "target": "xform.norm.amount",
      "edgeType": "DERIVES_FROM",
      "metadata": {
        "lifecycle": "Booking",
        "confidence": "final"
      }
    }
  ],
  "layers": [],
  "tags": [],
  "pipelines": [{"id": "conf", "name": "Conf-driven"}],
  "modular_pipelines": {...},
  "selected_pipeline": "conf"
}
```

## Usage Example

1. **Start kedro-viz server:**
   ```bash
   cd /path/to/your/project
   kedro viz
   ```

2. **Access conf-driven graph:**
   ```bash
   curl "http://localhost:4141/api/main?source=conf"
   ```

3. **Default Kedro pipeline graph:**
   ```bash
   curl "http://localhost:4141/api/main"
   ```

## Testing

A test script is provided to validate the implementation:

```bash
python tools/test_conf_graph.py
```

This test:
- Loads the lineage-project example
- Validates node and edge creation
- Checks for unexpected nodes (e.g., "map_to_*", "normalize_*")
- Verifies transform nodes have correct types
- Validates edge connectivity

## Validation Results (lineage-project)

```
✓ Total nodes: 468
  - SourceField: 227
  - CanonicalField: 199
  - Group: 41
  - TransformationNormalize: 1

✓ Total edges: 2

✓ No unexpected 'map_to_' or 'normalize_' nodes found
✓ All edges reference valid nodes
✓ Transform nodes have correct nodeType
```

## Key Features

1. **No Kedro Pipeline Dependency**: Builds graphs entirely from YAML
2. **Stable Node IDs**: Uses explicit field.id values
3. **Flexible Metadata**: Preserves all field metadata in viz.meta
4. **Smart Node Typing**: Infers node types from id prefixes
5. **Placeholder Nodes**: Creates placeholders for missing references with warnings
6. **Group Support**: Creates collapsible group nodes
7. **Edge Metadata**: Carries mapping metadata onto edges
8. **Backward Compatible**: Default behavior unchanged; new mode via query parameter

## Future Enhancements

Potential improvements for subsequent prompts:
- Label policy (Prompt 3)
- Frontend visualization support
- Additional node types (e.g., different transformation types)
- Validation rules for id naming conventions
- Support for multiple lineage files with merge strategies
