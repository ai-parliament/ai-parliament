import json

class SejmExtractor:
    
    def __init__(self, path:str):
        self.path = path
        self.allMpData = self._extractJson(self.path)

    def _extractJson(self) -> list[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            everyoneFullData = json.load(f)
        return everyoneFullData
    
    def _get_id_by_name(self, first_name:str, last_name:str):
        full_name = f"{first_name} {last_name}".lower()

        try:
            for mp_dictionary in self.allMpData:
                if mp_dictionary['firstLastName'].lower() == full_name:
                    return mp_dictionary['id']

        except:
            #to zastąpić później przez logging a wszystkie logi wrzucac do folderu logs
            print(f"Wystąpił błąd przy szukaniu danych dla {full_name}")