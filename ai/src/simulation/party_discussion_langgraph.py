"""
Party Discussion Module using LangGraph
Handles internal party deliberations with better state management
"""

from typing import List, Dict, TypedDict, Annotated
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
import operator

@dataclass
class PartyPosition:
    """Final position of the party on a piece of legislation"""
    party_name: str
    supports_legislation: bool
    main_arguments: List[str]
    individual_opinions: Dict[str, str]


class DiscussionState(TypedDict):
    """State for the party discussion workflow"""
    party_name: str
    legislation_text: str
    individual_opinions: Dict[str, str]
    debate_summary: str
    final_position: str
    supports: bool
    arguments: List[str]


class PartyDiscussion:
    """Manages internal party discussion using LangGraph"""
    
    def __init__(self, party_agent):
        self.party = party_agent
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create the LangGraph workflow for party discussion"""
        workflow = StateGraph(DiscussionState)
        
        # Add nodes
        workflow.add_node("gather_opinions", self._gather_opinions)
        workflow.add_node("conduct_debate", self._conduct_debate)
        workflow.add_node("formulate_position", self._formulate_position)
        
        # Add edges
        workflow.set_entry_point("gather_opinions")
        workflow.add_edge("gather_opinions", "conduct_debate")
        workflow.add_edge("conduct_debate", "formulate_position")
        workflow.add_edge("formulate_position", END)
        
        return workflow.compile()
    
    def _gather_opinions(self, state: DiscussionState) -> DiscussionState:
        """Node: Gather initial opinions from each politician"""
        print(f"\n=== Zbieranie opinii w partii {state['party_name']} ===")
        
        opinions = {}
        for politician in self.party.politicians:
            prompt = f"""
            Projekt ustawy: {state['legislation_text']}
            
            Jako {politician.name}, wyraź swoją opinię (2-3 zdania).
            Zacznij od "POPIERAM" lub "NIE POPIERAM", a następnie podaj uzasadnienie.
            """
            
            response = politician.answer_question(prompt)
            opinions[politician.name] = response
            print(f"\n{politician.name}: {response}")
        
        state['individual_opinions'] = opinions
        return state
    
    def _conduct_debate(self, state: DiscussionState) -> DiscussionState:
        """Node: Politicians respond to each other's opinions"""
        print(f"\n=== Debata w partii {state['party_name']} ===")
        
        debate_points = []
        opinions_text = "\n".join([f"{name}: {opinion}" 
                                  for name, opinion in state['individual_opinions'].items()])
        
        # Each politician can respond to others
        for politician in self.party.politicians:
            prompt = f"""
            Opinie kolegów z partii o ustawie:
            {opinions_text}
            
            Jako {politician.name}, krótko (1-2 zdania) odnieś się do dyskusji.
            Możesz podtrzymać swoje zdanie lub je zmienić.
            """
            
            response = politician.answer_question(prompt)
            debate_points.append(f"{politician.name}: {response}")
            print(f"\n{politician.name}: {response}")
        
        state['debate_summary'] = "\n".join(debate_points)
        return state
    
    def _formulate_position(self, state: DiscussionState) -> DiscussionState:
        """Node: Party leader formulates final position"""
        print(f"\n=== Formułowanie stanowiska partii {state['party_name']} ===")
        
        # Combine all discussion points
        full_discussion = f"Opinie początkowe:\n{chr(10).join([f'{k}: {v}' for k,v in state['individual_opinions'].items()])}\n\nDebata:\n{state['debate_summary']}"
        
        prompt = f"""
        Jako lider partii {state['party_name']}, podsumuj dyskusję o ustawie:
        {state['legislation_text']}
        
        {full_discussion}
        
        Odpowiedz w formacie:
        STANOWISKO: [POPIERA lub NIE POPIERA]
        ARGUMENT 1: [główny argument]
        ARGUMENT 2: [drugi argument]
        ARGUMENT 3: [trzeci argument]
        """
        
        response = self.party.answer_question(prompt)
        print(f"\nStanowisko partii: {response}")
        
        # Parse response
        state['final_position'] = response
        state['supports'] = "POPIERA" in response and "NIE POPIERA" not in response
        
        # Extract arguments
        arguments = []
        for line in response.split('\n'):
            if line.strip().startswith('ARGUMENT'):
                arguments.append(line.split(':', 1)[1].strip())
        
        state['arguments'] = arguments[:3]  # Take max 3 arguments
        return state
    
    def conduct_discussion(self, legislation_text: str) -> PartyPosition:
        """Run the discussion workflow and return party position"""
        
        # Initial state
        initial_state = {
            "party_name": self.party.name,
            "legislation_text": legislation_text,
            "individual_opinions": {},
            "debate_summary": "",
            "final_position": "",
            "supports": False,
            "arguments": []
        }
        
        # Run workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Determine individual positions from their initial opinions
        individual_positions = {}
        for name, opinion in final_state['individual_opinions'].items():
            # More robust parsing
            opinion_lower = opinion.lower()
            if "popieram" in opinion_lower and "nie popieram" not in opinion_lower:
                individual_positions[name] = "Za"
            else:
                individual_positions[name] = "Przeciw"
        
        # Create and return PartyPosition
        return PartyPosition(
            party_name=self.party.name,
            supports_legislation=final_state['supports'],
            main_arguments=final_state['arguments'],
            individual_opinions=individual_positions
        )


def discuss_legislation(parties: List, legislation_text: str) -> Dict[str, PartyPosition]:
    """
    Have multiple parties discuss legislation internally using LangGraph
    
    Args:
        parties: List of PartyAgent instances
        legislation_text: The legislation to discuss
        
    Returns:
        Dictionary mapping party names to their positions
    """
    positions = {}
    
    for party in parties:
        print(f"\n{'='*60}")
        print(f"DYSKUSJA W PARTII: {party.name}")
        print(f"{'='*60}")
        
        discussion = PartyDiscussion(party)
        position = discussion.conduct_discussion(legislation_text)
        positions[party.name] = position
        
        print(f"\nPodsumowanie {party.name}:")
        print(f"  Stanowisko: {'POPIERA' if position.supports_legislation else 'NIE POPIERA'}")
        print(f"  Głosy: Za={sum(1 for v in position.individual_opinions.values() if v=='Za')}, "
              f"Przeciw={sum(1 for v in position.individual_opinions.values() if v=='Przeciw')}")
    
    return positions