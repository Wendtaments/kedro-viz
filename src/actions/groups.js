export const TOGGLE_GROUP_EXPANDED = 'TOGGLE_GROUP_EXPANDED';

/**
 * Toggle a group node's expanded/collapsed state
 * @param {String} groupId The group node's unique identifier
 */
export function toggleGroupExpanded(groupId) {
  return {
    type: TOGGLE_GROUP_EXPANDED,
    groupId,
  };
}
