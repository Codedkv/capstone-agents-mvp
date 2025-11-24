# agents/analyst.py
"""
AnalystAgent: Deep Analysis of Business Anomalies

Performs statistical analysis, pattern detection, and root cause
identification on detected anomalies.

Collaborates with:
- CoordinatorAgent: Receives detected anomalies
- ToolRegistry: Uses anomaly detection and market trends tools
- RecommendationAgent: Passes analysis for recommendations
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from core.context import SharedContext


@dataclass
class AnomalyPattern:
    """Detected anomaly pattern with metadata."""
    metric: str
    pattern_type: str  # "spike", "drop", "trend", "seasonal"
    severity: str  # "HIGH", "MEDIUM", "LOW"
    values: List[float]
    timestamps: List[str]
    magnitude: float  # Deviation percentage
    confidence: float  # 0-1 score
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AnalysisResult:
    """Complete analysis result from AnalystAgent."""
    patterns: List[AnomalyPattern]
    potential_causes: List[Dict[str, Any]]
    severity_assessment: str
    market_context: List[Dict[str, Any]]
    confidence_score: float
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AnalystAgent:
    """
    Specialized agent for deep anomaly analysis.
    
    Responsibilities:
    1. Detect patterns in anomalies (spikes, drops, trends)
    2. Identify potential root causes
    3. Search for relevant market context
    4. Assess severity and confidence
    """
    
    def __init__(self, tool_registry, shared_context: SharedContext):
        """
        Initialize AnalystAgent.
        
        Args:
            tool_registry: ToolRegistry instance for accessing tools
            shared_context: SharedContext for agent communication
        """
        self.registry = tool_registry
        self.context = shared_context
        self.name = "AnalystAgent"
    
    async def analyze(self, raw_data: List[Dict], anomalies: List[float]) -> AnalysisResult:
        """
        Perform deep analysis on detected anomalies.
        
        Args:
            raw_data: Original CSV data
            anomalies: List of anomalous values detected
            
        Returns:
            AnalysisResult with patterns, causes, and context
        """
        logger = self.registry.get_tool("log_agent_action")
        await logger.execute(
            agent_name=self.name,
            action="start_analysis",
            details={"anomaly_count": len(anomalies)},
            level="INFO"
        )
        
        # Extract patterns from anomalies
        patterns = await self._extract_patterns(raw_data, anomalies)
        
        # Identify potential causes
        potential_causes = await self._identify_causes(patterns)
        
        # Search market context
        market_context = await self._search_market_context(patterns)
        
        # Assess overall severity
        severity = self._assess_severity(patterns)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(patterns, market_context)
        
        result = AnalysisResult(
            patterns=patterns,
            potential_causes=potential_causes,
            severity_assessment=severity,
            market_context=market_context,
            confidence_score=confidence
        )
        
        # Store in shared context
        await self.context.set("analysis_result", {
            "patterns": [self._pattern_to_dict(p) for p in patterns],
            "potential_causes": potential_causes,
            "severity": severity,
            "market_context": market_context,
            "confidence": confidence
        })
        
        await logger.execute(
            agent_name=self.name,
            action="analysis_complete",
            details={
                "patterns_found": len(patterns),
                "severity": severity,
                "confidence": confidence
            },
            level="INFO"
        )
        
        return result
    
    async def _extract_patterns(
        self,
        raw_data: List[Dict],
        anomalies: List[float]
    ) -> List[AnomalyPattern]:
        """Extract patterns from raw data and anomalies."""
        patterns = []
        
        if not anomalies:
            return patterns
        
        # Get revenue values and dates
        revenues = [float(row['revenue']) for row in raw_data]
        dates = [row['date'] for row in raw_data]
        
        avg_revenue = sum(revenues) / len(revenues)
        
        for anomaly_value in anomalies:
            # Find timestamp of anomaly
            try:
                idx = revenues.index(anomaly_value)
                timestamp = dates[idx]
            except ValueError:
                timestamp = "unknown"
            
            # Determine pattern type
            deviation_pct = ((anomaly_value - avg_revenue) / avg_revenue) * 100
            
            if deviation_pct > 20:
                pattern_type = "spike"
                severity = "HIGH"
            elif deviation_pct < -20:
                pattern_type = "drop"
                severity = "HIGH"
            elif abs(deviation_pct) > 10:
                pattern_type = "trend"
                severity = "MEDIUM"
            else:
                pattern_type = "fluctuation"
                severity = "LOW"
            
            pattern = AnomalyPattern(
                metric="revenue",
                pattern_type=pattern_type,
                severity=severity,
                values=[anomaly_value],
                timestamps=[timestamp],
                magnitude=abs(deviation_pct),
                confidence=0.85
            )
            patterns.append(pattern)
        
        return patterns
    
    async def _identify_causes(self, patterns: List[AnomalyPattern]) -> List[Dict[str, Any]]:
        """Identify potential root causes for detected patterns."""
        causes = []
        
        for pattern in patterns:
            if pattern.pattern_type == "spike":
                causes.extend([
                    {
                        "cause": "Seasonal demand increase",
                        "confidence": 0.75,
                        "category": "market"
                    },
                    {
                        "cause": "New product launch or promotion",
                        "confidence": 0.7,
                        "category": "internal"
                    },
                    {
                        "cause": "One-time large transaction",
                        "confidence": 0.65,
                        "category": "operational"
                    }
                ])
            elif pattern.pattern_type == "drop":
                causes.extend([
                    {
                        "cause": "Market downturn or economic factors",
                        "confidence": 0.75,
                        "category": "market"
                    },
                    {
                        "cause": "Operational issues or outages",
                        "confidence": 0.7,
                        "category": "operational"
                    },
                    {
                        "cause": "Increased competition",
                        "confidence": 0.65,
                        "category": "competitive"
                    }
                ])
        
        # Limit to top 5 causes by confidence
        causes.sort(key=lambda x: x['confidence'], reverse=True)
        return causes[:5]
    
    async def _search_market_context(self, patterns: List[AnomalyPattern]) -> List[Dict[str, Any]]:
        """Search for market context related to patterns."""
        market_trends_tool = self.registry.get_tool("search_market_trends")
        
        all_trends = []
        
        for pattern in patterns[:2]:  # Limit to 2 patterns to avoid rate limits
            topic = f"{pattern.pattern_type} in {pattern.metric}"
            
            result = await market_trends_tool.execute(
                topic=topic,
                region="Global",
                use_api=True
            )
            
            if result.success and result.data:
                trends = result.data.get("trends", [])
                all_trends.extend(trends[:3])  # Top 3 per pattern
        
        return all_trends
    
    def _assess_severity(self, patterns: List[AnomalyPattern]) -> str:
        """Assess overall severity based on patterns."""
        if not patterns:
            return "LOW"
        
        high_count = sum(1 for p in patterns if p.severity == "HIGH")
        
        if high_count >= 2:
            return "HIGH"
        elif high_count == 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(
        self,
        patterns: List[AnomalyPattern],
        market_context: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence score."""
        if not patterns:
            return 0.0
        
        # Base confidence from patterns
        pattern_confidence = sum(p.confidence for p in patterns) / len(patterns)
        
        # Bonus for market context
        context_bonus = min(0.15, len(market_context) * 0.05)
        
        return min(1.0, pattern_confidence + context_bonus)
    
    def _pattern_to_dict(self, pattern: AnomalyPattern) -> Dict[str, Any]:
        """Convert AnomalyPattern to dictionary."""
        return {
            "metric": pattern.metric,
            "pattern_type": pattern.pattern_type,
            "severity": pattern.severity,
            "values": pattern.values,
            "timestamps": pattern.timestamps,
            "magnitude": pattern.magnitude,
            "confidence": pattern.confidence,
            "detected_at": pattern.detected_at
        }
