from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
import os
from dotenv import load_dotenv

class Politician:
    def __init__(self, name:str, surname:str):
        load_dotenv()
        self.name = name
        self.surname = surname
        self.memory = ConversationBufferMemory()
        self.model = ChatOpenAI(model=os.getenv("GPT_MODEL_NAME"), temperature=0.8, max_completion_tokens=400)
        self.system_prompt = self._set_system_prompt()

        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

        self.general_beliefs = self.get_general_political_beliefs()


    def answer_question(self, question:str) -> str:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"context: [{self.get_context()}] \n\n question: [{question}]")
        ]
        response = self.model(messages=messages)
        return response
    
    def get_general_political_beliefs(self):
        prompt = f"Jakie poglądy polityczne ma {self.name} {self.surname}?\
            Skup się wyłącznie na jego poglądach politycznych — nie podawaj informacji biograficznych, dat, stanowisk ani ciekawostek.\
            Interesuje mnie tylko to, co myśli na temat spraw politycznych, gospodarczych i społecznych.\
            Wypisz je w następującym formacie: \n\
            1. Gospodarka: \n\
            2. Polityka zagraniczna: \n\
            3. Polityka społeczna: \n\
            4. Sprawy światopoglądowe: \n\""
        
        summary = self.agent_executor.invoke({"input" : prompt})
        return summary['output']
    
    def get_context(self):
        #na razie tylko ogólne poglądy, później też historia rozmowy
        return self.general_beliefs
    
    def _set_system_prompt(self):
        system_prompt = f"Jesteś politykiem i nazywasz się {self.name} {self.surname}. \
                    Bierzesz udział w dyskusji z innymi politykami.\
                    Odpowiadasz w oparciu o własne poglądy polityczne i uwzględniając wypowiedzi innych uczestników."
        return system_prompt

    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
    
    def _setup_sejm_api_tool(self):
        pass

    def _get_all_tools(self):
        #tutaj miejsce na wywołania jeszcze jakichś innych funkcji zwracających narzędzia (?) 
        wiki = self._setup_wikipedia_tool()
        return [wiki] #tu powinny być wszystkie narzędzia

    def _setup_agent(self):
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(self.model, self.tools, basic_prompt)
        return agent

    
