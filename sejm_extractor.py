import json
import requests
import time

class SejmExtractor:
    
    def __init__(self, path:str):
        self.path = path
        self.allMpData = self._extractJson()

    def get_voting_stats(self, first_name:str, last_name:str) -> dict:
        """
        Pobiera historie głosowań danego posła według dni, tylko statystyki liczbowe
        typu ile było głosowań a w ilu zagłosował i ile ominął
        Czy był obecny danego dnia tez

        """

        full_name = f"{first_name} {last_name}".lower()
        id = self._get_id_by_name(full_name)
        url = f"https://api.sejm.gov.pl/sejm/term10/MP/{id}/votings/stats"

        all_stats = self._get_from_url(url)

        return all_stats
    
    def get_votes(self, first_name:str, last_name:str, date:str) -> list[dict]:
        """
        Zwraca na co konkretnie głosował poseł razem z tytułem głosowania, krótkim opisem i jakimiś jeszcze technikaliami
        Problem jest tylko taki że to są dane o konkretnych dniach więc trzeba znać konkretne daty kiedy coś się działo w sejmie
        Do ustalenia co z tym zrobić
        """
        full_name = f"{first_name} {last_name}".lower()
        id = self._get_id_by_name(full_name)
        
        all_votes_that_day = []
        nr_posiedzenia = 1 #jest w linku do API, chyba oznacza które to jest zebranie danego dnia

        for i in range(nr_posiedzenia, 11): #raczej nie będzie więcej niż 10 posiedzeń jednego dnia
            url = f"https://api.sejm.gov.pl/sejm/term10/MP/{id}/votings/{i}/{date}"
            glosowania = self._get_from_url(url)
            if not glosowania:
                #jeśli zapytanie zwróci pustą listę to znaczy że 
                break
            all_votes_that_day.append(glosowania)

        return all_votes_that_day

    def _extractJson(self) -> list[dict]:
        with open(self.path, "r", encoding="utf-8") as f:
            everyoneFullData = json.load(f)
        return everyoneFullData
    
    def _get_id_by_name(self, full_name:str):
        """
        Zwraca id posła o danym imieniu i nazwisku tak jak występuje w systemie Sejmowym
        Dane pobrałem na sztywno do jsona all_mps_data ale równie dobrze może się to robić
        jako funkcja z każdym uruchomieniem programu - do ustalenia

        Id jest potrzebne żeby pobrać statystyki konkretnego posła np. głosowania bo to
        musi być w linku do API
        """

        try:
            for mp_dictionary in self.allMpData:
                if mp_dictionary['firstLastName'].lower() == full_name:
                    return mp_dictionary['id']

        except:
            #to zastąpić później przez logging a wszystkie logi wrzucac do folderu logs
            raise ValueError(f"Nie znaleziono posła o imieniu i nazwisku: {full_name}")

    def _get_from_url(self, url:str) -> dict:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                returned_data_json = response.json()
                return returned_data_json
            else:
                print(f"Nie udało się pobrać danych")

        except requests.exceptions.RequestException as e:
            #to też zrzucić do logów
            print(f"Błąd przy ID {id}: {e}")
