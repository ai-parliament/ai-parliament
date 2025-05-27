from main_agent import MainAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import Tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langsmith import Client
from langchain.agents import create_tool_calling_agent, AgentExecutor


class PoliticianAgent(MainAgent):
    def __init__(self, first_name: str, last_name: str):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.system_prompt = self._set_system_prompt()
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def answer_question(self, question):

        #ten tez powinien byc zasysany
        prompt = (
            """
            ## context of the conversation:\n
            {conversation_history}\n\n
            ## question: [{question}]"
            """
            )
        prompt = prompt.replace("{conversation_hisotry}", self.memory.load_memory_variables({})["history"])
        prompt = prompt.replace("{question}", question)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=prompt)
        ]
        messages += self.memory.load_memory_variables({})["history"]

        response = self.model(messages=messages)
        self.memory.chat_memory.add_ai_message(response.content)
        return response
    
    def get_general_political_beliefs(self):

        #ten prompt pewnie powinien być jako zasysany z prompt menadzera
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
    
    def _set_system_prompt(self):

        #ten prompt pewnie tez
        system_prompt = f"Jesteś politykiem i nazywasz się {self.name} {self.surname}. \
                    Bierzesz udział w dyskusji z innymi politykami.\
                    Odpowiadasz w oparciu o własne poglądy polityczne i uwzględniając wypowiedzi innych uczestników.\n\n \
                    Oto kontekst na temat tego jakie są twoje poglądy: context[{self.general_beliefs}]"
        return system_prompt
    
    def _get_all_tools(self):
        #tutaj miejsce na wywołania jeszcze jakichś innych funkcji zwracających narzędzia (?) 
        wiki = self._setup_wikipedia_tool()
        return [wiki]
    
    def _setup_agent(self):    
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(self.llm, self.tools, basic_prompt)
        return agent
    
    def _get_context(self):
        #na razie tylko ogólne poglądy, później też historia rozmowy, głosowania itd
        return self.general_beliefs
    
    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)

    