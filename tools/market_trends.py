from .base_tool import BaseTool

class MarketTrendsTool(BaseTool):
    def __init__(self):
        super().__init__("search_market_trends", "Search for market trends (mock, ready for API integration)")

    async def execute(self, topic, region="Global"):
        mock_trends_db = {
            "Sales decline": [
                {"trend": "Economic downturn", "confidence": 0.85, "region": region, "source": "Mock DB"},
                {"trend": "Increased competition", "confidence": 0.7, "region": region, "source": "Mock DB"}
            ],
            "Customer churn": [
                {"trend": "Changing expectations", "confidence": 0.8, "region": region, "source": "Mock DB"}
            ],
        }
        results = mock_trends_db.get(topic, [
            {"trend": "Market volatility", "confidence": 0.75, "region": region, "source": "Mock DB"}
        ])
        return type("Result", (), {
            "success": True,
            "data": {
                "trends": results,
                "region": region,
                "source": "Mock DB"
            }
        })()
