from dotenv import load_dotenv
import os
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..utilities.prompt_manager import PromptManager

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the AI Parliament system.
    Provides common functionality and defines the interface that all agents must implement.
    """
    def __init__(self):
        # Load environment variables
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        # Try to load environment variables from different possible locations
        env_files = [
            os.path.join(project_root, '.env'),
            os.path.join(project_root, '.env.shared'),
            os.path.join(project_root, '.env.secret')
        ]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                load_dotenv(dotenv_path=env_file)
        
        # Initialize LLM and memory
        self.model_name = os.getenv("GPT_MODEL_NAME", "gpt-4o-mini")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.7,
            max_tokens=2000
        )
        
        # For compatibility with derived classes
        self.model = self.llm
        
        # Initialize prompt manager
        self.prompt_manager = PromptManager()
        
        # Basic attributes
        self.name = ""
        self.system_prompt = None
        self.tools = None
        self.agent = None
        self.agent_executor = None
    
    @abstractmethod
    def answer_question(self, question: str) -> str:
        """
        Process a question and return an answer.
        
        Args:
            question: The question to answer
            
        Returns:
            A string containing the agent's response
        """
        pass
    
    @abstractmethod
    def _set_system_prompt(self) -> str:
        """
        Set the system prompt for the agent.
        
        Returns:
            The system prompt as a string
        """
        pass
    
    @abstractmethod
    def _get_all_tools(self) -> List:
        """
        Get all tools available to the agent.
        
        Returns:
            A list of tools
        """
        pass
    
    @abstractmethod
    def _setup_agent(self):
        """
        Set up the agent with the appropriate tools and prompt.
        
        Returns:
            The configured agent
        """
        pass
    
    @abstractmethod
    def _get_context(self) -> Dict[str, Any]:
        """
        Get the context for the agent.
        
        Returns:
            A dictionary containing context information
        """
        pass