/**
 * Format tooltip text for edges
 * @param {Object} edge Edge data with aggregationMetadata
 * @returns {String} Formatted tooltip text
 */
export const getEdgeTooltipText = (edge) => {
  if (!edge) {
    return '';
  }

  const { edgeType, aggregationMetadata } = edge;

  if (!aggregationMetadata || !aggregationMetadata.aggregated) {
    // Non-aggregated edge - show simple tooltip
    return edgeType || 'Edge';
  }

  // Aggregated edge - show count and samples
  const { count, sample } = aggregationMetadata;

  let tooltip = `${edgeType || 'Edge'} (${count} edges)\n\n`;
  tooltip += 'Samples:\n';

  sample.forEach(({ source, target }) => {
    tooltip += `• ${source} → ${target}\n`;
  });

  if (count > sample.length) {
    tooltip += `... and ${count - sample.length} more`;
  }

  return tooltip;
};

/**
 * Check if an edge is aggregated
 * @param {Object} edge Edge data
 * @returns {Boolean} True if edge is aggregated
 */
export const isAggregatedEdge = (edge) => {
  return edge?.aggregationMetadata?.aggregated === true;
};
