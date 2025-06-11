import os
import random
from main_agent import MainAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict


class PoliticianAgent(MainAgent):
    def __init__(self, first_name: str, last_name: str):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name

        # Przygotowujemy system prompt i narzędzia
        self.tools            = self._get_all_tools()
        self.agent            = self._setup_agent()
        self.agent_executor   = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, return_intermediate_steps=True)

        # Pobieramy ogólne przekonania (np. krótką notkę biograficzną)
        self.general_beliefs = self._get_general_beliefs()
        self.legislation_beliefs = ""
        self.system_prompt    = self._set_system_prompt()

    def answer_question(self, question: str):
        """
        Wysyła pytanie do agenta-polityka.
        Zwraca content (str) z odpowiedzi.
        """
        conversation_history = self.memory.load_memory_variables({})["history"]

        messages = [
            SystemMessage(content=f"{self.system_prompt}. Oto twoje poglądy na temat aktualnie omawianego zagadnienia: {self.legislation_beliefs}\n\
                          Oto wszystkie twoje dotychczasowe wypowiedzi, uwzględnij je w swojej odpowiedzi: {conversation_history}"),
            HumanMessage(content=question)
        ]

        # prefix = f"{self.first_name} {self.last_name}:"
        response = self.model(messages=messages)

        # Dla różnych wersji LangChain:
        if isinstance(response, dict) and "output" in response:
            self.memory.chat_memory.add_ai_message(response["output"])
            return response["output"]
        self.memory.chat_memory.add_ai_message(response.content)
        return response.content
    
    def set_legislation_beliefs(self, legislation_text):
        """
        Jakie poglądy na ten konkretny temat ma dany polityk.
        Dodatkowo decydujemy czy będzie dzisiaj w złym nastroju i niechętny do zgadzania się z innymi
        """

        prompt = f"Znajdź kluczowe zagadnienie omawiane w następującym projekcie ustawy: {legislation_text}."\
            f"Następnie znajdź jakie poglądy na dane zagadnienie ma {self.first_name} {self.last_name} oraz streść je w kilku zdaniach."\
            "Odpowiedź musi zawierać przynajmniej dwa zdania."
        
        summary = self.agent_executor.invoke({"input" : prompt})
        self.bad_day()

        self.legislation_beliefs = summary['output']
    
    def bad_day(self, changed_temperature = 1.2):
        if random.randint(1,3) == 1:
            print(f"O nie! - {self.first_name} {self.last_name} ma dzisiaj zły dzień i jest bardzo kłótliwy.")

            self.system_prompt = f"Jesteś politykiem i nazywasz się {self.name} {self.surname}. \
            Bierzesz udział w dyskusji z innymi politykami.\
            Odpowiadasz w oparciu o własne poglądy polityczne i uwzględniając wypowiedzi innych uczestników.\n\n \
            Oto kontekst na temat tego jakie są twoje ogólne poglądy: context[{self.general_beliefs}] \
            Masz dzisiaj bardzo zły humor, jesteś **kłotliwy** i **nie zgadzasz się** ze stanowiskami swoich kolegów i koleżanek z partii.\
            Twoje poglądy są dzisiaj **zupełnie inne niż zwykle**.\
            **Bardzo ciężko jest cię przekonać do zmiany zdania**."

            self.model.temperature = changed_temperature

    #
    # === IMPLEMENTACJE METOD ABSTRAKCYJNYCH z MainAgent ===
    #

    def _get_general_beliefs(self) -> str:
        """
        Krótka "biografia" lub wstępne przekonania polityka.
        Potrzebne, bo MainAgent wymaga tej metody.
        """
        prompt = f"Jakie poglądy polityczne ma {self.first_name} {self.last_name}?\
            Skup się **wyłącznie** na jego poglądach politycznych — nie podawaj informacji biograficznych, dat, stanowisk ani ciekawostek.\
            Interesuje mnie tylko to, co myśli na temat spraw politycznych, gospodarczych i społecznych.\
            Wypisz je w następującym formacie: \n\
            1. Gospodarka: \n\
            2. Polityka zagraniczna: \n\
            3. Polityka społeczna: \n\
            4. Sprawy światopoglądowe: \n\
            **Wszystkie** z tych pozycji muszą **istnieć**. Jeśli nie znalazłeś o danej pozycji informacji wprost"\
            " postaraj się wydedukować jej zawartość w oparciu o ogólne poglądy polityka."
        
        summary = self.agent_executor.invoke({"input" : prompt})
        return summary['output']

    def _set_system_prompt(self) -> str:
        """
        Systemowy prompt do agenta-polityka.
        """
        return (
            f"Jesteś politykiem i nazywasz się {self.name} {self.surname}. \
            Bierzesz udział w dyskusji z innymi politykami.\
            Odpowiadasz w oparciu o własne poglądy polityczne i uwzględniając wypowiedzi innych uczestników.\n\n \
            Oto kontekst na temat tego jakie są twoje ogólne poglądy: context[{self.general_beliefs}]"
        )

    def _get_all_tools(self) -> List:
        """
        Narzędzia używane przez agenta (np. dostęp do Wikipedii).
        """
        return [self._setup_wikipedia_tool()]

    def _setup_agent(self):
        """
        Buduje i zwraca agenta LangChain z podpiętym promptem i narzędziami.
        """
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        return create_tool_calling_agent(self.llm, self.tools, basic_prompt)

    def _get_context(self) -> Dict[str, str]:
        """
        Zwraca kontekst dla pamięci lub dalszych promptów.
        """
        return self.general_beliefs

    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """
        Konfiguruje narzędzie do zapytań Wikipedii.
        """
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
