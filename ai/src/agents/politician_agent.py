import os
from .base_agent import BaseAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict, Any

class PoliticianAgent(BaseAgent):
    """
    Agent representing a politician in the AI Parliament system.
    """
    def __init__(self, first_name: str, last_name: str, party_name: str = ""):
        """
        Initialize a politician agent.
        
        Args:
            first_name: The first name of the politician
            last_name: The last name of the politician
            party_name: The name of the party the politician belongs to
        """
        super().__init__()
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
        self.beliefs = self._get_beliefs()
        self.system_prompt = self._set_system_prompt()
    
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
        prompt = f"""
        What are the political views of {self.full_name}?
        Focus ONLY on their political views - do not include biographical information, dates, positions, or trivia.
        I'm only interested in what they think about political, economic, and social issues.
        List them in the following format:
        
        1. Economy:
        2. Foreign policy:
        3. Social policy:
        4. Worldview issues:
        
        ALL of these positions MUST exist. If you can't find explicit information about a position,
        try to deduce its content based on the politician's general views.
        """
        
        try:
            summary = self.agent_executor.invoke({"input": prompt})
            return summary['output']
        except Exception as e:
            # Fallback if agent execution fails
            return f"A politician with moderate views on most issues. Represents {self.party_name}."
    
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the politician agent.
        
        Returns:
            The system prompt as a string
        """
        return f"""
        You are a politician named {self.full_name}. You are a member of {self.party_name}.
        You are participating in a discussion with other politicians.
        You respond based on your own political views and take into account what others have said.
        
        Here is context about your political views:
        {self.beliefs}
        
        When responding:
        1. Stay in character as {self.full_name}
        2. Be consistent with your political views
        3. Be persuasive but respectful
        4. Use a formal, parliamentary style of speech
        """
    
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
        Set up the Wikipedia tool.
        
        Returns:
            A configured Wikipedia query tool
        """
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)