import { createSelector } from 'reselect';
import { getMemberToGroupMap } from './groups';
import { getVisibleNodes } from './nodes';

const getExpandedGroups = (state) => state.groups || {};
const getNodeViz = (state) => state.node.viz || {};
const getRawEdges = (state) => state.edge.ids || [];
const getEdgeSources = (state) => state.edge.sources || {};
const getEdgeTargets = (state) => state.edge.targets || {};

/**
 * Determine which nodes should be visible based on group expand/collapse state
 * Rules:
 * - Group nodes: always visible
 * - Field nodes that belong to a group: visible only when their group is expanded
 * - Nodes not in any group: always visible
 * - Transform nodes: always visible (unless grouped later)
 */
export const getGroupAwareVisibleNodes = createSelector(
  [getVisibleNodes, getMemberToGroupMap, getExpandedGroups, getNodeViz],
  (nodes, memberToGroup, expandedGroups, nodeViz) => {
    return nodes.filter((node) => {
      // Group nodes are always visible - check viz data by node ID
      const viz = nodeViz[node.id];
      if (viz?.nodeType === 'Group') {
        return true;
      }

      // Check if this node is a member of a group
      const groupId = memberToGroup[node.id];

      if (groupId) {
        // Field node that belongs to a group - visible only if group is expanded
        return Boolean(expandedGroups[groupId]);
      }

      // Nodes not in any group are always visible
      return true;
    });
  }
);

/**
 * Resolve an endpoint for edge computation:
 * - If nodeId is a member of group G AND G is collapsed: return G (group node id)
 * - Else return nodeId
 */
const resolveEndpoint = (nodeId, memberToGroup, expandedGroups) => {
  const groupId = memberToGroup[nodeId];

  if (groupId && !expandedGroups[groupId]) {
    // Node is a member of a collapsed group - return the group ID
    return groupId;
  }

  // Return the original node ID
  return nodeId;
};

/**
 * Compute view edges with aggregation for collapsed groups
 *
 * For each underlying edge (source -> target):
 * - Resolve both endpoints through resolveEndpoint()
 * - If src2 == tgt2: drop edge (internal to same collapsed group)
 * - Else emit a view edge src2 -> tgt2
 *
 * Deduplicate by (sourceId, targetId, edgeType) and aggregate metadata
 */
export const getViewEdges = createSelector(
  [
    getRawEdges,
    getEdgeSources,
    getEdgeTargets,
    getMemberToGroupMap,
    getExpandedGroups,
  ],
  (edgeIds, sources, targets, memberToGroup, expandedGroups) => {
    // Map to track view edges: key = "sourceId|targetId|edgeType"
    const viewEdgesMap = new Map();

    edgeIds.forEach((edgeId) => {
      const originalSource = sources[edgeId];
      const originalTarget = targets[edgeId];
      const edgeType = '';

      if (!originalSource || !originalTarget) {
        return;
      }

      // Resolve endpoints
      const resolvedSource = resolveEndpoint(
        originalSource,
        memberToGroup,
        expandedGroups
      );
      const resolvedTarget = resolveEndpoint(
        originalTarget,
        memberToGroup,
        expandedGroups
      );

      // Drop if both resolve to the same node (internal edge within collapsed group)
      if (resolvedSource === resolvedTarget) {
        return;
      }

      // Create a unique key for deduplication
      const viewEdgeKey = `${resolvedSource}|${resolvedTarget}|${edgeType}`;

      // Aggregate edges
      if (viewEdgesMap.has(viewEdgeKey)) {
        const existingEdge = viewEdgesMap.get(viewEdgeKey);
        existingEdge.aggregationMetadata.count += 1;

        // Add to sample list (max 3)
        if (existingEdge.aggregationMetadata.sample.length < 3) {
          existingEdge.aggregationMetadata.sample.push({
            source: originalSource,
            target: originalTarget,
          });
        }

        // Merge original metadata (keep first one's metadata for simplicity)
        // You could also aggregate metadata fields if needed
      } else {
        // Create new view edge
        viewEdgesMap.set(viewEdgeKey, {
          source: resolvedSource,
          target: resolvedTarget,
          edgeType,
          metadata: {},
          aggregationMetadata: {
            aggregated: false, // Will be set to true if count > 1
            count: 1,
            sample: [
              {
                source: originalSource,
                target: originalTarget,
              },
            ],
          },
        });
      }
    });

    // Convert map to array and mark aggregated edges
    const viewEdges = Array.from(viewEdgesMap.values()).map((edge) => {
      if (edge.aggregationMetadata.count > 1) {
        edge.aggregationMetadata.aggregated = true;
      }
      return edge;
    });

    return viewEdges;
  }
);
