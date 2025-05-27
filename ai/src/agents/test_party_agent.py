#!/usr/bin/env python3
"""
Skrypt testowy dla PartyAgent
Testuje podstawowe funkcjonalności agenta partii
"""

import sys
import os
# Dodajemy ścieżkę do modułów
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.src.agents.party_agent import PartyAgent
from logger import Logger

def test_basic_party_creation():
    """Test tworzenia partii"""
    print("\n=== TEST 1: Tworzenie partii ===")
    
    # Tworzymy różne partie
    parties = [
        ("Prawo i Sprawiedliwość", "PiS"),
        ("Koalicja Obywatelska", "KO"),
        ("Lewica", "Lewica"),
        ("Konfederacja", "Konfederacja")
    ]
    
    for party_name, party_acronym in parties:
        try:
            party = PartyAgent(party_name, party_acronym)
            print(f"✓ Utworzono partię: {party_name}")
            
            # Sprawdzamy czy pobrało informacje z Wikipedii
            if len(party.general_beliefs) > 100:
                print(f"  - Pobrano informacje z Wikipedii ({len(party.general_beliefs)} znaków)")
            else:
                print(f"  - Brak szczegółowych informacji z Wikipedii")
                
        except Exception as e:
            print(f"✗ Błąd przy tworzeniu partii {party_name}: {e}")

def test_party_with_politicians():
    """Test partii z posłami"""
    print("\n=== TEST 2: Partia z posłami ===")
    
    # Tworzymy partię KO
    ko = PartyAgent("Koalicja Obywatelska", "KO")
    
    # Dodajemy posłów
    politicians = [
        ("Donald", "Tusk"),
        ("Rafał", "Trzaskowski"),
        ("Barbara", "Nowacka"),
        ("Borys", "Budka")
    ]
    
    print(f"\nDodawanie posłów do {ko.party_name}:")
    for first_name, last_name in politicians:
        ko.add_politician(first_name, last_name)
    
    print(f"\nPartia {ko.party_name} ma {len(ko.politicians)} posłów")

def test_legislation_analysis():
    """Test analizy ustawy"""
    print("\n=== TEST 3: Analiza ustawy ===")
    
    # Przykładowy projekt ustawy
    legislation = """
    Projekt ustawy o podwyższeniu płacy minimalnej
    
    Art. 1. Minimalne wynagrodzenie za pracę od 1 stycznia 2024 roku wynosi 5000 zł brutto.
    Art. 2. Pracodawcy mają 3 miesiące na dostosowanie wynagrodzeń.
    Art. 3. Ustawa wchodzi w życie po 14 dniach od ogłoszenia.
    """
    
    # Tworzymy dwie partie z różnymi poglądami
    print("\nTworzenie partii...")
    pis = PartyAgent("Prawo i Sprawiedliwość", "PiS")
    pis.add_politician("Mateusz", "Morawiecki")
    pis.add_politician("Beata", "Szydło")
    pis.add_politician("Jacek", "Sasin")
    
    ko = PartyAgent("Koalicja Obywatelska", "KO")
    ko.add_politician("Donald", "Tusk")
    ko.add_politician("Rafał", "Trzaskowski")
    ko.add_politician("Barbara", "Nowacka")
    
    # Testujemy dla PiS
    print(f"\n--- Analiza ustawy przez {pis.party_name} ---")
    print("1. Zbieranie opinii posłów...")
    opinions_pis = pis.get_politicians_opinions(legislation)
    
    for opinion in opinions_pis:
        print(f"\n{opinion['politician']}:")
        print(f"{opinion['opinion'][:200]}...")  # Pierwsze 200 znaków
    
    print("\n2. Formułowanie stanowiska partii...")
    stance_pis = pis.formulate_party_stance(legislation)
    print(f"\nStanowisko {pis.party_name}:")
    print(stance_pis)
    
    # Testujemy dla KO
    print(f"\n\n--- Analiza ustawy przez {ko.party_name} ---")
    print("1. Zbieranie opinii posłów...")
    opinions_ko = ko.get_politicians_opinions(legislation)
    
    for opinion in opinions_ko:
        print(f"\n{opinion['politician']}:")
        print(f"{opinion['opinion'][:200]}...")
    
    print("\n2. Formułowanie stanowiska partii...")
    stance_ko = ko.formulate_party_stance(legislation)
    print(f"\nStanowisko {ko.party_name}:")
    print(stance_ko)

def test_party_qa():
    """Test odpowiedzi na pytania"""
    print("\n=== TEST 4: Pytania i odpowiedzi ===")
    
    lewica = PartyAgent("Lewica", "Lewica")
    
    questions = [
        "Jakie jest wasze stanowisko w sprawie praw kobiet?",
        "Co sądzicie o podatkach dla najbogatszych?",
        "Czy popieracie energię atomową?"
    ]
    
    for question in questions:
        print(f"\nPytanie: {question}")
        answer = lewica.answer_question(question)
        print(f"Odpowiedź: {answer[:300]}...")  # Pierwsze 300 znaków

def main():
    """Główna funkcja testowa"""
    print("=== TESTY PARTY AGENT ===")
    
    # Sprawdzamy czy są ustawione zmienne środowiskowe
    required_env = ["OPENAI_API_KEY", "LANGSMITH_API_KEY"]
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"\n⚠️  Brakuje zmiennych środowiskowych: {', '.join(missing)}")
        print("Upewnij się, że masz pliki .env.shared i .env.secret")
        return
    
    try:
        # Uruchamiamy testy
        test_basic_party_creation()
        test_party_with_politicians()
        test_legislation_analysis()
        test_party_qa()
        
        print("\n\n✓ Wszystkie testy zakończone!")
        
    except Exception as e:
        print(f"\n✗ Błąd podczas testów: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()