# agents/recommendation.py
"""
RecommendationAgent: Action-Oriented Recommendation Generation

Generates prioritized, actionable recommendations based on
analysis results from AnalystAgent.

Collaborates with:
- AnalystAgent: Receives analysis results
- ToolRegistry: Uses market trends and logging tools
- CoordinatorAgent: Passes recommendations to final report
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from core.context import SharedContext


@dataclass
class ActionItem:
    """Single actionable recommendation."""
    id: str
    title: str
    description: str
    priority: int  # 1-5, 1=highest
    expected_impact: str  # "High", "Medium", "Low"
    implementation_effort: str  # "Low", "Medium", "High"
    timeline: str  # "Immediate", "Short-term", "Long-term"
    success_metrics: List[str]
    owner: Optional[str] = None
    status: str = "pending"


@dataclass
class RecommendationResult:
    """Complete recommendation result from RecommendationAgent."""
    action_items: List[ActionItem]
    quick_wins: List[ActionItem]
    strategic_initiatives: List[ActionItem]
    risk_assessment: Dict[str, Any]
    expected_outcomes: List[Dict[str, Any]]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class RecommendationAgent:
    """
    Specialized agent for generating actionable recommendations.
    
    Responsibilities:
    1. Generate recommendations based on analysis
    2. Prioritize actions (quick wins vs strategic)
    3. Assess implementation risks
    4. Predict expected outcomes
    """
    
    def __init__(self, tool_registry, shared_context: SharedContext):
        """
        Initialize RecommendationAgent.
        
        Args:
            tool_registry: ToolRegistry instance for accessing tools
            shared_context: SharedContext for agent communication
        """
        self.registry = tool_registry
        self.context = shared_context
        self.name = "RecommendationAgent"
    
    async def generate_recommendations(
        self,
        analysis_result: Dict[str, Any]
    ) -> RecommendationResult:
        """
        Generate prioritized recommendations based on analysis.
        
        Args:
            analysis_result: Analysis result from AnalystAgent
            
        Returns:
            RecommendationResult with prioritized action items
        """
        logger = self.registry.get_tool("log_agent_action")
        await logger.execute(
            agent_name=self.name,
            action="start_recommendation_generation",
            details={"severity": analysis_result.get("severity")},
            level="INFO"
        )
        
        # Generate base recommendations
        action_items = await self._generate_base_recommendations(analysis_result)
        
        # Categorize recommendations
        quick_wins, strategic = self._categorize_recommendations(action_items)
        
        # Assess risks
        risk_assessment = self._assess_risks(action_items)
        
        # Predict outcomes
        expected_outcomes = self._predict_outcomes(action_items)
        
        result = RecommendationResult(
            action_items=action_items,
            quick_wins=quick_wins,
            strategic_initiatives=strategic,
            risk_assessment=risk_assessment,
            expected_outcomes=expected_outcomes
        )
        
        # Store in shared context
        await self.context.set("recommendation_result", {
            "action_items": [self._action_to_dict(a) for a in action_items],
            "quick_wins": [self._action_to_dict(a) for a in quick_wins],
            "strategic_initiatives": [self._action_to_dict(a) for a in strategic],
            "risk_assessment": risk_assessment,
            "expected_outcomes": expected_outcomes
        })
        
        await logger.execute(
            agent_name=self.name,
            action="recommendations_generated",
            details={
                "total_actions": len(action_items),
                "quick_wins": len(quick_wins),
                "strategic": len(strategic)
            },
            level="INFO"
        )
        
        return result
    
    async def _generate_base_recommendations(
        self,
        analysis_result: Dict[str, Any]
    ) -> List[ActionItem]:
        """Generate base recommendations from analysis."""
        recommendations = []
        patterns = analysis_result.get("patterns", [])
        severity = analysis_result.get("severity", "MEDIUM")
        
        action_id = 1
        
        for pattern in patterns:
            pattern_type = pattern.get("pattern_type", "unknown")
            
            if pattern_type == "spike":
                recommendations.append(ActionItem(
                    id=f"ACT-{action_id:03d}",
                    title="Investigate Revenue Spike Root Cause",
                    description="Analyze the factors contributing to the revenue spike to determine if it's sustainable or one-time event.",
                    priority=2,
                    expected_impact="High",
                    implementation_effort="Medium",
                    timeline="Immediate",
                    success_metrics=["Root cause identified", "Sustainability assessment completed"]
                ))
                action_id += 1
                
                recommendations.append(ActionItem(
                    id=f"ACT-{action_id:03d}",
                    title="Capitalize on Spike Drivers",
                    description="If spike is driven by specific factors (promotion, product), develop strategy to replicate success.",
                    priority=1,
                    expected_impact="High",
                    implementation_effort="Medium",
                    timeline="Short-term",
                    success_metrics=["Strategy documented", "Implementation plan created"]
                ))
                action_id += 1
                
            elif pattern_type == "drop":
                recommendations.append(ActionItem(
                    id=f"ACT-{action_id:03d}",
                    title="Emergency Revenue Recovery Plan",
                    description="Develop and implement immediate actions to stabilize and recover revenue.",
                    priority=1,
                    expected_impact="High",
                    implementation_effort="High",
                    timeline="Immediate",
                    success_metrics=["Recovery plan deployed", "Revenue stabilized"]
                ))
                action_id += 1
                
                recommendations.append(ActionItem(
                    id=f"ACT-{action_id:03d}",
                    title="Customer Retention Analysis",
                    description="Analyze customer churn and implement retention strategies.",
                    priority=2,
                    expected_impact="Medium",
                    implementation_effort="Medium",
                    timeline="Short-term",
                    success_metrics=["Churn rate reduced by 15%", "Retention program launched"]
                ))
                action_id += 1
        
        # Add general recommendations based on severity
        if severity == "HIGH":
            recommendations.append(ActionItem(
                id=f"ACT-{action_id:03d}",
                title="Executive Review and Decision",
                description="Escalate findings to executive team for strategic review and decision-making.",
                priority=1,
                expected_impact="High",
                implementation_effort="Low",
                timeline="Immediate",
                success_metrics=["Executive briefing completed", "Strategic decisions documented"]
            ))
            action_id += 1
        
        recommendations.append(ActionItem(
            id=f"ACT-{action_id:03d}",
            title="Enhanced Monitoring System",
            description="Implement real-time monitoring to detect similar patterns early.",
            priority=3,
            expected_impact="Medium",
            implementation_effort="Medium",
            timeline="Long-term",
            success_metrics=["Monitoring system deployed", "Alert thresholds configured"]
        ))
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)
        
        return recommendations
    
    def _categorize_recommendations(
        self,
        action_items: List[ActionItem]
    ) -> tuple[List[ActionItem], List[ActionItem]]:
        """Categorize recommendations into quick wins and strategic initiatives."""
        quick_wins = [
            item for item in action_items
            if item.implementation_effort == "Low" and item.priority <= 2
        ]
        
        strategic = [
            item for item in action_items
            if item.timeline in ["Long-term", "Short-term"] and item.expected_impact == "High"
        ]
        
        return quick_wins, strategic
    
    def _assess_risks(self, action_items: List[ActionItem]) -> Dict[str, Any]:
        """Assess implementation risks."""
        high_priority_count = sum(1 for item in action_items if item.priority == 1)
        high_effort_count = sum(1 for item in action_items if item.implementation_effort == "High")
        
        risk_level = "LOW"
        if high_priority_count >= 3 or high_effort_count >= 2:
            risk_level = "HIGH"
        elif high_priority_count >= 2 or high_effort_count >= 1:
            risk_level = "MEDIUM"
        
        return {
            "overall_risk_level": risk_level,
            "resource_constraints": high_effort_count >= 2,
            "timeline_pressure": high_priority_count >= 3,
            "mitigation_strategies": [
                "Prioritize critical actions",
                "Allocate dedicated resources",
                "Establish clear ownership",
                "Regular progress monitoring"
            ]
        }
    
    def _predict_outcomes(self, action_items: List[ActionItem]) -> List[Dict[str, Any]]:
        """Predict expected outcomes from implementing recommendations."""
        outcomes = []
        
        high_impact_count = sum(1 for item in action_items if item.expected_impact == "High")
        
        if high_impact_count >= 2:
            outcomes.append({
                "outcome": "Revenue stabilization and growth",
                "probability": "High",
                "timeframe": "1-3 months",
                "quantitative_impact": "10-25% improvement"
            })
        
        outcomes.append({
            "outcome": "Improved operational visibility",
            "probability": "High",
            "timeframe": "1-2 months",
            "quantitative_impact": "Real-time monitoring established"
        })
        
        outcomes.append({
            "outcome": "Enhanced decision-making capability",
            "probability": "Medium",
            "timeframe": "3-6 months",
            "quantitative_impact": "Reduced response time by 50%"
        })
        
        return outcomes
    
    def _action_to_dict(self, action: ActionItem) -> Dict[str, Any]:
        """Convert ActionItem to dictionary."""
        return {
            "id": action.id,
            "title": action.title,
            "description": action.description,
            "priority": action.priority,
            "expected_impact": action.expected_impact,
            "implementation_effort": action.implementation_effort,
            "timeline": action.timeline,
            "success_metrics": action.success_metrics,
            "owner": action.owner,
            "status": action.status
        }
