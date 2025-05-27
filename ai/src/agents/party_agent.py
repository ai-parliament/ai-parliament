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
    def __init__(self, party_name: str, party_acronym: str):
        super().__init__()
        self.party_name = party_name
        self.party_acronym = party_acronym
        
        # Lista posłów
        self.politicians: List[PoliticianAgent] = []
        
        # Historia dyskusji
        self.discussion_history = []
        
        # Podstawowa inicjalizacja
        self.general_beliefs = self._get_general_beliefs()
        self.system_prompt = self._set_system_prompt()
        self.tools = self._get_all_tools()
        self.agent = self._setup_agent()
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    def add_politician(self, first_name: str, last_name: str):
        """Dodaje posła do partii"""
        politician = PoliticianAgent(first_name=first_name, last_name=last_name)
        self.politicians.append(politician)
        print(f"Dodano posła: {first_name} {last_name} do partii {self.party_name}")
    
    def get_politicians_opinions(self, legislation_text: str) -> List[Dict[str, str]]:
        """Zbiera opinie posłów na temat ustawy"""
        opinions = []
        
        for politician in self.politicians:
            prompt = f"""
            Projekt ustawy: {legislation_text}
            
            Wyraź swoją opinię na temat tego projektu jako poseł {politician.first_name} {politician.last_name}.
            Czy popierasz tę ustawę? Jakie masz argumenty?
            """
            
            response = politician.answer_question(prompt)
            opinions.append({
                "politician": f"{politician.first_name} {politician.last_name}",
                "opinion": response.content
            })
            
        self.discussion_history = opinions
        return opinions
    
    def formulate_party_stance(self, legislation_text: str) -> str:
        """Formułuje stanowisko partii na podstawie opinii posłów"""
        # Najpierw zbieramy opinie posłów
        if not self.discussion_history:
            self.get_politicians_opinions(legislation_text)
        
        # Przygotowujemy podsumowanie dyskusji
        discussion_summary = "\n".join([
            f"{opinion['politician']}: {opinion['opinion']}" 
            for opinion in self.discussion_history
        ])
        
        # Agent partii formułuje stanowisko na podstawie dyskusji
        prompt = f"""
        Jako lider partii {self.party_name} ({self.party_acronym}), 
        na podstawie poniższych opinii posłów:
        
        {discussion_summary}
        
        Sformułuj oficjalne stanowisko partii:
        1. Głosowanie: ZA/PRZECIW/WSTRZYMANIE
        2. Uzasadnienie decyzji
        3. Czy wszyscy posłowie są zgodni?
        """
        
        response = self.agent_executor.invoke({"input": prompt})
        return response['output']
    
    def answer_question(self, question: str) -> str:
        """Odpowiada na pytanie jako partia"""
        prompt = f"Jako partia {self.party_name}, odpowiedz na pytanie: {question}"
        response = self.agent_executor.invoke({"input": prompt})
        return response['output']
    
    def _get_general_beliefs(self) -> str:
        """Pobiera informacje o partii z Wikipedii"""
        wiki_tool = self._setup_wikipedia_tool()
        
        try:
            # Szukamy informacji o partii
            party_info = wiki_tool.run(f"{self.party_name} partia polityczna Polska")
            
            # Jeśli znajdziemy informacje, zwracamy je
            if party_info and len(party_info) > 100:
                return party_info[:1000]  # Ograniczamy do 1000 znaków
        except:
            pass
        
        # Jeśli nie znajdziemy, zwracamy podstawowe info
        return f"Partia polityczna {self.party_name} ({self.party_acronym}) działająca w Polsce."
    
    def _set_system_prompt(self):
        """System prompt dla agenta partii"""
        return f"""
        Jesteś liderem partii politycznej {self.party_name} ({self.party_acronym}).
        
        Informacje o partii:
        {self.general_beliefs}
        
        Twoim zadaniem jest:
        - Analizować opinie posłów z twojej partii
        - Formułować oficjalne stanowisko partii
        - Dbać o spójność działań partii
        """
    
    def _get_all_tools(self) -> list:
        """Zwraca narzędzia dostępne dla agenta"""
        wiki = self._setup_wikipedia_tool()
        return [wiki]
    
    def _setup_agent(self):
        """Podstawowa konfiguracja agenta"""
        hub_client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
        basic_prompt = hub_client.pull_prompt("hwchase17/openai-tools-agent")
        agent = create_tool_calling_agent(self.llm, self.tools, basic_prompt)
        return agent
    
    def _get_context(self):
        """Zwraca kontekst - historia dyskusji i przekonania partii"""
        return {
            "party_beliefs": self.general_beliefs,
            "discussion_history": self.discussion_history
        }
    
    def _setup_wikipedia_tool(self) -> WikipediaQueryRun:
        """Konfiguruje narzędzie Wikipedia"""
        wiki_wrapper = WikipediaAPIWrapper(lang="pl")
        return WikipediaQueryRun(api_wrapper=wiki_wrapper)