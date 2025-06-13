# scripts/warm_cache.py
"""Pre-populate cache with common politicians and parties"""

from ai.src.agents import PartyAgent, PoliticianAgent
from ai.src.agents.cache_manager import cache_manager
import time

def warm_cache():
    """Warm up the cache with common politicians and parties"""
    
    print("🔥 Warming up cache...")
    
    # Common parties
    parties = [
        ("Platforma Obywatelska", "PO"),
        ("Prawo i Sprawiedliwość", "PiS"),
        ("Lewica", ""),
        ("Polska 2050", "PL2050"),
        ("Konfederacja", "")
    ]
    
    # Common politicians per party
    politicians = {
        "Platforma Obywatelska": [
            {"name": "Donald Tusk", "role": "Przewodniczący"},
            {"name": "Rafał Trzaskowski", "role": "Prezydent Warszawy"},
            {"name": "Ewa Kopacz", "role": "Poseł"}
        ],
        "Prawo i Sprawiedliwość": [
            {"name": "Jarosław Kaczyński", "role": "Prezes"},
            {"name": "Mateusz Morawiecki", "role": "Premier"},
            {"name": "Jacek Sasin", "role": "Minister"}
        ],
        "Lewica": [
            {"name": "Robert Biedroń", "role": "Współprzewodniczący"},
            {"name": "Adrian Zandberg", "role": "Współprzewodniczący"}
        ]
    }
    
    # Warm parties
    for party_name, acronym in parties:
        print(f"\n📊 Warming party: {party_name}")
        party = PartyAgent(party_name, acronym)
        
        # Warm politicians for this party
        if party_name in politicians:
            for pol in politicians[party_name]:
                print(f"  👤 Warming politician: {pol['name']}")
                party.add_politician(pol['name'], pol['role'])
                time.sleep(0.5)  # Be nice to APIs
    
    # Show cache stats
    stats = cache_manager.get_cache_stats()
    print(f"\n📈 Cache statistics:")
    print(f"  - Politicians: {stats['politicians']}")
    print(f"  - Parties: {stats['parties']}")
    print(f"  - Wikipedia: {stats['wikipedia']}")
    print(f"  - Total size: {stats['total_size_mb']:.2f} MB")

if __name__ == "__main__":
    warm_cache()