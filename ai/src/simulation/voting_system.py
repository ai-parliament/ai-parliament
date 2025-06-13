from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict
from langsmith import traceable
try:
    from ..utilities.prompt_manager import PromptManager
except ImportError:
    # Fallback for different import contexts
    from ai.src.utilities.prompt_manager import PromptManager


@dataclass
class Vote:
    """Individual vote"""
    politician_name: str
    party_name: str
    vote: str  # "For", "Against", "Abstain"
    
    
@dataclass
class VotingResult:
    """Result of voting"""
    total_for: int
    total_against: int
    total_abstain: int
    passed: bool
    votes_by_party: Dict[str, Dict[str, int]]
    individual_votes: List[Vote]
    
    def __str__(self):
        status = "PASSED ✓" if self.passed else "REJECTED"
        return f"For: {self.total_for}, Against: {self.total_against}, Abstained: {self.total_abstain} - Bill {status}"


class VotingSystem:
    """Manages the voting process"""
    
    def __init__(self, parties: List, party_positions: Dict[str, bool]):
        """
        Initialize voting system
        
        Args:
            parties: List of PartyAgent instances
            party_positions: Dict mapping party names to their positions (True = support)
        """
        self.parties = parties
        self.party_positions = party_positions
        self.votes: List[Vote] = []
        self.prompt_manager = PromptManager()

    @traceable(name="Conduct Voting")    
    def conduct_vote(self, allow_dissent: bool = True, dissent_probability: float = 0.1) -> VotingResult:
        """
        Conduct the actual vote
        
        Args:
            allow_dissent: Whether politicians can vote against party line
            dissent_probability: Probability of voting against party line
            
        Returns:
            VotingResult with detailed voting information
        """
        print("\n" + "="*60)
        print("VOTING")
        print("="*60)
        
        for party in self.parties:
            print(f"\n--- {party.name} ---")
            party_supports = self.party_positions.get(party.name, False)
            
            for politician in party.politicians:
                # Determine individual vote
                vote = self._determine_vote(
                    politician, 
                    party_supports,
                    allow_dissent,
                    dissent_probability
                )
                
                self.votes.append(Vote(
                    politician_name=politician.name,
                    party_name=party.name,
                    vote=vote
                ))
                
                print(f"{politician.name}: {vote}")
        
        # Calculate results
        result = self._calculate_results()
        
        # Display summary
        self._display_summary(result)
        
        return result
        
    def _determine_vote(self, politician, party_supports: bool, 
                       allow_dissent: bool, dissent_probability: float) -> str:
        """Determine how a politician votes"""
        
        if not allow_dissent:
            # Vote strictly along party lines
            return "For" if party_supports else "Against"
        
        # Ask politician for their personal stance
        party_position = 'SUPPORT' if party_supports else 'OPPOSE'
        
        prompt = self.prompt_manager.format_prompt(
            'simulation',
            'voting_system.vote_prompt',
            politician_name=politician.name,
            party_position=party_position
        )
        
        response = politician.answer_question(prompt).strip().upper()
        
        # Parse response
        if "FOR" in response and "AGAINST" not in response:
            return "For"
        elif "AGAINST" in response:
            return "Against"
        elif "ABSTAIN" in response:
            return "Abstain"
        else:
            # Default to party line if unclear
            return "For" if party_supports else "Against"
            
    def _calculate_results(self) -> VotingResult:
        """Calculate voting results"""
        total_for = sum(1 for v in self.votes if v.vote == "For")
        total_against = sum(1 for v in self.votes if v.vote == "Against")
        total_abstain = sum(1 for v in self.votes if v.vote == "Abstain")
        
        # Calculate by party
        votes_by_party = defaultdict(lambda: {"For": 0, "Against": 0, "Abstain": 0})
        for vote in self.votes:
            votes_by_party[vote.party_name][vote.vote] += 1
            
        # Determine if passed (simple majority)
        passed = total_for > total_against
        
        return VotingResult(
            total_for=total_for,
            total_against=total_against,
            total_abstain=total_abstain,
            passed=passed,
            votes_by_party=dict(votes_by_party),
            individual_votes=self.votes
        )
        
    def _display_summary(self, result: VotingResult):
        """Display voting summary"""
        print("\n" + "="*60)
        print("VOTING RESULTS")
        print("="*60)
        
        # Overall results
        print(f"\nOverall:")
        print(f"  For: {result.total_for}")
        print(f"  Against: {result.total_against}")
        print(f"  Abstained: {result.total_abstain}")
        
        # By party
        print("\nBy party:")
        for party_name, votes in result.votes_by_party.items():
            print(f"\n{party_name}:")
            print(f"  For: {votes['For']}")
            print(f"  Against: {votes['Against']}")
            print(f"  Abstained: {votes['Abstain']}")
            
            # Check for dissent
            expected_vote = "For" if self.party_positions.get(party_name, False) else "Against"
            dissent_count = len([v for v in result.individual_votes 
                               if v.party_name == party_name and v.vote != expected_vote])
            if dissent_count > 0:
                print(f"Votes against party line: {dissent_count}")
        
        # Final result
        print("\n" + "-"*60)
        print(f"RESULT: Bill {'PASSED ✓' if result.passed else 'REJECTED'}")
        print(f"({result.total_for} for, {result.total_against} against, {result.total_abstain} abstained)")


def simulate_voting(parties: List, party_positions: Dict[str, bool], 
                   allow_dissent: bool = True, dissent_probability: float = 0.1) -> VotingResult:
    """
    Simulate the voting process
    
    Args:
        parties: List of PartyAgent instances
        party_positions: Dict mapping party names to their positions
        allow_dissent: Whether politicians can vote against party line
        dissent_probability: Probability of dissent
        
    Returns:
        VotingResult with detailed voting information
    """
    voting_system = VotingSystem(parties, party_positions)
    return voting_system.conduct_vote(allow_dissent, dissent_probability)
