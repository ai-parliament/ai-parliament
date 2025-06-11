import unittest
from src.api.ai_service import AIService
from src.agents.agent_loader import AgentLoader
from src.agents.supervisor_agent import SupervisorAgent
from src.database.vector_db import VectorDatabase
import os
import dotenv

class TestAIService(unittest.TestCase):
    """
    Test suite for the AI Service component.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        """
        # Load environment variables
        dotenv.load_dotenv()
        
        # Initialize the AI service
        self.ai_service = AIService()
        
        # Test data
        self.party_names = [
            "Civic Platform (PO)",
            "Law and Justice (PiS)",
            "Left (Lewica)"
        ]
        
        self.politicians_per_party = {
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
        
        self.test_topic = "Renewable Energy Subsidies"
    
    def test_create_simulation(self):
        """
        Test creating a simulation with parties and politicians.
        """
        # Create a simulation
        simulation_config = self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Check that the simulation was created successfully
        self.assertIsNotNone(simulation_config)
        self.assertIn("parties", simulation_config)
        self.assertEqual(len(simulation_config["parties"]), 3)
        
        # Check that the parties have the correct names
        party_names = [party["name"] for party in simulation_config["parties"]]
        self.assertIn("Civic Platform", party_names)
        self.assertIn("Law and Justice", party_names)
        self.assertIn("Left", party_names)
        
        # Check that the politicians were added to the parties
        for party in simulation_config["parties"]:
            self.assertGreaterEqual(len(party["politicians"]), 2)
    
    def test_generate_legislation(self):
        """
        Test generating legislation on a topic.
        """
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Check that the legislation was generated successfully
        self.assertIsNotNone(legislation_text)
        self.assertGreater(len(legislation_text), 100)  # Should be a substantial text
        
        # Check that the legislation contains the topic
        self.assertIn("energy", legislation_text.lower())
    
    def test_run_intra_party_deliberation(self):
        """
        Test running the intra-party deliberation phase.
        """
        # Create a simulation first
        self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Run intra-party deliberation
        results = self.ai_service.run_intra_party_deliberation(legislation_text)
        
        # Check that the deliberation ran successfully
        self.assertIsNotNone(results)
        self.assertIn("party_stances", results)
        self.assertIn("legislation_text", results)
        
        # Check that all parties have stances
        for party_name in ["Civic Platform", "Law and Justice", "Left"]:
            self.assertIn(party_name, results["party_stances"])
            self.assertIn("stance", results["party_stances"][party_name])
            self.assertIn("opinions", results["party_stances"][party_name])
    
    def test_run_inter_party_debate(self):
        """
        Test running the inter-party debate phase.
        """
        # Create a simulation first
        self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Run inter-party debate
        results = self.ai_service.run_inter_party_debate(legislation_text)
        
        # Check that the debate ran successfully
        self.assertIsNotNone(results)
        self.assertIn("debate_results", results)
        self.assertIn("legislation_text", results)
        
        # Check that all parties participated in the debate
        for party_name in ["Civic Platform", "Law and Justice", "Left"]:
            self.assertIn(party_name, results["debate_results"])
    
    def test_run_voting(self):
        """
        Test running the voting phase.
        """
        # Create a simulation first
        self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Run voting
        results = self.ai_service.run_voting(legislation_text)
        
        # Check that the voting ran successfully
        self.assertIsNotNone(results)
        self.assertIn("voting_results", results)
        self.assertIn("legislation_text", results)
        
        # Check that the voting results contain the expected fields
        voting_results = results["voting_results"]
        self.assertIn("party_votes", voting_results)
        self.assertIn("total_votes", voting_results)
        self.assertIn("votes_in_favor", voting_results)
        self.assertIn("legislation_passes", voting_results)
        
        # Check that all parties voted
        for party_name in ["Civic Platform", "Law and Justice", "Left"]:
            self.assertIn(party_name, voting_results["party_votes"])
    
    def test_run_full_simulation(self):
        """
        Test running the full simulation.
        """
        # Create a simulation first
        self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Run the full simulation
        results = self.ai_service.run_simulation(legislation_text)
        
        # Check that the simulation ran successfully
        self.assertIsNotNone(results)
        self.assertIn("legislation_text", results)
        self.assertIn("voting_results", results)
        self.assertIn("summary", results)
        self.assertIn("full_results", results)
    
    def test_vector_db_search(self):
        """
        Test searching the vector database.
        """
        # Create a simulation first
        self.ai_service.create_simulation(
            self.party_names,
            self.politicians_per_party
        )
        
        # Generate legislation
        legislation_text = self.ai_service.generate_legislation(self.test_topic)
        
        # Search for legislation
        results = self.ai_service.search_legislation("renewable energy")
        
        # Check that the search returned results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        
        # Search for parties
        results = self.ai_service.search_parties("conservative")
        
        # Check that the search returned results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        
        # Search for politicians
        results = self.ai_service.search_politicians("Tusk")
        
        # Check that the search returned results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        
        # Search for politicians in a specific party
        results = self.ai_service.search_politicians("leader", party_name="Law and Justice")
        
        # Check that the search returned results
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()