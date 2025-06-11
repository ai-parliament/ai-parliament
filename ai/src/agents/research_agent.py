import os
from .base_agent import BaseAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict, Any

class ResearchAgent(BaseAgent):
    """
    Agent that searches for data from Wikipedia about parties and politicians.
    """
    def __init__(self):
        """
        Initialize a research agent.
        """
        super().__init__()
        
        # Set up agent
        self.system_prompt = self._set_system_prompt()
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=self.tools, 
            verbose=True
        )
        
        # Cache for storing research results
        self.research_cache = {}
    
    def research_party(self, party_name: str) -> Dict[str, Any]:
        """
        Research information about a political party.
        
        Args:
            party_name: The name of the party
            
        Returns:
            A dictionary containing information about the party
        """
        # Check if we already have this information in the cache
        cache_key = f"party_{party_name}"
        if cache_key in self.research_cache:
            return self.research_cache[cache_key]
        
        prompt = f"""
        Research the political party '{party_name}' in Poland.
        
        Provide the following information:
        1. Brief history and founding
        2. Ideology and political position
        3. Key policy positions
        4. Current leadership
        5. Electoral performance
        
        Format the information in a structured way.
        """
        
        response = self.agent_executor.invoke({"input": prompt})
        
        # Process and structure the response
        party_info = {
            "name": party_name,
            "research_data": response["output"],
            "summary": self._generate_summary(response["output"], "party")
        }
        
        # Cache the results
        self.research_cache[cache_key] = party_info
        
        return party_info
    
    def research_politician(self, full_name: str) -> Dict[str, Any]:
        """
        Research information about a politician.
        
        Args:
            full_name: The full name of the politician
            
        Returns:
            A dictionary containing information about the politician
        """
        # Check if we already have this information in the cache
        cache_key = f"politician_{full_name}"
        if cache_key in self.research_cache:
            return self.research_cache[cache_key]
        
        prompt = f"""
        Research the Polish politician '{full_name}'.
        
        Provide the following information:
        1. Brief biography
        2. Political party affiliation
        3. Political positions and ideology
        4. Notable statements or votes
        5. Current role in politics
        
        Format the information in a structured way.
        """
        
        response = self.agent_executor.invoke({"input": prompt})
        
        # Process and structure the response
        politician_info = {
            "name": full_name,
            "research_data": response["output"],
            "summary": self._generate_summary(response["output"], "politician")
        }
        
        # Cache the results
        self.research_cache[cache_key] = politician_info
        
        return politician_info
    
    def research_legislation(self, topic: str) -> Dict[str, Any]:
        """
        Research information about a legislative topic.
        
        Args:
            topic: The topic of the legislation
            
        Returns:
            A dictionary containing information about the legislation
        """
        # Check if we already have this information in the cache
        cache_key = f"legislation_{topic}"
        if cache_key in self.research_cache:
            return self.research_cache[cache_key]
        
        prompt = f"""
        Research information about legislation related to '{topic}' in Poland.
        
        Provide the following information:
        1. Current legal status
        2. Recent legislative proposals
        3. Key debates and controversies
        4. Positions of major political parties
        5. Public opinion
        
        Format the information in a structured way.
        """
        
        response = self.agent_executor.invoke({"input": prompt})
        
        # Process and structure the response
        legislation_info = {
            "topic": topic,
            "research_data": response["output"],
            "summary": self._generate_summary(response["output"], "legislation")
        }
        
        # Cache the results
        self.research_cache[cache_key] = legislation_info
        
        return legislation_info
    
    def generate_legislation_text(self, topic: str) -> str:
        """
        Generate text for a piece of legislation on a given topic.
        
        Args:
            topic: The topic of the legislation
            
        Returns:
            The generated legislation text
        """
        # First, research the topic
        legislation_info = self.research_legislation(topic)
        
        prompt = f"""
        Based on the following research about '{topic}' in Poland:
        
        {legislation_info['research_data']}
        
        Generate a realistic draft legislation text that could be debated in the Polish parliament.
        The legislation should:
        1. Have a formal title and preamble
        2. Include 3-5 key articles or sections
        3. Be specific enough to generate meaningful debate
        4. Be controversial enough that different parties might have different opinions
        
        Format it as a proper legislative document.
        """
        
        response = self.answer_question(prompt)
        return response
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the research agent.
        
        Args:
            question: The question to answer
            
        Returns:
            The agent's response
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=question)
        ]
        
        response = self.model(messages=messages)
        
        if isinstance(response, dict) and "output" in response:
            return response["output"]
        
        return response.content
    
    def _generate_summary(self, research_data: str, entity_type: str) -> str:
        """
        Generate a concise summary of research data.
        
        Args:
            research_data: The research data to summarize
            entity_type: The type of entity (party, politician, or legislation)
            
        Returns:
            A concise summary
        """
        prompt = f"""
        Summarize the following information about a {entity_type} in 2-3 sentences:
        
        {research_data}
        
        Provide only the most essential information.
        """
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = self.model(messages=messages)
        
        if isinstance(response, dict) and "output" in response:
            return response["output"]
        
        return response.content
    
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the research agent.
        
        Returns:
            The system prompt as a string
        """
        return """
        You are a research agent specializing in Polish politics.
        Your role is to gather accurate information about political parties, politicians, and legislative topics.
        
        When researching:
        1. Focus on factual information from reliable sources
        2. Provide balanced and objective information
        3. Include different perspectives when relevant
        4. Structure information clearly and concisely
        5. Prioritize recent and relevant information
        
        When generating summaries or legislation text, ensure they are realistic and reflect the actual
        political landscape in Poland.
        """
    
    def _get_all_tools(self) -> List:
        """
        Get all tools available to the research agent.
        
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
        Get the context for the research agent.
        
        Returns:
            A dictionary containing context information
        """
        return {
            "research_cache": self.research_cache
        }
    
    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """
        Set up the Wikipedia tool.
        
        Returns:
            A configured Wikipedia query tool
        """
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)