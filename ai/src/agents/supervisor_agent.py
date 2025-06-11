import os
from .base_agent import BaseAgent
from .party_agent import PartyAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from typing import List, Dict, Any

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
        Run the intra-party deliberation phase.
        
        Returns:
            A dictionary containing the results of the deliberation
        """
        party_stances = {}
        
        for party in self.parties:
            # Get opinions from politicians in the party
            opinions = party.get_politicians_opinions(self.legislation_text)
            
            # Formulate the party's stance
            stance = party.formulate_party_stance(self.legislation_text)
            
            party_stances[party.party_name] = {
                "stance": stance,
                "opinions": opinions
            }
        
        self.simulation_results["intra_party_deliberation"] = party_stances
        return party_stances
    
    def run_inter_party_debate(self):
        """
        Run the inter-party debate phase.
        
        Returns:
            A dictionary containing the results of the debate
        """
        if "intra_party_deliberation" not in self.simulation_results:
            self.run_intra_party_deliberation()
        
        party_stances = self.simulation_results["intra_party_deliberation"]
        
        # Create a summary of all party stances
        stances_summary = "\n\n".join([
            f"{party_name}:\n{data['stance']}"
            for party_name, data in party_stances.items()
        ])
        
        debate_results = {}
        
        # Each party responds to other parties' stances
        for party in self.parties:
            prompt = f"""
            Proposed legislation: {self.legislation_text}
            
            Here are the stances of all parties on this legislation:
            {stances_summary}
            
            As the leader of {party.party_name}, respond to the other parties' positions.
            Try to persuade them to align with your party's stance.
            """
            
            response = party.answer_question(prompt)
            debate_results[party.party_name] = response
        
        self.simulation_results["inter_party_debate"] = debate_results
        return debate_results
    
    def run_voting(self):
        """
        Run the voting phase.
        
        Returns:
            A dictionary containing the results of the voting
        """
        if "inter_party_debate" not in self.simulation_results:
            self.run_inter_party_debate()
        
        voting_results = {}
        total_votes = 0
        votes_in_favor = 0
        
        # Each party votes based on their stance and the debate
        for party in self.parties:
            # Determine the number of votes (equal to the number of politicians)
            num_votes = len(party.politicians)
            total_votes = num_votes
            
            # Determine if the party is in favor or against
            prompt = f"""
            Based on your party's stance and the inter-party debate, 
            will {party.party_name} vote in favor of or against the following legislation?
            
            Legislation: {self.legislation_text}
            
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
        
        self.simulation_results["voting"] = {
            "party_votes": voting_results,
            "total_votes": total_votes,
            "votes_in_favor": votes_in_favor,
            "legislation_passes": legislation_passes
        }
        
        return self.simulation_results["voting"]
    
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
        
        summary_prompt = f"""
        Summarize the results of the parliamentary simulation on the following legislation:
        
        Legislation: {self.legislation_text}
        
        Voting results:
        - Total votes: {voting_results['total_votes']}
        - Votes in favor: {voting_results['votes_in_favor']}
        - Legislation passes: {voting_results['legislation_passes']}
        
        Party votes:
        {self._format_party_votes(voting_results['party_votes'])}
        
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
        return "\n".join([
            f"- {party_name}: {data['vote']} ({data['num_votes']} votes)"
            for party_name, data in party_votes.items()
        ])
    
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
        try:
            langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
            if langsmith_api_key:
                hub_client = Client(api_key=langsmith_api_key)
                basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
                return create_tool_calling_agent(self.llm, self.tools, basic_prompt)
            else:
                # Fallback if LANGSMITH_API_KEY is not available
                from langchain.agents import AgentType, initialize_agent
                return initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                    verbose=True
                )
        except Exception:
            # Fallback if there's an error with LangSmith
            from langchain.agents import AgentType, initialize_agent
            return initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True
            )
    
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