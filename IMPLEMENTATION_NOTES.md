# Group Expand/Collapse Implementation

## Summary
Implementation of expand/collapse functionality for Group nodes in kedro-viz frontend, with multi-group support and aggregated edge rendering when groups are collapsed.

## Files Created/Modified

### New Files
1. **src/actions/groups.js** - Actions for toggling group expansion
2. **src/reducers/groups.js** - Reducer managing group expand/collapse state
3. **src/selectors/groups.js** - Selectors for group membership indexing
4. **src/selectors/group-view.js** - Core logic for node visibility and edge aggregation
5. **src/utils/edge-tooltip.js** - Tooltip formatting for aggregated edges

### Modified Files
1. **src/reducers/index.js** - Added groups reducer to root reducer
2. **src/selectors/layout.js** - Integrated group-aware nodes and view edges
3. **src/components/flowchart/flowchart.jsx** - Added click handler for Group nodes

## Implementation Details

### 1. State Management
- **State**: `expandedGroupIds` stored as an object `{groupId: true}` (default: empty = all collapsed)
- **Action**: `TOGGLE_GROUP_EXPANDED` - toggles a group's expansion state
- **Reducer**: Adds/removes group IDs from the expanded state object

### 2. Membership Index
- Builds a `memberToGroupId` map from field node IDs to their parent group IDs
- Scans all Group nodes with `viz.nodeType === 'Group'` and their `viz.meta.members` arrays
- Handles multi-membership (warns and uses first match)

### 3. Visibility Rules
Implemented in `getGroupAwareVisibleNodes` selector:
- **Group nodes**: always visible
- **Field nodes in groups**: visible only when their group is expanded
- **Nodes not in any group**: always visible
- **Transform nodes**: always visible

### 4. Edge Resolution & Aggregation
Implemented in `getViewEdges` selector:

**Endpoint Resolution**:
```javascript
resolveEndpoint(nodeId):
  if nodeId is member of collapsed group G: return G
  else: return nodeId
```

**Edge Processing**:
- For each edge (source → target):
  1. Resolve both endpoints
  2. If both resolve to same node: drop (internal to collapsed group)
  3. Otherwise: create view edge
- Deduplicate by `(sourceId, targetId, edgeType)`
- Aggregate metadata:
  - `count`: number of underlying edges
  - `sample`: up to 3 example source→target pairs
  - `aggregated`: true if count > 1

### 5. User Interaction
- Clicking a Group node toggles its expansion state
- The graph automatically re-renders with updated node visibility and edge aggregation
- Multiple groups can be expanded simultaneously

### 6. Tooltips (Utility Created)
**File**: `src/utils/edge-tooltip.js`
- `getEdgeTooltipText(edge)`: Formats tooltip showing:
  - Edge type + count for aggregated edges
  - Sample list (up to 3) of underlying edges
  - Count of additional edges if > 3 samples
- `isAggregatedEdge(edge)`: Helper to check if edge is aggregated

## Integration Points

### Layout Selector (`src/selectors/layout.js`)
The `getGraphInput` selector now:
1. Calls `getGroupAwareVisibleNodes` to filter nodes based on group state
2. Calls `getViewEdges` to compute aggregated edges
3. Passes these to the graph layout calculator

### FlowChart Component (`src/components/flowchart/flowchart.jsx`)
The `handleNodeClick` method now:
1. Checks if clicked node has `type === 'group'`
2. If yes, calls `onToggleGroupExpanded(nodeId)`
3. Otherwise, processes as normal node click

## Testing

### Build Status
✅ Build successful - all files compile without errors

### Manual Testing Checklist
To fully test the implementation:

1. **Default State** (all collapsed):
   - [ ] All Group nodes visible
   - [ ] No member field nodes visible
   - [ ] Edges between groups are aggregated

2. **Single Group Expansion**:
   - [ ] Click a Group node
   - [ ] Member fields appear
   - [ ] Edges from members to other groups or non-grouped nodes appear
   - [ ] Edges to collapsed groups show as group→group

3. **Multiple Groups Expanded**:
   - [ ] Expand two groups
   - [ ] Both sets of member fields visible
   - [ ] Edges between expanded group members shown as field→field
   - [ ] Edges to collapsed groups still aggregated

4. **Edge Aggregation**:
   - [ ] Collapsed group-to-group edges show aggregation metadata
   - [ ] Edge count is correct
   - [ ] Sample list shows underlying edges (up to 3)

5. **Toggle Behavior**:
   - [ ] Clicking expanded group collapses it
   - [ ] Member fields disappear
   - [ ] Edges are re-aggregated

## Next Steps (Not Implemented)

The following features were mentioned in the prompt but require additional UI work:

1. **Edge Tooltips Integration**: The utility functions are created (`edge-tooltip.js`), but actual tooltip rendering on hover needs to be integrated with the edge drawing component (`draw-edges.jsx`)

2. **Visual Indicators**: Could add visual cues:
   - Expand/collapse icon on Group nodes
   - Badge showing number of hidden members
   - Different styling for aggregated vs. normal edges

3. **Persistence**: Could save expand/collapse state to localStorage

4. **Animation**: Smooth transitions when expanding/collapsing groups

## Notes

- Implementation follows the existing patterns in kedro-viz (Redux, Reselect, D3)
- Group nodes are identified by `type === 'group'` which maps to `viz.nodeType === 'Group'`
- Edge aggregation is computed on-the-fly in selectors (no mutation of underlying data)
- Compatible with existing features (slicing, focus mode, etc.) as they operate on the view layer
