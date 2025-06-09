"""
Inter-Party Debate Module
Handles debates between different political parties
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
import random


@dataclass
class DebateArgument:
    """Single argument in a debate"""
    party_name: str
    speaker_name: str
    argument: str
    is_supporting: bool
    responding_to: Optional[str] = None


class InterPartyDebate:
    """Manages debates between political parties"""
    
    def __init__(self, parties: List, legislation_text: str):
        self.parties = parties
        self.legislation_text = legislation_text
        self.debate_history: List[DebateArgument] = []
        
    def conduct_debate(self, rounds: int = 2) -> List[DebateArgument]:
        """
        Conduct inter-party debate
        
        Args:
            rounds: Number of debate rounds
            
        Returns:
            List of debate arguments
        """
        print("\n" + "="*60)
        print("DEBATA MIĘDZYPARTYJNA")
        print("="*60)
        
        # First round - opening statements
        print("\n--- RUNDA 1: Stanowiska wstępne ---")
        for party in self.parties:
            self._party_opening_statement(party)
        
        # Subsequent rounds - responses and rebuttals
        for round_num in range(2, rounds + 1):
            print(f"\n--- RUNDA {round_num}: Odpowiedzi i kontrargumenty ---")
            
            # Each party responds to previous arguments
            for party in self.parties:
                self._party_response(party, round_num)
        
        # Final statements
        print("\n--- STANOWISKA KOŃCOWE ---")
        for party in self.parties:
            self._party_closing_statement(party)
            
        return self.debate_history
    
    def _party_opening_statement(self, party):
        """Generate opening statement for a party"""
        # Select representative speaker
        speaker = random.choice(party.politicians)
        
        prompt = f"""
        Jako {speaker.name} z partii {party.name}, przedstaw stanowisko partii
        w sprawie ustawy:
        {self.legislation_text}
        
        Skoncentruj się na głównych argumentach partii (2-3 zdania).
        Rozpocznij od jasnego stwierdzenia czy popierasz czy odrzucasz ustawę.
        """
        
        response = speaker.answer_question(prompt)
        is_supporting = "popieram" in response.lower() and "nie popieram" not in response.lower()
        
        argument = DebateArgument(
            party_name=party.name,
            speaker_name=speaker.name,
            argument=response,
            is_supporting=is_supporting
        )
        
        self.debate_history.append(argument)
        print(f"\n{speaker.name} ({party.name}):")
        print(response)
        
    def _party_response(self, party, round_num):
        """Generate response to other parties' arguments"""
        # Get opposing arguments
        opposing_arguments = [
            arg for arg in self.debate_history 
            if arg.party_name != party.name
        ]
        
        if not opposing_arguments:
            return
            
        # Select argument to respond to
        target_argument = random.choice(opposing_arguments[-len(self.parties):])
        
        # Select speaker
        speaker = random.choice(party.politicians)
        
        # Build context of previous arguments
        recent_arguments = "\n".join([
            f"{arg.speaker_name} ({arg.party_name}): {arg.argument}"
            for arg in opposing_arguments[-3:]
        ])
        
        prompt = f"""
        Jako {speaker.name} z partii {party.name}, odpowiedz na argumenty innych partii.
        
        Ostatnie argumenty w debacie:
        {recent_arguments}
        
        Szczególnie odnieś się do argumentu {target_argument.speaker_name} ({target_argument.party_name}).
        Odpowiedź powinna być konkretna i merytoryczna (2-3 zdania).
        """
        
        response = speaker.answer_question(prompt)
        
        argument = DebateArgument(
            party_name=party.name,
            speaker_name=speaker.name,
            argument=response,
            is_supporting=self._get_party_stance(party),
            responding_to=f"{target_argument.speaker_name} ({target_argument.party_name})"
        )
        
        self.debate_history.append(argument)
        print(f"\n{speaker.name} ({party.name}) → {target_argument.speaker_name}:")
        print(response)
        
    def _party_closing_statement(self, party):
        """Generate closing statement for a party"""
        prompt = f"""
        Jako lider partii {party.name}, podsumuj debatę na temat ustawy:
        {self.legislation_text}
        
        Uwzględnij główne argumenty które padły w debacie.
        Potwierdź ostateczne stanowisko partii (1-2 zdania).
        Zakończ jasnym stwierdzeniem: "Partia {party.name} GŁOSUJE ZA/PRZECIW ustawie."
        """
        
        response = party.answer_question(prompt)
        is_supporting = "głosuje za" in response.lower()
        
        argument = DebateArgument(
            party_name=party.name,
            speaker_name=f"Lider {party.name}",
            argument=response,
            is_supporting=is_supporting
        )
        
        self.debate_history.append(argument)
        print(f"\n{party.name} - Stanowisko końcowe:")
        print(response)
        
    def _get_party_stance(self, party) -> bool:
        """Get party's stance from previous arguments"""
        party_args = [arg for arg in self.debate_history if arg.party_name == party.name]
        if party_args:
            return party_args[-1].is_supporting
        return False
    
    def get_final_positions(self) -> Dict[str, bool]:
        """Get final position of each party after debate"""
        positions = {}
        
        for party in self.parties:
            # Get last argument from party
            party_args = [arg for arg in self.debate_history if arg.party_name == party.name]
            if party_args:
                positions[party.name] = party_args[-1].is_supporting
            else:
                positions[party.name] = False
                
        return positions


def conduct_inter_party_debate(parties: List, legislation_text: str, rounds: int = 2) -> Dict[str, bool]:
    """
    Conduct debate between parties and return their final positions
    
    Args:
        parties: List of PartyAgent instances
        legislation_text: The legislation being debated
        rounds: Number of debate rounds
        
    Returns:
        Dictionary mapping party names to their final positions (True = support, False = oppose)
    """
    debate = InterPartyDebate(parties, legislation_text)
    debate.conduct_debate(rounds)
    return debate.get_final_positions()