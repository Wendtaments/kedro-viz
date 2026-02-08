import { TOGGLE_GROUP_EXPANDED } from '../actions/groups';
import { RESET_DATA } from '../actions';

/**
 * Reducer for group expand/collapse state
 * @param {Object} state Current state
 * @param {Object} action Redux action
 * @returns {Object} Updated state
 */
function groupsReducer(state = {}, action) {
  switch (action.type) {
    case TOGGLE_GROUP_EXPANDED: {
      const { groupId } = action;
      const newExpandedState = { ...state };

      if (newExpandedState[groupId]) {
        delete newExpandedState[groupId];
      } else {
        newExpandedState[groupId] = true;
      }

      return newExpandedState;
    }

    case RESET_DATA: {
      // Reset to empty (all groups collapsed by default)
      return {};
    }

    default:
      return state;
  }
}

export default groupsReducer;
