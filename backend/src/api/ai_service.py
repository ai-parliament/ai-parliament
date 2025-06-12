from typing import List, Dict, Any
from src.ai.agents.agent_loader import AgentLoader
from src.ai.agents.supervisor_agent import SupervisorAgent
from src.ai.database.vector_db import VectorDatabase
from src.ai.simulation.party_discussion import PartyDiscussion
from src.ai.simulation.inter_party_debate import InterPartyDebate
from src.ai.simulation.voting_system import VotingSystem


class AIService:
    """
    Exposes AI functionality to the backend.
    """
    def __init__(self):
        """
        Initialize the AI service.
        """
        self.agent_loader = AgentLoader()
        # self.vector_db = VectorDatabase()
    
    def create_simulation(self, party_names: List[str], politicians_per_party: Dict[str, List[Dict[str, str]]]) -> Dict[str, Any]:
        """
        Create a simulation with the specified parties and politicians.
        
        Args:
            party_names: A list of party names
            politicians_per_party: A dictionary mapping party names to lists of politician dictionaries
                                  (each containing 'name' and optionally 'role')
            
        Returns:
            A dictionary containing the simulation configuration
        """
        supervisor = self.agent_loader.create_simulation(party_names, politicians_per_party)
        
        # Store the supervisor in the instance for later use
        self.supervisor = supervisor
        
        # Return the configuration
        return {
            "parties": [
                {
                    "name": party.party_name,
                    "acronym": party.party_acronym,
                    "politicians": [
                        {
                            "name": politician.full_name,
                            "role": politician.role
                        }
                        for politician in party.politicians
                    ]
                }
                for party in supervisor.parties
            ]
        }
    
    def generate_legislation(self, topic: str) -> str:
        """
        Generate legislation text on a given topic.
        
        Args:
            topic: The topic of the legislation
            
        Returns:
            The generated legislation text
        """
        legislation_text = self.agent_loader.generate_legislation(topic)
                
        return legislation_text
    
    def run_simulation(self, legislation_text: str) -> Dict[str, Any]:
        """
        Run a simulation with the specified legislation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the simulation
        """
        if not hasattr(self, 'supervisor'):
            return {"error": "No simulation has been created yet."}
        
        # Run the full simulation
        results = self.supervisor.run_full_simulation(legislation_text)
        
        return results
    
    def run_intra_party_deliberation(self, legislation_text: str) -> Dict[str, Any]:
        """
        Run the intra-party deliberation phase.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the deliberation
        """
        if not hasattr(self, 'supervisor'):
            return {"error": "No simulation has been created yet."}
        
        self.supervisor.set_legislation(legislation_text)
        results = self.supervisor.run_intra_party_deliberation()
        
        return {
            "legislation_text": legislation_text,
            "party_stances": results
        }
    
    def run_inter_party_debate(self, legislation_text: str) -> Dict[str, Any]:
        """
        Run the inter-party debate phase.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the debate
        """
        if not hasattr(self, 'supervisor'):
            return {"error": "No simulation has been created yet."}
        
        if "intra_party_deliberation" not in self.supervisor.simulation_results:
            self.run_intra_party_deliberation(legislation_text)
        
        results = self.supervisor.run_inter_party_debate()
        
        # Get the debate speeches if available
        debate_speeches = []
        if "inter_party_debate" in self.supervisor.simulation_results:
            debate_speeches = self.supervisor.simulation_results["inter_party_debate"].get("debate_speeches", [])
        
        return {
            "legislation_text": legislation_text,
            "debate_results": results,
            "debate_speeches": debate_speeches
        }
    
    def run_voting(self, legislation_text: str) -> Dict[str, Any]:
        """
        Run the voting phase.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the voting
        """
        if not hasattr(self, 'supervisor'):
            return {"error": "No simulation has been created yet."}
        
        if "inter_party_debate" not in self.supervisor.simulation_results:
            self.run_inter_party_debate(legislation_text)
        
        results = self.supervisor.run_voting()
        
        return {
            "legislation_text": legislation_text,
            "voting_results": results
        }
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the simulation results.
        
        Returns:
            A dictionary containing a summary of the simulation results
        """
        if not hasattr(self, 'supervisor'):
            return {"error": "No simulation has been created yet."}
        
        return self.supervisor.get_simulation_summary()
