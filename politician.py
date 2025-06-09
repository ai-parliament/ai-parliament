from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
import os
from dotenv import load_dotenv
from sejm_tools import SejmTools
from sejm_extractor import SejmExtractor

class Politician:
    def __init__(self, name:str, surname:str):
        load_dotenv()
        self.name = name
        self.surname = surname
        self.memory = ConversationBufferMemory(return_messages=True)
        self.model = ChatOpenAI(model=os.getenv("GPT_MODEL_NAME"), temperature=0.8, max_completion_tokens=400)

        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

        self.general_beliefs = self.get_general_political_beliefs()
        self.system_prompt = self._set_system_prompt()

    def answer_question(self, question:str) -> str:
        '''
        Funkcja do pogadania sobie z posłem, odpowiada na pytanie mając kontekst ze swoich narzędzi
        '''
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"context of the conversation: [{self.memory.load_memory_variables({})['history']}] \n\n question: [{question}]")
        ]
        messages += self.memory.load_memory_variables({})["history"]

        response = self.model(messages=messages)
        self.memory.chat_memory.add_ai_message(response.content)
        return response
    
        #Próba zrobienia go jako agenta - nie łapie kontekstu i zapomina że jest politykiem (?)
        #memory = self.memory.load_memory_variables({})["history"]

        # inputs = {
        #     "input": f"Pytanie: {question}",
        #     "chat_history": memory
        # }

        # response = self.agent_executor.invoke(inputs)

        # output = response["output"]

        # self.memory.chat_memory.add_user_message(question)
        # self.memory.chat_memory.add_ai_message(output)

        return output
    
    def get_general_political_beliefs(self):
        prompt = f"Jakie poglądy polityczne ma {self.name} {self.surname}?\
            Skup się wyłącznie na jego poglądach politycznych — nie podawaj informacji biograficznych, dat, stanowisk ani ciekawostek.\
            Interesuje mnie tylko to, co myśli na temat spraw politycznych, gospodarczych i społecznych.\
            Wypisz je w następującym formacie: \n\
            1. Gospodarka: \n\
            2. Polityka zagraniczna: \n\
            3. Polityka społeczna: \n\
            4. Sprawy światopoglądowe: \n"
        
        summary = self.agent_executor.invoke({"input" : prompt})
        return summary['output']
    
    def get_context(self):
        #na razie tylko ogólne poglądy, później też historia rozmowy, głosowania itd
        return self.general_beliefs
    
    def _set_system_prompt(self):
        system_prompt = f"Jesteś politykiem i nazywasz się {self.name} {self.surname}. \
                    Bierzesz udział w dyskusji z innymi politykami.\
                    Odpowiadasz w oparciu o własne poglądy polityczne i uwzględniając wypowiedzi innych uczestników.\n\n \
                    Oto kontekst na temat tego jakie są twoje poglądy: context[{self.general_beliefs}]"
        return system_prompt

    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
    
    def _setup_sejm_api_tool(self):
        self.sejm_toolset = SejmTools("dane_poslow.json")
        return self.sejm_toolset.get_all_tools()

    def _get_all_tools(self):
        #tutaj miejsce na wywołania jeszcze jakichś innych funkcji zwracających narzędzia (?) 
        wiki = self._setup_wikipedia_tool()
        sejm = self._setup_sejm_api_tool()

        #return [wiki]
        return [wiki, sejm[0], sejm[1]] #tu powinny być wszystkie narzędzia

    def _setup_agent(self):
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(self.model, self.tools, basic_prompt)
        return agent

    
