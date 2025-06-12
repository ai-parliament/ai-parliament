from .politician_agent import PoliticianAgent
from .party_agent import PartyAgent
from .supervisor_agent import SupervisorAgent
from typing import List, Dict, Any

class AgentLoader:
    """
    Loads biographical and political context data for each politician and party.
    Creates unique system prompts based on ideology, past votes, public statements, etc.
    """
    def __init__(self):
        """
        Initialize the agent loader.
        """
        self.parties = {}
        self.politicians = {}
    
    def load_party(self, party_name: str, party_acronym: str = "") -> PartyAgent:
        """
        Load a party agent with context data.
        
        Args:
            party_name: The name of the party
            party_acronym: The acronym of the party
            
        Returns:
            A configured party agent
        """
        # Check if we already have this party
        if party_name in self.parties:
            return self.parties[party_name]
        
        # Create the party agent
        party_agent = PartyAgent(name=party_name, acronym=party_acronym)
        
        # Store the party agent
        self.parties[party_name] = party_agent
        
        return party_agent
    
    def load_politician(self, full_name: str, party_name: str = "", role: str = "") -> PoliticianAgent:
        """
        Load a politician agent with context data.
        
        Args:
            full_name: The full name of the politician
            party_name: The name of the party the politician belongs to
            role: The role of the politician
            
        Returns:
            A configured politician agent
        """
        # Check if we already have this politician
        if full_name in self.politicians:
            return self.politicians[full_name]
        
        # Split the name
        parts = full_name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        
        # Create the politician agent
        politician_agent = PoliticianAgent(
            first_name=first_name,
            last_name=last_name,
            party_name=party_name
        )
        
        # Set the role if provided
        if role:
            politician_agent.role = role
        
        # Store the politician agent
        self.politicians[full_name] = politician_agent
        
        return politician_agent
    
    def add_politician_to_party(self, politician_name: str, party_name: str, role: str = ""):
        """
        Add a politician to a party.
        
        Args:
            politician_name: The name of the politician
            party_name: The name of the party
            role: The role of the politician in the party
        """
        # Load the party if it doesn't exist
        if party_name not in self.parties:
            self.load_party(party_name)
        
        party = self.parties[party_name]
        
        # Check if the politician is already in the party
        for politician in party.politicians:
            if politician.full_name == politician_name:
                # Update the role if provided
                if role:
                    politician.role = role
                return
        
        # Load the politician if they don't exist
        if politician_name not in self.politicians:
            self.load_politician(politician_name, party_name, role)
        
        politician = self.politicians[politician_name]
        
        # Add the politician to the party
        party.add_politician(politician_name, role)
    
    def create_simulation(self, party_names: List[str], politicians_per_party: Dict[str, List[Dict[str, str]]]) -> SupervisorAgent:
        """
        Create a simulation with the specified parties and politicians.
        
        Args:
            party_names: A list of party names
            politicians_per_party: A dictionary mapping party names to lists of politician dictionaries
                                  (each containing 'name' and optionally 'role')
            
        Returns:
            A configured supervisor agent
        """
        supervisor = SupervisorAgent()
        
        for party_name in party_names:
            # Extract the acronym if provided (format: "Party Name (ACRONYM)")
            acronym = ""
            if "(" in party_name and ")" in party_name:
                acronym_start = party_name.find("(") + 1
                acronym_end = party_name.find(")")
                acronym = party_name[acronym_start:acronym_end]
                party_name_clean = party_name[:acronym_start-1].strip()
            else:
                party_name_clean = party_name
            
            # Load the party
            party = self.load_party(party_name_clean, acronym)
            
            # Add politicians to the party
            if party_name in politicians_per_party:
                for politician_info in politicians_per_party[party_name]:
                    name = politician_info["name"]
                    role = politician_info.get("role", "")
                    self.add_politician_to_party(name, party_name_clean, role)
            
            # Add the party to the simulation
            supervisor.add_party(party)
        
        return supervisor
    
    def generate_legislation(self, topic: str) -> str:
        """
        Generate legislation text on a given topic.
        
        Args:
            topic: The topic of the legislation
            
        Returns:
            The generated legislation text
        """
        return topic
