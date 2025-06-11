from typing import List, Dict, Any
from ..agents.party_agent import PartyAgent

class PartyDiscussion:
    """
    Simulates discussions within a party.
    """
    def __init__(self, party: PartyAgent):
        """
        Initialize a party discussion.
        
        Args:
            party: The party agent
        """
        self.party = party
    
    def discuss_legislation(self, legislation_text: str) -> Dict[str, Any]:
        """
        Simulate a discussion within the party about a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the discussion
        """
        # Get opinions from all politicians in the party
        opinions = self.party.get_politicians_opinions(legislation_text)
        
        # Analyze the opinions to identify agreement and disagreement
        agreement_level = self._calculate_agreement_level(opinions)
        
        # Formulate the party's stance
        party_stance = self.party.formulate_party_stance(legislation_text)
        
        return {
            "party_name": self.party.party_name,
            "opinions": opinions,
            "agreement_level": agreement_level,
            "party_stance": party_stance
        }
    
    def _calculate_agreement_level(self, opinions: List[Dict[str, str]]) -> str:
        """
        Calculate the level of agreement within the party.
        
        Args:
            opinions: A list of dictionaries containing politician names and their opinions
            
        Returns:
            A string indicating the level of agreement
        """
        # This is a simplified implementation
        # In a real system, you would use NLP to analyze the opinions
        
        # Count positive and negative opinions
        positive_count = 0
        negative_count = 0
        
        for opinion in opinions:
            text = opinion["opinion"].lower()
            
            # Simple keyword-based analysis
            if any(word in text for word in ["support", "agree", "favor", "positive", "good", "beneficial"]):
                positive_count = 1
            elif any(word in text for word in ["oppose", "disagree", "against", "negative", "bad", "harmful"]):
                negative_count = 1
        
        # Determine agreement level
        total_opinions = len(opinions)
        if total_opinions == 0:
            return "No opinions"
        
        positive_percentage = positive_count / total_opinions * 100
        negative_percentage = negative_count / total_opinions * 100
        
        if positive_percentage >= 80:
            return "Strong agreement"
        elif positive_percentage >= 60:
            return "Moderate agreement"
        elif positive_percentage >= 40:
            return "Mixed opinions"
        elif positive_percentage >= 20:
            return "Moderate disagreement"
        else:
            return "Strong disagreement"