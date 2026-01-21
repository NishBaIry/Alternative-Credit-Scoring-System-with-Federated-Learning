# score_explain_service.py
# Service for generating human-readable explanations of credit scores.
# Functions:
# - explain_score(customer_id): returns top factors (positive/negative) with natural language
# - get_recommendations(customer_id): suggests actionable improvements
# - compute_shap_values(features): calculates SHAP contributions if available
# Makes the "Why is my score like this?" feature work for clients.
# Used by both client and staff UIs for transparency and explainability.

from typing import Dict, List
import numpy as np

class ScoreExplainService:
    """Service for explaining credit scores."""
    
    def __init__(self, bank_id: str):
        self.bank_id = bank_id
    
    def explain_score(self, customer_id: str, score: int, features: Dict) -> Dict:
        """
        Generate natural language explanation for a score.
        """
        factors = self._identify_top_factors(features, score)
        recommendations = self._generate_recommendations(factors)
        
        return {
            "customer_id": customer_id,
            "score": score,
            "factors": factors,
            "recommendations": recommendations
        }
    
    def _identify_top_factors(self, features: Dict, score: int) -> List[Dict]:
        """
        Identify top positive and negative factors.
        """
        # TODO: Implement actual factor analysis
        # Based on feature importance and SHAP values
        
        factors = []
        
        # Example factors
        if features.get('utility_bill_score', 0) > 80:
            factors.append({
                "name": "High bill on-time rate",
                "impact": "positive",
                "contribution": 45,
                "description": "Consistent utility and rent payments improve your score"
            })
        
        if features.get('dti', 0) > 40:
            factors.append({
                "name": "High DTI ratio",
                "impact": "negative",
                "contribution": -15,
                "description": "Your debt-to-income ratio is above the recommended threshold"
            })
        
        if features.get('upi_essentials_share', 0) > 0.5:
            factors.append({
                "name": "Strong UPI essentials share",
                "impact": "positive",
                "contribution": 30,
                "description": "High proportion of essential spending (groceries, fuel) shows financial responsibility"
            })
        
        return factors
    
    def _generate_recommendations(self, factors: List[Dict]) -> List[str]:
        """
        Generate actionable recommendations based on factors.
        """
        recommendations = []
        
        for factor in factors:
            if factor['impact'] == 'negative':
                if 'DTI' in factor['name']:
                    recommendations.append("Try to keep your debt-to-income ratio below 40%")
                elif 'delinquency' in factor['name'].lower():
                    recommendations.append("Maintain on-time payments for the next 3-6 months")
        
        # Add general recommendations
        recommendations.extend([
            "Increase UPI essentials share (Grocery/Fuel) and reduce impulsive shopping",
            "Maintain on-time utility and rent payments",
            "Build consistent income and savings patterns"
        ])
        
        return recommendations[:5]  # Top 5 recommendations
    
    def compute_shap_values(self, features: Dict, model) -> Dict:
        """
        Compute SHAP values for detailed feature contributions.
        """
        # TODO: Implement SHAP calculation
        # Requires SHAP library and trained model
        
        return {
            "base_value": 0.5,
            "shap_values": {},
            "feature_values": features
        }
    
    def get_score_history(self, customer_id: str) -> List[Dict]:
        """
        Get historical scores for a customer.
        """
        # TODO: Implement score history retrieval
        return [
            {
                "score": 742,
                "date": "2026-01-17",
                "risk_band": "Low"
            }
        ]

def get_explain_service(bank_id: str) -> ScoreExplainService:
    """Factory function to get explain service for a bank."""
    return ScoreExplainService(bank_id)
