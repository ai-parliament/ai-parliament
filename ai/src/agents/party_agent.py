from main_agent import MainAgent
from politician_agent import PoliticianAgent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langsmith import Client
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from typing import List, Dict
import os


class PartyAgent(MainAgent):
    def __init__(self, name: str, acronym: str = ""):
        super().__init__()
        # alias dla testów
        self.party_name = name
        self.party_acronym = acronym

        # Lista posłów i historia dyskusji
        self.politicians: List[PoliticianAgent] = []
        self.discussion_history: List[Dict[str, str]] = []

        # Ustawienia agenta
        self.general_beliefs = self._get_general_beliefs()
        self.system_prompt   = self._set_system_prompt()
        self.tools           = self._get_all_tools()
        self.agent           = self._setup_agent()
        self.agent_executor  = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    @property
    def name(self) -> str:
        """Pozwala testom zrobić party.name"""
        return self.party_name

    @name.setter
    def name(self, value: str):
        """Obsługa przypisania self.name = … z MainAgent.__init__"""
        self.party_name = value

    def add_politician(self, full_name: str, role: str = ""):
        parts = full_name.split(maxsplit=1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        politician = PoliticianAgent(first_name=first_name, last_name=last_name)
        politician.name = full_name  # żeby test mógł to odczytać
        politician.role = role
        self.politicians.append(politician)
        print(f"Dodano posła: {full_name} do partii {self.party_name}")

    def get_politicians_opinions(self, legislation_text: str) -> List[Dict[str, str]]:
        opinions = []
        for politician in self.politicians:
            prompt = f"""
            Projekt ustawy: {legislation_text}

            Wyraź swoją opinię na temat tego projektu jako poseł {politician.name}.
            Czy popierasz tę ustawę? Jakie masz argumenty?
            """
            response = politician.answer_question(prompt)
            opinions.append({
                "politician": politician.name,
                "opinion": response
            })

        self.discussion_history = opinions
        return opinions

    def formulate_party_stance(self, legislation_text: str) -> str:
        if not self.discussion_history:
            self.get_politicians_opinions(legislation_text)

        discussion_summary = "\n".join(
            f"{op['politician']}: {op['opinion']}"
            for op in self.discussion_history
        )
        prompt = (
            f"Jesteś liderem partii {self.party_name} ({self.party_acronym}). "
            f"Oto opinie posłów na temat ustawy:\n\n{discussion_summary}\n\n"
            "Sformułuj krótkie stanowisko partii wobec tej ustawy."
        )
        response = self.agent_executor.invoke({"input": prompt})
        return response["output"]

    def analyze_legislation(self, legislation_text: str) -> str:
        """Alias dla testów: party.analyze_legislation(...)"""
        return self.formulate_party_stance(legislation_text)

    def answer_question(self, question: str) -> str:
        prompt = f"Jako partia {self.party_name}, odpowiedz na pytanie: {question}"
        response = self.agent_executor.invoke({"input": prompt})
        return response["output"]

    def ask(self, question: str) -> str:
        """Alias dla testów: party.ask(...)"""
        return self.answer_question(question)

    def _get_general_beliefs(self) -> str:
        wiki_tool = self._setup_wikipedia_tool()
        try:
            party_info = wiki_tool.run(f"{self.party_name} partia polityczna Polska")
            if party_info and len(party_info) > 100:
                return party_info[:1000]
        except:
            pass
        return f"Partia polityczna {self.party_name} ({self.party_acronym}) działająca w Polsce."

    def _set_system_prompt(self) -> str:
        return (
            f"Jesteś liderem partii politycznej {self.party_name} ({self.party_acronym}).\n\n"
            f"Informacje o partii:\n{self.general_beliefs}\n\n"
            "Twoim zadaniem jest reprezentować stanowisko partii."
        )

    def _get_all_tools(self):
        return [self._setup_wikipedia_tool()]

    def _setup_agent(self):
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        return create_tool_calling_agent(self.llm, self.tools, basic_prompt)

    def _get_context(self) -> Dict[str, str]:
        return {
            "party_beliefs": self.general_beliefs,
            "discussion_history": self.discussion_history
        }

    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)
