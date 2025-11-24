# tools/market_trends.py
"""
Market Trends Tool with Google Custom Search API Integration

Replaces Day 2 mock implementation with real API integration.
Falls back to mock if API fails or rate limit exceeded.
"""

import os
import time
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_tool import BaseTool


class MarketTrendsTool(BaseTool):
    """
    Search for market trends using Google Custom Search API.
    
    Features:
    - Real Google Search API integration
    - Fallback to mock data on API failure
    - Rate limiting (max 3 requests per session)
    - Caching of search results
    
    Environment Variables:
    - GOOGLE_API_KEY: Google API key
    - GOOGLE_CSE_ID: Custom Search Engine ID
    
    Example:
        tool = MarketTrendsTool()
        result = await tool.execute(
            topic="Revenue spike",
            region="US",
            use_api=True
        )
    """
    
    def __init__(self):
        super().__init__(
            name="search_market_trends",
            description="Search for market trends using Google API or mock data"
        )
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.request_count = 0
        self.max_requests = 3
        self.cache: Dict[str, Any] = {}
    
    async def execute(
        self,
        topic: str,
        region: str = "Global",
        use_api: bool = True,
        max_results: int = 5
    ):
        """
        Search for market trends related to a topic.
        
        Args:
            topic: Search topic/query
            region: Geographic region for search
            use_api: Whether to use real API (True) or mock (False)
            max_results: Maximum number of results to return
            
        Returns:
            Result object with trends data
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = f"{topic}_{region}"
            if cache_key in self.cache:
                execution_time = (time.time() - start_time) * 1000
                return type("Result", (), {
                    "success": True,
                    "data": {
                        **self.cache[cache_key],
                        "cached": True
                    },
                    "error": None,
                    "execution_time_ms": execution_time
                })()
            
            # Use API if enabled and credentials available
            if use_api and self.api_key and self.cse_id:
                if self.request_count >= self.max_requests:
                    # Rate limit exceeded, fallback to mock
                    result_data = self._get_mock_trends(topic, region)
                    result_data["source"] = "Mock (rate limit)"
                else:
                    try:
                        result_data = await self._search_google_api(topic, region, max_results)
                        self.request_count += 1
                    except Exception as api_error:
                        # API failed, fallback to mock
                        result_data = self._get_mock_trends(topic, region)
                        result_data["source"] = f"Mock (API error: {str(api_error)[:50]})"
            else:
                # No API credentials or API disabled
                result_data = self._get_mock_trends(topic, region)
                result_data["source"] = "Mock (no API credentials)"
            
            # Cache result
            self.cache[cache_key] = result_data
            
            execution_time = (time.time() - start_time) * 1000
            
            return type("Result", (), {
                "success": True,
                "data": result_data,
                "error": None,
                "execution_time_ms": execution_time
            })()
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return type("Result", (), {
                "success": False,
                "data": None,
                "error": f"Market trends search failed: {str(e)}",
                "execution_time_ms": execution_time
            })()
    
    async def _search_google_api(
        self,
        topic: str,
        region: str,
        max_results: int
    ) -> Dict[str, Any]:
        """
        Execute Google Custom Search API request.
        
        Args:
            topic: Search query
            region: Geographic region
            max_results: Max results to fetch
            
        Returns:
            Dictionary with trends data
        """
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": f"{topic} {region} business trends analysis",
            "num": min(max_results, 10)  # Google API max is 10
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API returned status {response.status}")
                
                data = await response.json()
                
                trends = []
                for item in data.get("items", [])[:max_results]:
                    trends.append({
                        "trend": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "link": item.get("link", ""),
                        "confidence": 0.9,  # High confidence for real API results
                        "region": region,
                        "source": "Google Search API"
                    })
                
                return {
                    "trends": trends,
                    "region": region,
                    "source": "Google Search API",
                    "total_results": data.get("searchInformation", {}).get("totalResults", 0),
                    "search_time": data.get("searchInformation", {}).get("searchTime", 0)
                }
    
    def _get_mock_trends(self, topic: str, region: str) -> Dict[str, Any]:
        """
        Get mock trends data (fallback when API unavailable).
        
        Args:
            topic: Search topic
            region: Geographic region
            
        Returns:
            Dictionary with mock trends data
        """
        mock_trends_db = {
            "Revenue spike": [
                {"trend": "Seasonal demand increase", "confidence": 0.85, "region": region, "source": "Mock DB"},
                {"trend": "New product launch impact", "confidence": 0.8, "region": region, "source": "Mock DB"},
                {"trend": "Market expansion effects", "confidence": 0.75, "region": region, "source": "Mock DB"}
            ],
            "Sales decline": [
                {"trend": "Economic downturn", "confidence": 0.85, "region": region, "source": "Mock DB"},
                {"trend": "Increased competition", "confidence": 0.7, "region": region, "source": "Mock DB"},
                {"trend": "Market saturation", "confidence": 0.65, "region": region, "source": "Mock DB"}
            ],
            "Customer churn": [
                {"trend": "Service quality issues", "confidence": 0.8, "region": region, "source": "Mock DB"},
                {"trend": "Competitive alternatives", "confidence": 0.75, "region": region, "source": "Mock DB"},
                {"trend": "Pricing concerns", "confidence": 0.7, "region": region, "source": "Mock DB"}
            ]
        }
        
        # Try to find matching topic
        for key in mock_trends_db.keys():
            if key.lower() in topic.lower() or topic.lower() in key.lower():
                return {
                    "trends": mock_trends_db[key],
                    "region": region,
                    "source": "Mock DB"
                }
        
        # Default fallback
        return {
            "trends": [
                {"trend": "Market volatility", "confidence": 0.75, "region": region, "source": "Mock DB"},
                {"trend": "Industry changes", "confidence": 0.7, "region": region, "source": "Mock DB"}
            ],
            "region": region,
            "source": "Mock DB"
        }
