import os
from main_agent import MainAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict


class PoliticianAgent(MainAgent):
    def __init__(self, first_name: str, last_name: str):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name

        # Pobieramy ogólne przekonania (np. krótką notkę biograficzną)
        self.general_beliefs = self._get_general_beliefs()
        # Przygotowujemy system prompt i narzędzia
        self.system_prompt    = self._set_system_prompt()
        self.tools            = self._get_all_tools()
        self.agent            = self._setup_agent()
        self.agent_executor   = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def answer_question(self, question: str):
        """
        Wysyła pytanie do agenta-polityka.
        Zwraca content (str) z odpowiedzi.
        """
        response = self.agent_executor.invoke({"input": question})
        # Dla różnych wersji LangChain:
        if isinstance(response, dict) and "output" in response:
            return response["output"]
        return response.content

    #
    # === IMPLEMENTACJE METOD ABSTRAKCYJNYCH z MainAgent ===
    #

    def _get_general_beliefs(self) -> str:
        """
        Krótka "biografia" lub wstępne przekonania polityka.
        Potrzebne, bo MainAgent wymaga tej metody.
        """
        # Możesz tu dodać wywołanie Wikipedii albo statyczny tekst:
        return f"{self.first_name} {self.last_name}, polityk działający w Polsce."

    def _set_system_prompt(self) -> str:
        """
        Systemowy prompt do agenta-polityka.
        """
        return (
            f"Jesteś politykiem {self.first_name} {self.last_name}.\n"
            "Twoim zadaniem jest odpowiadać na pytania i formułować opinie zgodnie z Twoim profilem."
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
        return {
            "politician_beliefs": self.general_beliefs
        }

    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """
        Konfiguruje narzędzie do zapytań Wikipedii.
        """
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
