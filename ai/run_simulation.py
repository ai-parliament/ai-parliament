"""
Script to run a simulation using the AI Parliament system.
"""

import os
import dotenv
from src.api.ai_service import AIService

def main():
    """
    Run a simulation of the AI Parliament system.
    """
    # Load environment variables
    dotenv.load_dotenv()
    
    # Initialize the AI service
    ai_service = AIService()
    
    # Define parties and politicians
    party_names = [
        "Civic Platform (PO)",
        "Law and Justice (PiS)",
        "Left (Lewica)"
    ]
    
    politicians_per_party = {
        "Civic Platform (PO)": [
            {"name": "Donald Tusk", "role": "Party Leader"},
            {"name": "Rafał Trzaskowski", "role": "Mayor of Warsaw"}
        ],
        "Law and Justice (PiS)": [
            {"name": "Jarosław Kaczyński", "role": "Party Leader"},
            {"name": "Mateusz Morawiecki", "role": "Former Prime Minister"}
        ],
        "Left (Lewica)": [
            {"name": "Robert Biedroń", "role": "Co-Chair"},
            {"name": "Adrian Zandberg", "role": "Co-Chair"}
        ]
    }
    
    # Create a simulation
    print("Creating simulation...")
    simulation_config = ai_service.create_simulation(
        party_names,
        politicians_per_party
    )
    
    print("\nSimulation created with the following parties:")
    for party in simulation_config["parties"]:
        print(f"- {party['name']} ({party['acronym']})")
        for politician in party["politicians"]:
            print(f"  - {politician['name']} ({politician['role']})")
    
    # Generate legislation
    topic = input("\nEnter a topic for legislation (e.g., 'Renewable Energy Subsidies'): ")
    print(f"\nGenerating legislation on '{topic}'...")
    legislation_text = ai_service.generate_legislation(topic)
    
    print("\nGenerated legislation:")
    print("=" * 80)
    print(legislation_text)
    print("=" * 80)
    
    # Run intra-party deliberation
    print("\nRunning intra-party deliberation...")
    deliberation_results = ai_service.run_intra_party_deliberation(legislation_text)
    
    print("\nParty stances:")
    for party_name, data in deliberation_results["party_stances"].items():
        print(f"\n{party_name}:")
        print("-" * 40)
        print(data["stance"])
        
        print("\nPolitician opinions:")
        for opinion in data["opinions"]:
            print(f"- {opinion['politician']}: {opinion['opinion'][:100]}...")
    
    # Run inter-party debate
    print("\nRunning inter-party debate...")
    debate_results = ai_service.run_inter_party_debate(legislation_text)
    
    print("\nDebate results:")
    for party_name, response in debate_results["debate_results"].items():
        print(f"\n{party_name}:")
        print("-" * 40)
        print(response[:200]  "...")
    
    # Run voting
    print("\nRunning voting...")
    voting_results = ai_service.run_voting(legislation_text)
    
    print("\nVoting results:")
    results = voting_results["voting_results"]
    print(f"Total votes: {results['total_votes']}")
    print(f"Votes in favor: {results['votes_in_favor']}")
    print(f"Legislation passes: {results['legislation_passes']}")
    
    print("\nParty votes:")
    for party_name, vote_data in results["party_votes"].items():
        print(f"- {party_name}: {vote_data['vote']} ({vote_data['num_votes']} votes)")
    
    # Get simulation summary
    print("\nGetting simulation summary...")
    summary = ai_service.get_simulation_summary()
    
    print("\nSimulation summary:")
    print("=" * 80)
    print(summary["summary"])
    print("=" * 80)

if __name__ == "__main__":
    main()