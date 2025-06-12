import os
from .base_agent import BaseAgent
from .politician_agent import PoliticianAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict, Any

class PartyAgent(BaseAgent):
    """
    Agent representing a political party in the AI Parliament system.
    """
    def __init__(self, name: str, acronym: str = ""):
        """
        Initialize a party agent.
        
        Args:
            name: The name of the party
            acronym: The acronym of the party
        """
        super().__init__()
        self.party_name = name
        self.party_acronym = acronym
        
        # List of politicians and discussion history
        self.politicians: List[PoliticianAgent] = []
        self.discussion_history: List[Dict[str, str]] = []
        
        # Set up agent
        self.party_info = self._get_party_info()
        self.system_prompt = self._set_system_prompt()
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True
        )
    
    @property
    def name(self) -> str:
        """
        Get the name of the party.
        
        Returns:
            The party name
        """
        return self.party_name
    
    @name.setter
    def name(self, value: str):
        """
        Set the name of the party.
        
        Args:
            value: The new party name
        """
        self.party_name = value
    
    def add_politician(self, full_name: str, role: str = ""):
        """
        Add a politician to the party.
        
        Args:
            full_name: The full name of the politician
            role: The role of the politician in the party
        """
        parts = full_name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        
        politician = PoliticianAgent(
            first_name=first_name, 
            last_name=last_name,
            party_name=self.party_name
        )
        politician.name = full_name  
        politician.role = role
        self.politicians.append(politician)
        print(f"Added politician: {full_name} to party {self.party_name}")
    
    def get_politicians_opinions(self, legislation_text: str) -> List[Dict[str, str]]:
        """
        Get opinions from all politicians in the party about a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            A list of dictionaries containing politician names and their opinions
        """
        opinions = []
        for politician in self.politicians:
            prompt = self.prompt_manager.format_prompt(
                'politician',
                'legislation_opinion_prompt',
                legislation_text=legislation_text,
                full_name=politician.full_name
            )
                
            response = politician.answer_question(prompt)
            opinions.append({
                "politician": politician.full_name,
                "opinion": response
            })
        
        self.discussion_history = opinions
        return opinions
    
    def formulate_party_stance(self, legislation_text: str) -> str:
        """
        Formulate the party's stance on a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            The party's stance as a string
        """
        if not self.discussion_history:
            self.get_politicians_opinions(legislation_text)
        
        discussion_summary = "\n".join(
            f"{op['politician']}: {op['opinion']}"
            for op in self.discussion_history
        )
        
        prompt = self.prompt_manager.format_prompt(
            'party',
            'stance_prompt',
            party_name=self.party_name,
            party_acronym=self.party_acronym,
            discussion_summary=discussion_summary
        )
        
        response = self.agent_executor.invoke({"input": prompt})
        return response["output"]
    
    def analyze_legislation(self, legislation_text: str) -> str:
        """
        Analyze a piece of legislation.
        
        Args:
            legislation_text: The text of the legislation
            
        Returns:
            The party's analysis as a string
        """
        return self.formulate_party_stance(legislation_text)
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question as this party.
        
        Args:
            question: The question to answer
            
        Returns:
            The party's response
        """
        prompt = self.prompt_manager.format_prompt(
            'party',
            'question_prompt',
            party_name=self.party_name,
            question=question
        )
            
        response = self.agent_executor.invoke({"input": prompt})
        return response["output"]
    
    def _get_party_info(self) -> str:
        """
        Get information about the party.
        
        Returns:
            Information about the party as a string
        """
        wiki_tool = self._setup_wikipedia_tool()
        try:
            party_info = wiki_tool.invoke(f"{self.party_name} political party Poland")
            if party_info and len(party_info) > 100:
                return party_info[:1000]
        except Exception:
            pass
        
        return f"Political party {self.party_name} ({self.party_acronym}) operating in Poland."
    
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the party agent.
        
        Returns:
            The system prompt as a string
        """
        return self.prompt_manager.format_prompt(
            'party',
            'system_prompt',
            party_name=self.party_name,
            party_acronym=self.party_acronym,
            party_info=self.party_info
        )
    
    def _get_all_tools(self) -> List:
        """
        Get all tools available to the party agent.
        
        Returns:
            A list of tools
        """
        return [self._setup_wikipedia_tool()]
    
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
    
    def _get_context(self) -> Dict[str, Any]:
        """
        Get the context for the party agent.
        
        Returns:
            A dictionary containing context information
        """
        return {
            "party_name": self.party_name,
            "party_acronym": self.party_acronym,
            "party_info": self.party_info,
            "discussion_history": self.discussion_history
        }
    
    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """
        Set up the Wikipedia tool.
        
        Returns:
            A configured Wikipedia query tool
        """
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
    
    def update_members_on_legislation(self, legislation: str):
        for politician in self.politicians:
            politician.set_legislation_beliefs(legislation)

        print(f"Wszyscy posłowie partii {self.party_name} zaznajomili się z tekstem ustawy.")