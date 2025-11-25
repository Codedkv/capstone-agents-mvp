from typing import List, Dict, Any, Optional

def search_trends(
    data: List[Dict[str, Any]], 
    query: Optional[str] = None, 
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Search for market trends in the business metrics dataset.
    
    Args:
        data: List of dictionaries with business metrics (each dict = row)
        query: Optional search keyword for trends (e.g., 'growth')
        top_n: Number of trends to return (default 3)
    
    Returns:
        Dictionary with:
        - trends (list): List of identified trends (rows matching query or top_n)
        - query (str): The query used
        - returned (int): Count of trends returned
    """
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
