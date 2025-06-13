# ai/src/agents/parallel_loader.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import time

class ParallelLoader:
    @staticmethod
    def load_parties_parallel(parties_config: List[Dict]) -> List[PartyAgent]:
        """Load multiple parties in parallel"""
        parties = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit party creation tasks
            future_to_party = {
                executor.submit(
                    PartyAgent,
                    config['name'],
                    config.get('acronym', '')
                ): config for config in parties_config
            }
            
            # Collect results
            for future in as_completed(future_to_party):
                config = future_to_party[future]
                try:
                    party = future.result()
                    parties.append(party)
                    print(f"✅ Loaded party: {config['name']}")
                except Exception as e:
                    print(f"❌ Error loading party {config['name']}: {e}")
        
        print(f"⏱️ Loaded {len(parties)} parties in {time.time() - start_time:.2f}s")
        return parties
    
    @staticmethod
    def load_politicians_for_party_parallel(party: PartyAgent, politicians_config: List[Dict]):
        """Load politicians for a party in parallel"""
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for pol_config in politicians_config:
                future = executor.submit(
                    party.add_politician,
                    pol_config['name'],
                    pol_config.get('role', '')
                )
                futures.append(future)
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"❌ Error adding politician: {e}")
        
        print(f"⏱️ Added {len(politicians_config)} politicians in {time.time() - start_time:.2f}s")