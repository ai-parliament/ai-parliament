#!/usr/bin/env python3
"""
Skrypt testowy dla PartyAgent
Testuje podstawowe funkcjonalności agenta partii
"""

import sys
import os

# 1) Znajdź katalog z tym skryptem
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2) Wyznacz root projektu (katalog, w którym masz .env.shared/.env.secret)
#    test_party_agent.py leży w ai/src/agents, czyli trzy poziomy wyżej jest root projektu
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

# 3) Wczytaj zmienne środowiskowe z plików .env
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env.shared"))
load_dotenv(os.path.join(project_root, ".env.secret"), override=True)

# 4) Dodaj katalog z agentami (i ew. src) do ścieżki
sys.path.insert(0, os.path.join(project_root, "ai", "src", "agents"))
sys.path.insert(0, project_root)

# Teraz już możesz importować swoje klasy
from party_agent import PartyAgent


def test_basic_party_creation():
    print("-> test_basic_party_creation")
    party = PartyAgent(name="MojaPartia")
    assert party.name == "MojaPartia"
    print("   OK")


def test_party_with_politicians():
    print("-> test_party_with_politicians")
    party = PartyAgent(name="Testowa")
    party.add_politician("Jan Kowalski", role="Przewodniczący")
    assert any(p.name == "Jan Kowalski" for p in party.politicians)
    print("   OK")


def test_legislation_analysis():
    print("-> test_legislation_analysis")
    party = PartyAgent(name="AnalizaPartii")
    summary = party.analyze_legislation("Ustawa o testach")
    assert isinstance(summary, str) and len(summary) > 0
    print("   OK")


def test_party_qa():
    print("-> test_party_qa")
    party = PartyAgent(name="QApartia")
    answer = party.ask("Jakie są cele partii?")
    assert isinstance(answer, str) and "cele" in answer.lower()
    print("   OK")


def main():
    print("=== TESTY PARTY AGENT ===\n")
    try:
        test_basic_party_creation()
        test_party_with_politicians()
        test_legislation_analysis()
        test_party_qa()
        print("\n✓ Wszystkie testy zakończone pomyślnie!")
    except AssertionError as ae:
        print(f"\n✗ Test się nie powiódł: {ae}")
        raise
    except Exception as e:
        print(f"\n✗ Błąd podczas testów: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
