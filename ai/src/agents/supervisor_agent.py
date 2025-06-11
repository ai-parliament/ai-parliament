import os
from .base_agent import BaseAgent
from .party_agent import PartyAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from typing import List, Dict, Any

# Import the simulation modules
from ..simulation.party_discussion import discuss_legislation, PartyPosition
from ..simulation.inter_party_debate import conduct_inter_party_debate
from ..simulation.voting_system import simulate_voting

class SupervisorAgent(BaseAgent):
    """
    Agent that manages the coordination of the system and information flow.
    """
    def __init__(self):
        """
        Initialize a supervisor agent.
        """
        super().__init__()
        self.parties: List[PartyAgent] = []
        self.legislation_text = ""
        self.simulation_results = {}
        
        # Set up agent
        self.system_prompt = self._set_system_prompt()
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True
        )
    
    def add_party(self, party: PartyAgent):
        """
        Add a party to the simulation.
        
        Args:
            party: The party to add
        """
        self.parties.append(party)
        print(f"Added party: {party.party_name} to the simulation")
    
    def set_legislation(self, legislation_text: str):
        """
        Set the legislation text for the simulation.
        
        Args:
            legislation_text: The text of the legislation
        """
        self.legislation_text = legislation_text
    
    def run_intra_party_deliberation(self):
        """
        Run the intra-party deliberation phase using the party_discussion module.
        
        Returns:
            A dictionary containing the results of the deliberation
        """
        # Use the discuss_legislation function from party_discussion.py
        party_positions = discuss_legislation(self.parties, self.legislation_text)
        
        # Format results for compatibility with existing code
        party_stances = {}
        for party_name, position in party_positions.items():
            party_stances[party_name] = {
                "stance": f"{'SUPPORTS' if position.supports_legislation else 'DOES NOT SUPPORT'} the legislation.\nArguments: {', '.join(position.main_arguments)}",
                "opinions": position.individual_opinions,
                "supports": position.supports_legislation,
                "arguments": position.main_arguments
            }
        
        self.simulation_results["intra_party_deliberation"] = party_stances
        return party_stances
    
    def run_inter_party_debate(self):
        """
        Run the inter-party debate phase using the inter_party_debate module.
        
        Returns:
            A dictionary containing the results of the debate
        """
        if "intra_party_deliberation" not in self.simulation_results:
            self.run_intra_party_deliberation()
        
        # Use the conduct_inter_party_debate function from inter_party_debate.py
        party_positions = conduct_inter_party_debate(self.parties, self.legislation_text, rounds=2)
        
        # Store the results in a format compatible with the rest of the system
        debate_results = {}
        for party_name, supports_position in party_positions.items():
            stance = "SUPPORTS" if supports_position else "DOES NOT SUPPORT"
            debate_results[party_name] = f"The {party_name} party {stance} the legislation after the debate."
            
            # Update party positions in the intra-party results to reflect debate outcome
            if "intra_party_deliberation" in self.simulation_results and party_name in self.simulation_results["intra_party_deliberation"]:
                self.simulation_results["intra_party_deliberation"][party_name]["supports"] = supports_position
        
        self.simulation_results["inter_party_debate"] = {
            "party_positions": party_positions,
            "debate_summary": debate_results
        }
        
        # To maintain backward compatibility with tests, ensure debate_results is directly returnable
        return debate_results
    
    def run_voting(self):
        """
        Run the voting phase using the voting_system module.
        
        Returns:
            A dictionary containing the results of the voting
        """
        if "inter_party_debate" not in self.simulation_results:
            self.run_inter_party_debate()
        
        # Get party positions from the debate results
        party_positions = {}
        if "inter_party_debate" in self.simulation_results and "party_positions" in self.simulation_results["inter_party_debate"]:
            party_positions = self.simulation_results["inter_party_debate"]["party_positions"]
        else:
            # Fall back to intra-party deliberation results if needed
            for party_name, data in self.simulation_results.get("intra_party_deliberation", {}).items():
                party_positions[party_name] = data.get("supports", False)
        
        # Use the simulate_voting function from voting_system.py
        voting_result = simulate_voting(self.parties, party_positions)
        
        # Format results for compatibility with existing code
        party_votes = {}
        for party in self.parties:
            party_votes_count = {
                "For": 0,
                "Against": 0,
                "Abstain": 0
            }
            
            # Count votes by party
            if party.name in voting_result.votes_by_party:
                party_votes_count = voting_result.votes_by_party[party.name]
            
            # Determine overall party vote based on majority
            if party_votes_count["For"] > party_votes_count["Against"]:
                party_vote = "in favor"
            else:
                party_vote = "against"
                
            party_votes[party.name] = {
                "vote": party_vote,
                "explanation": f"The {party.name} party voted {party_vote} with {party_votes_count['For']} votes for, {party_votes_count['Against']} against, and {party_votes_count['Abstain']} abstaining.",
                "num_votes": len(party.politicians),
                "detailed_votes": party_votes_count
            }
        
        # Maintain expected structure for compatibility with tests
        voting_results = {
            "party_votes": party_votes,
            "total_votes": voting_result.total_for + voting_result.total_against + voting_result.total_abstain,
            "votes_in_favor": voting_result.total_for,
            "legislation_passes": voting_result.passed
        }
        
        # Add additional detailed information
        voting_results.update({
            "votes_against": voting_result.total_against,
            "abstained": voting_result.total_abstain,
            "individual_votes": [vars(vote) for vote in voting_result.individual_votes]
        })
        
        self.simulation_results["voting"] = voting_results
        return voting_results
    
    def run_full_simulation(self, legislation_text: str):
        """
        Run the full simulation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A dictionary containing the results of the simulation
        """
        self.set_legislation(legislation_text)
        self.run_intra_party_deliberation()
        self.run_inter_party_debate()
        self.run_voting()
        
        return self.get_simulation_summary()
    
    def get_simulation_summary(self):
        """
        Get a summary of the simulation results.
        
        Returns:
            A dictionary containing a summary of the simulation results
        """
        if "voting" not in self.simulation_results:
            return {"error": "Simulation has not been completed yet."}
        
        voting_results = self.simulation_results["voting"]
        
        # Gather party arguments from the intra-party deliberation phase
        party_arguments = {}
        for party_name, data in self.simulation_results.get("intra_party_deliberation", {}).items():
            if "arguments" in data:
                party_arguments[party_name] = data["arguments"]
        
        # Prepare arguments text for the summary prompt
        party_args_text = ""
        for party_name, arguments in party_arguments.items():
            party_args_text += f"\n{party_name} main arguments:\n"
            for i, arg in enumerate(arguments, 1):
                party_args_text += f"- {arg}\n"
        
        summary_prompt = f"""
        Summarize the results of the parliamentary simulation on the following legislation:
        
        Legislation: {self.legislation_text}
        
        Voting results:
        - Total votes: {voting_results['total_votes']}
        - Votes in favor: {voting_results['votes_in_favor']}
        - Votes against: {voting_results.get('votes_against', 0)}
        - Abstained: {voting_results.get('abstained', 0)}
        - Legislation passes: {voting_results['legislation_passes']}
        
        Party votes:
        {self._format_party_votes(voting_results['party_votes'])}
        
        {party_args_text}
        
        Provide a concise summary of the simulation, including the key arguments from each party
        and why the legislation passed or failed.
        """
        
        response = self.answer_question(summary_prompt)
        
        return {
            "legislation_text": self.legislation_text,
            "voting_results": voting_results,
            "summary": response,
            "full_results": self.simulation_results
        }
    
    def _format_party_votes(self, party_votes):
        """
        Format the party votes for display.
        
        Args:
            party_votes: A dictionary containing the party votes
            
        Returns:
            A formatted string of party votes
        """
        formatted_votes = []
        
        for party_name, data in party_votes.items():
            basic_info = f"- {party_name}: {data['vote']} ({data['num_votes']} total members)"
            
            # Add detailed breakdown if available
            if 'detailed_votes' in data:
                detailed = data['detailed_votes']
                detailed_info = f" [For: {detailed.get('For', 0)}, Against: {detailed.get('Against', 0)}, Abstain: {detailed.get('Abstain', 0)}]"
                basic_info += detailed_info
                
            formatted_votes.append(basic_info)
            
        return "\n".join(formatted_votes)
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question as the supervisor.
        
        Args:
            question: The question to answer
            
        Returns:
            The supervisor's response
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=question)
        ]
        
        response = self.model(messages=messages)
        
        if isinstance(response, dict) and "output" in response:
            return response["output"]
        
        return response.content
    
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the supervisor agent.
        
        Returns:
            The system prompt as a string
        """
        return """
        You are the supervisor of a parliamentary simulation system.
        Your role is to oversee the decision-making process and provide objective analysis.
        
        You should:
        1. Maintain neutrality and objectivity
        2. Provide clear summaries of complex political processes
        3. Explain why certain decisions were made
        4. Highlight key arguments from different parties
        
        When responding, use a formal, analytical tone appropriate for political analysis.
        """
    
    def _get_all_tools(self) -> List:
        """
        Get all tools available to the supervisor agent.
        
        Returns:
            A list of tools
        """
        return []  # Supervisor doesn't need external tools
    
    def _setup_agent(self):
        """
        Set up the agent with the appropriate tools and prompt.
        
        Returns:
            The configured agent
        """
        langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        hub_client = Client(api_key=langsmith_api_key)
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        return create_tool_calling_agent(self.llm, self.tools, basic_prompt)

        # try:
        #     langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        #     if langsmith_api_key:
        #         hub_client = Client(api_key=langsmith_api_key)
        #         basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        #         return create_tool_calling_agent(self.llm, self.tools, basic_prompt)
        #     else:
        #         # Fallback if LANGSMITH_API_KEY is not available
        #         from langchain.agents import AgentType, initialize_agent
        #         return initialize_agent(
        #             tools=self.tools,
        #             llm=self.llm,
        #             agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        #             verbose=True
        #         )
        # except Exception:
        #     # Fallback if there's an error with LangSmith
        #     from langchain.agents import AgentType, initialize_agent
        #     return initialize_agent(
        #         tools=self.tools,
        #         llm=self.llm,
        #         agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        #         verbose=True
        #     )
    
    def _get_context(self) -> Dict[str, Any]:
        """
        Get the context for the supervisor agent.
        
        Returns:
            A dictionary containing context information
        """
        return {
            "legislation_text": self.legislation_text,
            "parties": [party.party_name for party in self.parties],
            "simulation_results": self.simulation_results
        }