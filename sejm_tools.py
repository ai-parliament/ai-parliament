from langchain_core.tools import tool
from langchain_core.tools import Tool
from sejm_extractor import SejmExtractor

class SejmTools:
    '''
    Funkcjonalności z SejmExtractor muszą zostać opakowane w langchainowe tools
    żeby można było je dodac do agenta
    (jeśli dobrze rozumiem)
    '''
    def __init__(self, path):
        self.extractor = SejmExtractor(path)
    
    def get_all_tools(self):
        '''
        Przekonwertowuje funkcje na langchainowe narzędzia i zwraca je
        '''
        voting_stats_tool = Tool.from_function(
            func = self.extractor.get_voting_stats,
            name = "get_voting_statistics",
            description="Zwraca w formacie JSON historie głosowań danego posła zawierającą w ilu głosowaniach brał udział, " \
            "ile ominał i ile odbyło się w sumie według dat."
        )
        votes_tool = Tool.from_function(
            func = self.extractor.get_votes,
            name = "get_specific_votes",
            description="Zwraca w formacie JSON informacje jakie głosy zostały oddane przez danego posła i pod jakimi projektami. " \
            "Wymaga podania daty posiedzenia sejmowego, inaczej zwróci pustą listę."
        )

        return [voting_stats_tool, votes_tool]
