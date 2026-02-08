import { createSelector } from 'reselect';

// Get raw nodes from normalized state, not computed graph
const getNodeIds = (state) => state.node.ids || [];
const getNodeViz = (state) => state.node.viz || {};
const getNodeName = (state) => state.node.name || {};

/**
 * Build a membership index: Map from field node ID to group node ID
 * If a field belongs to multiple groups, the first match wins (with a warning in console).
 */
export const getMemberToGroupMap = createSelector(
  [getNodeIds, getNodeViz],
  (nodeIds, nodeViz) => {
    const memberToGroup = {};
    const multiMembership = {};

    // Find all Group nodes and index their members
    nodeIds.forEach((nodeId) => {
      const viz = nodeViz[nodeId];
      if (viz?.nodeType === 'Group' && viz?.meta?.members) {
        const groupId = nodeId;
        const members = viz.meta.members;

        members.forEach((memberId) => {
          if (memberToGroup[memberId]) {
            // Track multi-membership for warning
            if (!multiMembership[memberId]) {
              multiMembership[memberId] = [memberToGroup[memberId]];
            }
            multiMembership[memberId].push(groupId);
          } else {
            memberToGroup[memberId] = groupId;
          }
        });
      }
    });

    // Log warnings for multi-membership
    Object.entries(multiMembership).forEach(([memberId, groupIds]) => {
      console.warn(
        `Field node ${memberId} belongs to multiple groups: ${groupIds.join(
          ', '
        )}. Using first: ${groupIds[0]}`
      );
    });

    return memberToGroup;
  }
);

/**
 * Get all group nodes from the graph
 */
export const getGroupNodes = createSelector(
  [getNodeIds, getNodeViz, getNodeName],
  (nodeIds, nodeViz, nodeName) =>
    nodeIds
      .filter((id) => nodeViz[id]?.nodeType === 'Group')
      .map((id) => ({
        id,
        name: nodeName[id],
        viz: nodeViz[id],
      }))
);

/**
 * DEPRECATED: Old version that relied on state.graph
 */
export const getGroupNodesOld = createSelector([() => []], (nodes) =>
  nodes.filter((node) => node.viz?.nodeType === 'Group')
);

/**
 * Check if a node is a Group node (using viz field from normalized or graph node)
 */
export const isGroupNode = (node) => node.viz?.nodeType === 'Group';

/**
 * Check if a node ID is a Group node (using normalized state)
 */
export const isGroupNodeById = (nodeId, nodeViz) =>
  nodeViz[nodeId]?.nodeType === 'Group';

/**
 * Check if a node is a member of any group
 */
export const isMemberOfGroup = createSelector(
  [getMemberToGroupMap, (state, nodeId) => nodeId],
  (memberToGroup, nodeId) => Boolean(memberToGroup[nodeId])
);

/**
 * Get the group ID for a given field node (if it belongs to one)
 */
export const getGroupForMember = createSelector(
  [getMemberToGroupMap, (state, nodeId) => nodeId],
  (memberToGroup, nodeId) => memberToGroup[nodeId] || null
);
