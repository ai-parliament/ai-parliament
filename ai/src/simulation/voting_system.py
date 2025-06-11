"""
Voting System Module
Handles the voting process and determines if legislation passes
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Vote:
    """Individual vote"""
    politician_name: str
    party_name: str
    vote: str  # "Za", "Przeciw", "Wstrzymuje się"
    
    
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
        status = "PRZYJĘTA ✓" if self.passed else "ODRZUCONA ✗"
        return f"Za: {self.total_for}, Przeciw: {self.total_against}, Wstrzymało się: {self.total_abstain} - Ustawa {status}"


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
        print("GŁOSOWANIE")
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
            return "Za" if party_supports else "Przeciw"
        
        # Ask politician for their personal stance
        prompt = f"""
        Jako {politician.name}, musisz teraz zagłosować.
        Oficjalne stanowisko twojej partii to: {'POPARCIE' if party_supports else 'SPRZECIW'}.
        
        Czy głosujesz zgodnie z linią partii, czy może masz inne zdanie?
        Odpowiedz TYLKO jednym słowem: ZA, PRZECIW lub WSTRZYMUJĘ_SIĘ
        """
        
        response = politician.answer_question(prompt).strip().upper()
        
        # Parse response
        if "ZA" in response and "PRZECIW" not in response:
            return "Za"
        elif "PRZECIW" in response:
            return "Przeciw"
        elif "WSTRZYM" in response:
            return "Wstrzymuje się"
        else:
            # Default to party line if unclear
            return "Za" if party_supports else "Przeciw"
            
    def _calculate_results(self) -> VotingResult:
        """Calculate voting results"""
        total_for = sum(1 for v in self.votes if v.vote == "Za")
        total_against = sum(1 for v in self.votes if v.vote == "Przeciw")
        total_abstain = sum(1 for v in self.votes if v.vote == "Wstrzymuje się")
        
        # Calculate by party
        votes_by_party = defaultdict(lambda: {"Za": 0, "Przeciw": 0, "Wstrzymuje się": 0})
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
        print("WYNIKI GŁOSOWANIA")
        print("="*60)
        
        # Overall results
        print(f"\nOgółem:")
        print(f"  Za: {result.total_for}")
        print(f"  Przeciw: {result.total_against}")
        print(f"  Wstrzymało się: {result.total_abstain}")
        
        # By party
        print("\nWedług partii:")
        for party_name, votes in result.votes_by_party.items():
            print(f"\n{party_name}:")
            print(f"  Za: {votes['Za']}")
            print(f"  Przeciw: {votes['Przeciw']}")
            print(f"  Wstrzymało się: {votes['Wstrzymuje się']}")
            
            # Check for dissent
            expected_vote = "Za" if self.party_positions.get(party_name, False) else "Przeciw"
            dissent_count = len([v for v in result.individual_votes 
                               if v.party_name == party_name and v.vote != expected_vote])
            if dissent_count > 0:
                print(f"  ⚠️  Głosów niezgodnych z linią partii: {dissent_count}")
        
        # Final result
        print("\n" + "-"*60)
        print(f"WYNIK: Ustawa {'PRZYJĘTA ✓' if result.passed else 'ODRZUCONA ✗'}")
        print(f"({result.total_for} za, {result.total_against} przeciw, {result.total_abstain} wstrzymało się)")


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