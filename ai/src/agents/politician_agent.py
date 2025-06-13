import os
from .base_agent import BaseAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client, traceable
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict, Any
from .cache_manager import cache_manager
from .cached_wikipedia import CachedWikipediaTool


class PoliticianAgent(BaseAgent):
    """
    Agent representing a politician in the AI Parliament system.
    """
    @traceable(name="Get Politician Opinion")
    def __init__(self, first_name: str, last_name: str, party_name: str = ""):
        """
        Initialize a politician agent.
        
        Args:
            first_name: The first name of the politician
            last_name: The last name of the politician
            party_name: The name of the party the politician belongs to
        """
        # Check cache first
        cached_data = cache_manager.get_politician(first_name, last_name, party_name)
        
        if cached_data:
            print(f"✅ Loaded {first_name} {last_name} from cache!")
            # Load cached data
            beliefs = cached_data['beliefs']
            wikipedia_summary = cached_data.get('wikipedia_summary', '')
            
            # Initialize parent
            super().__init__()
            
            # Set cached values
            self.beliefs = beliefs
            self.wikipedia_summary = wikipedia_summary
            self._from_cache = True
        else:
            print(f"🔄 Initializing {first_name} {last_name}...")
            super().__init__()
            self._from_cache = False
        
        self.first_name = first_name
        self.last_name = last_name
        self.full_name = f"{first_name} {last_name}"
        self.party_name = party_name
        self.role = ""  # Can be set later (e.g., "Minister of Finance")
        
        # Set up tools and agent
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True, 
            return_intermediate_steps=True
        )
        
        # Get politician's beliefs and set system prompt
        if not self._from_cache:
            self.beliefs = self._get_beliefs()
            # Save to cache
            self._save_to_cache()
        
        self.system_prompt = self._set_system_prompt()
    
    def _save_to_cache(self):
        """Save politician data to cache"""
        cache_manager.save_politician(
            self.first_name,
            self.last_name,
            self.party_name,
            {
                'beliefs': self.beliefs,
                'wikipedia_summary': getattr(self, 'wikipedia_summary', ''),
                'full_name': self.full_name,
                'party_name': self.party_name
            }
        )
        
    @traceable(name="Get Politician Opinion")
    def answer_question(self, question: str) -> str:
        """
        Answer a question as this politician.
        
        Args:
            question: The question to answer
            
        Returns:
            The politician's response
        """
        conversation_history = self.memory.load_memory_variables({})["history"]
        
        messages = [
            SystemMessage(content=f"{self.system_prompt}. Consider your previous statements in this conversation: {conversation_history}"),
            HumanMessage(content=question)
        ]
        
        response = self.model.invoke(messages)
        
        self.memory.chat_memory.add_ai_message(response.content)
        return response.content
    
    def _get_beliefs(self) -> str:
        """
        Get the politician's beliefs by querying for information.
        
        Returns:
            A string containing the politician's political beliefs
        """
        # If we're refreshing, clear the cache
        if hasattr(self, '_force_refresh') and self._force_refresh:
            cache_path = cache_manager.get_politician_cache_path(
                self.first_name, self.last_name, self.party_name
            )
            if cache_path.exists():
                cache_path.unlink()
        
        prompt = self.prompt_manager.format_prompt(
            'politician', 
            'beliefs_prompt', 
            full_name=f'"{self.full_name}" polityk {self.party_name} Polska'
        )
        
        try:
            summary = self.agent_executor.invoke({"input": prompt})
            output = summary['output']
            
            # Verify we got the right person
            if self.last_name.lower() not in output.lower():
                # Try again with more specific search
                prompt = f'Find information about Polish politician {self.full_name} from {self.party_name} party'
                summary = self.agent_executor.invoke({"input": prompt})
                output = summary['output']
            
            return output
        except Exception as e:
            # Fallback if agent execution fails
            return f"A politician with moderate views on most issues. Represents {self.party_name}."
    
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the politician agent.
        
        Returns:
            The system prompt as a string
        """
        return self.prompt_manager.format_prompt(
            'politician', 
            'system_prompt', 
            full_name=self.full_name,
            party_name=self.party_name,
            beliefs=self.beliefs
        )
    
    def _get_all_tools(self) -> List:
        """
        Get all tools available to the politician agent.
        
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
        Get the context for the politician agent.
        
        Returns:
            A dictionary containing context information
        """
        return {
            "name": self.full_name,
            "party": self.party_name,
            "role": self.role,
            "beliefs": self.beliefs
        }
    
    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """
        Set up the Wikipedia tool with caching.
        
        Returns:
            A configured Wikipedia query tool
        """
        cached_tool = CachedWikipediaTool(cache_manager, lang="pl")
        return cached_tool.as_tool()