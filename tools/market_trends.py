def search_trends(data, query=None, top_n=3):
    """
    Search for market trends in the business metrics dataset.
    Arguments:
        data: list of dicts, usually business metrics
        query: optional search keyword (e.g., "growth", "competition")
        top_n: number of trends to return
    Returns:
        dict with 'trends' list and metadata
    """
    # Example stub: find rows where 'trend' or 'pattern' matches query, or return dummy if no logic
    results = []
    if query:
        for row in data:
            if query.lower() in str(row.get("trend", "")).lower() or query.lower() in str(row.get("pattern", "")).lower():
                results.append(row)
    else:
        results = data[:top_n] if isinstance(data, list) else []
    return {
        "trends": results,
        "query": query,
        "returned": len(results)
    }
