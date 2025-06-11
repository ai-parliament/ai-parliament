from typing import List, Dict, Any
from ..agents.party_agent import PartyAgent

class VotingSystem:
    """
    Determines if the legislation passes based on party votes.
    """
    def __init__(self, parties: List[PartyAgent]):
        """
        Initialize a voting system.
        
        Args:
            parties: A list of party agents
        """
        self.parties = parties
    
    def conduct_vote(self, legislation_text: str, debate_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct a vote on a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            debate_results: The results of the inter-party debate
            
        Returns:
            A dictionary containing the results of the vote
        """
        voting_results = {}
        total_votes = 0
        votes_in_favor = 0
        
        # Each party votes based on their stance and the debate
        for party in self.parties:
            # Determine the number of votes (equal to the number of politicians)
            num_votes = len(party.politicians)
            total_votes = num_votes
            
            # Get the closing statement from the debate
            closing_statement = debate_results["closing_statements"].get(party.party_name, "")
            
            # Determine if the party is in favor or against
            prompt = f"""
            Based on your party's stance and the inter-party debate, 
            will {party.party_name} vote in favor of or against the following legislation?
            
            Legislation: {legislation_text}
            
            Your closing statement: {closing_statement}
            
            Answer with 'in favor' or 'against' and a brief explanation.
            """
            
            response = party.answer_question(prompt)
            
            # Parse the response to determine the vote
            vote_in_favor = "in favor" in response.lower()
            
            if vote_in_favor:
                votes_in_favor = num_votes
            
            voting_results[party.party_name] = {
                "vote": "in favor" if vote_in_favor else "against",
                "explanation": response,
                "num_votes": num_votes
            }
        
        # Determine if the legislation passes
        legislation_passes = votes_in_favor > total_votes / 2
        
        return {
            "legislation_text": legislation_text,
            "party_votes": voting_results,
            "total_votes": total_votes,
            "votes_in_favor": votes_in_favor,
            "legislation_passes": legislation_passes
        }
    
    def generate_voting_summary(self, voting_results: Dict[str, Any]) -> str:
        """
        Generate a summary of the voting results.
        
        Args:
            voting_results: The results of the vote
            
        Returns:
            A summary of the voting results
        """
        legislation_text = voting_results["legislation_text"]
        total_votes = voting_results["total_votes"]
        votes_in_favor = voting_results["votes_in_favor"]
        legislation_passes = voting_results["legislation_passes"]
        party_votes = voting_results["party_votes"]
        
        # Format party votes
        party_votes_formatted = "\n".join([
            f"- {party_name}: {data['vote']} ({data['num_votes']} votes)"
            for party_name, data in party_votes.items()
        ])
        
        summary = f"""
        Voting Results for Legislation:
        {legislation_text}
        
        Total votes: {total_votes}
        Votes in favor: {votes_in_favor} ({votes_in_favor/total_votes*100:.1f}%)
        Votes against: {total_votes - votes_in_favor} ({(total_votes - votes_in_favor)/total_votes*100:.1f}%)
        
        Result: The legislation {'passes' if legislation_passes else 'fails'}.
        
        Party votes:
        {party_votes_formatted}
        
        Explanations:
        """
        
        for party_name, data in party_votes.items():
            summary = f"\n{party_name}: {data['explanation']}"
        
        return summary