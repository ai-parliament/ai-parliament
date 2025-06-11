from typing import List, Dict, Any
from ..agents.party_agent import PartyAgent

class InterPartyDebate:
    """
    Simulates debates between parties.
    """
    def __init__(self, parties: List[PartyAgent]):
        """
        Initialize an inter-party debate.
        
        Args:
            parties: A list of party agents
        """
        self.parties = parties
    
    def conduct_debate(self, legislation_text: str, party_stances: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Conduct a debate between parties about a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            party_stances: A dictionary mapping party names to their stances
            
        Returns:
            A dictionary containing the results of the debate
        """
        # Create a summary of all party stances
        stances_summary = "\n\n".join([
            f"{party_name}:\n{data['party_stance']}"
            for party_name, data in party_stances.items()
        ])
        
        debate_rounds = []
        
        # First round: Each party responds to other parties' stances
        round_1_responses = {}
        
        for party in self.parties:
            prompt = f"""
            Proposed legislation: {legislation_text}
            
            Here are the stances of all parties on this legislation:
            {stances_summary}
            
            As the leader of {party.party_name}, respond to the other parties' positions.
            Try to persuade them to align with your party's stance.
            """
            
            response = party.answer_question(prompt)
            round_1_responses[party.party_name] = response
        
        debate_rounds.append({
            "round": 1,
            "responses": round_1_responses
        })
        
        # Second round: Each party responds to the first round
        round_1_summary = "\n\n".join([
            f"{party_name}:\n{response}"
            for party_name, response in round_1_responses.items()
        ])
        
        round_2_responses = {}
        
        for party in self.parties:
            prompt = f"""
            Proposed legislation: {legislation_text}
            
            First round of debate:
            {round_1_summary}
            
            As the leader of {party.party_name}, respond to the arguments made in the first round.
            Address specific points raised by other parties and defend your position.
            """
            
            response = party.answer_question(prompt)
            round_2_responses[party.party_name] = response
        
        debate_rounds.append({
            "round": 2,
            "responses": round_2_responses
        })
        
        # Final round: Each party makes a closing statement
        round_2_summary = "\n\n".join([
            f"{party_name}:\n{response}"
            for party_name, response in round_2_responses.items()
        ])
        
        closing_statements = {}
        
        for party in self.parties:
            prompt = f"""
            Proposed legislation: {legislation_text}
            
            After two rounds of debate, make a closing statement as the leader of {party.party_name}.
            Summarize your position, address key counterarguments, and make a final appeal.
            Keep it concise and persuasive.
            """
            
            response = party.answer_question(prompt)
            closing_statements[party.party_name] = response
        
        debate_rounds.append({
            "round": 3,
            "responses": closing_statements
        })
        
        return {
            "legislation_text": legislation_text,
            "party_stances": party_stances,
            "debate_rounds": debate_rounds,
            "closing_statements": closing_statements
        }