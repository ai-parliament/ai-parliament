#!/usr/bin/env python3
"""
Skrypt testowy dla PoliticianAgent
Testuje podstawowe funkcjonalności agenta polityka
"""

import sys
import os

# 1) Znajdź katalog z tym skryptem
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2) Wyznacz root projektu (katalog z .env)
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

# 3) Wczytaj zmienne środowiskowe
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env.shared"))
load_dotenv(os.path.join(project_root, ".env.secret"), override=True)

# 4) Dodaj katalogi src i agents do ścieżki
sys.path.insert(0, os.path.join(project_root, "ai", "src", "agents"))
sys.path.insert(0, project_root)

# Import klasy PoliticianAgent
from politician_agent import PoliticianAgent


def test_basic_politician_creation():
    print("-> test_basic_politician_creation")
    politician = PoliticianAgent(first_name="Anna", last_name="Nowak")
    assert politician.first_name == "Anna"
    assert politician.last_name == "Nowak"
    print("   OK")


def test_politician_general_beliefs():
    print("-> test_politician_general_beliefs")
    politician = PoliticianAgent(first_name="Tomasz", last_name="Zieliński")
    beliefs = politician.general_beliefs
    print("beliefs:", beliefs)
    print("type:", type(beliefs))
    assert isinstance(beliefs, str) and "Gospodarka" in beliefs
    print("   OK")


def test_politician_answer():
    print("-> test_politician_answer")
    politician = PoliticianAgent(first_name="Karolina", last_name="Mazur")
    answer = politician.answer_question("Co sądzisz o podwyżkach podatków?")
    assert isinstance(answer, str) and len(answer) > 0
    print("   OK")


def main():
    print("=== TESTY POLITICIAN AGENT ===\n")
    try:
        test_basic_politician_creation()
        test_politician_general_beliefs()
        test_politician_answer()
        print("\n✓ Wszystkie testy zakończone pomyślnie!")
    except AssertionError as ae:
        print(f"\n✗ Test nie przeszedł: {ae}")
        raise
    except Exception as e:
        print(f"\n✗ Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
