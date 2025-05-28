from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langchain.memory import ConversationBufferMemory
from langsmith import Client
from langchain.agents import create_tool_calling_agent
from abc import ABC, abstractmethod
from langchain_google_genai import ChatGoogleGenerativeAI


class MainAgent(ABC):
    def __init__(self):
        # Znajdujemy ścieżkę do głównego katalogu projektu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Idziemy 4 poziomy w górę: agents -> src -> ai -> ai-parliament
        #4 poziomy wychodzą poza projekt
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        
        # Ładujemy pliki .env z głównego katalogu
        env_shared = os.path.join(project_root, '.env.shared')
        env_secret = os.path.join(project_root, '.env.secret')
        
        load_dotenv(dotenv_path=env_shared)
        load_dotenv(dotenv_path=env_secret)
        
        self.model_name = os.getenv("MODEL_NAME")
        self.openai_api_key = os.getenv("GPT_MODEL_NAME")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.memory = ConversationBufferMemory(return_messages=True)

        # Poprawne parametry dla Gemini
        # self.llm = ChatGoogleGenerativeAI(
        #     model=self.model_name,  # 'model' nie 'model_name'
        #     google_api_key=self.google_api_key,  # 'google_api_key' nie 'openai_api_key'
        #     temperature=0.7,
        #     convert_system_message_to_human=True  # Gemini nie obsługuje system messages
        # )
        self.llm = ChatOpenAI(model=os.getenv("GPT_MODEL_NAME"),
                              temperature=0.8)
        
        # Dla kompatybilności z politician_agent.py
        self.model = self.llm
        
        # Atrybuty dla kompatybilności z politician_agent
        self.name = getattr(self, 'first_name', '')
        self.surname = getattr(self, 'last_name', '')
        self.general_beliefs = ''
        
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