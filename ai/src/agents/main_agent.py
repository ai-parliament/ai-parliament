from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langsmith import Client
from langchain.agents import create_tool_calling_agent
from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI


class MainAgent(ABC):
    def __init__(self):
        load_dotenv(dotenv_path='.env.shared')
        load_dotenv(dotenv_path='.env.secret')
        self.model_name = os.getenv("MODEL_NAME")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.memory = ConversationBufferMemory(return_messages=True)

        self.llm = ChatGoogleGenerativeAI(
            model_name = self.model_name,
            openai_api_key = self.openai_api_key,
            temperature = 0.7
            )
        self.system_prompt = None
        
        self.tools = None
        self.agent = None
        self.agent_executor = None
    
    @abstractmethod
    def answer_question(self, question: str) -> str:
        pass

    @abstractmethod
    def _get_general_beliefs(self) -> str:
        pass

    @abstractmethod
    def _set_system_prompt(self):
        pass

    @abstractmethod
    def _get_all_tools(self) -> list:
        pass

    @abstractmethod
    def _setup_agent(self):
        pass

    @abstractmethod
    def _get_context(self):
        pass

