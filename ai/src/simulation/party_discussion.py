from typing import List, Dict, TypedDict, Annotated
from dataclasses import dataclass
from langgraph.graph import StateGraph, END
import operator
try:
    from ..utilities.prompt_manager import PromptManager
except ImportError:
    # Fallback for different import contexts
    from ai.src.utilities.prompt_manager import PromptManager

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
        self.prompt_manager = PromptManager()
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
        print(f"\n=== Gathering opinions in party {state['party_name']} ===")
        
        opinions = {}
        for politician in self.party.politicians:
            prompt = self.prompt_manager.format_prompt(
                'simulation',
                'party_discussion.gather_opinions_prompt',
                legislation_text=state['legislation_text'],
                politician_name=politician.name
            )
            
            response = politician.answer_question(prompt)
            opinions[politician.name] = response
            print(f"\n{politician.name}: {response}")
        
        state['individual_opinions'] = opinions
        return state
    
    def _conduct_debate(self, state: DiscussionState) -> DiscussionState:
        """Node: Politicians respond to each other's opinions"""
        print(f"\n=== Debate in party {state['party_name']} ===")
        
        debate_points = []
        opinions_text = "\n".join([f"{name}: {opinion}" 
                                  for name, opinion in state['individual_opinions'].items()])
        
        # Each politician can respond to others
        for politician in self.party.politicians:
            prompt = self.prompt_manager.format_prompt(
                'simulation',
                'party_discussion.conduct_debate_prompt',
                opinions_text=opinions_text,
                politician_name=politician.name
            )
            
            response = politician.answer_question(prompt)
            debate_points.append(f"{politician.name}: {response}")
            print(f"\n{politician.name}: {response}")
        
        state['debate_summary'] = "\n".join(debate_points)
        return state
    
    def _formulate_position(self, state: DiscussionState) -> DiscussionState:
        """Node: Party leader formulates final position"""
        print(f"\n=== Formulating party position for {state['party_name']} ===")
        
        # Combine all discussion points
        full_discussion = f"Initial opinions:\n{chr(10).join([f'{k}: {v}' for k,v in state['individual_opinions'].items()])}\n\nDebate:\n{state['debate_summary']}"
        
        prompt = self.prompt_manager.format_prompt(
            'simulation',
            'party_discussion.formulate_position_prompt',
            party_name=state['party_name'],
            legislation_text=state['legislation_text'],
            full_discussion=full_discussion
        )
        
        response = self.party.answer_question(prompt)
        print(f"\nParty position: {response}")
        
        # Parse response
        state['final_position'] = response
        state['supports'] = "SUPPORTS" in response and "NOT SUPPORT" not in response
        
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
            if ("support" in opinion_lower and "not support" not in opinion_lower) or "i support" in opinion_lower:
                individual_positions[name] = "For"
            else:
                individual_positions[name] = "Against"
        
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
        print(f"PARTY DISCUSSION: {party.name}")
        print(f"{'='*60}")
        
        discussion = PartyDiscussion(party)
        position = discussion.conduct_discussion(legislation_text)
        positions[party.name] = position
        
        print(f"\nSummary for {party.name}:")
        print(f"  Position: {'SUPPORTS' if position.supports_legislation else 'DOES NOT SUPPORT'}")
        print(f"  Votes: For={sum(1 for v in position.individual_opinions.values() if v=='For')}, "
              f"Against={sum(1 for v in position.individual_opinions.values() if v=='Against')}")
    
    return positions
