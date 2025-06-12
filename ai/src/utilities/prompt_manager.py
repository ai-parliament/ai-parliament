"""
Prompt Manager for AI Parliament

This module provides a centralized way to manage prompts used by the various agents in the system.
It loads prompts from a YAML file and provides methods to retrieve and format them.
If a prompt is not found in the YAML file, it falls back to default prompts.
"""

import os
import yaml
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """
    Manages the loading and formatting of prompts used throughout the AI Parliament system.
    """
    
    # Default prompts to use when prompts aren't found in the YAML file
    DEFAULT_PROMPTS = {
        # Politician Agent Prompts
        "politician": {
            "system_prompt": """
            You are a politician named {full_name}. You are a member of {party_name}.
            You are participating in a discussion with other politicians.
            You respond based on your own political views and take into account what others have said.
            
            Here is context about your political views:
            {beliefs}
            
            When responding:
            1. Stay in character as {full_name}
            2. Be consistent with your political views
            3. Be persuasive but respectful
            4. Use a formal, parliamentary style of speech
            """,
            
            "beliefs_prompt": """
            What are the political views of {full_name}?
            Focus ONLY on their political views - do not include biographical information, dates, positions, or trivia.
            I'm only interested in what they think about political, economic, and social issues.
            List them in the following format:
            
            1. Economy:
            2. Foreign policy:
            3. Social policy:
            4. Worldview issues:
            
            ALL of these positions MUST exist. If you can't find explicit information about a position,
            try to deduce its content based on the politician's general views.
            """,
            
            "legislation_opinion_prompt": """
            Proposed legislation: {legislation_text}

            Express your opinion on this proposal as MP {full_name}.
            Do you support this legislation? What are your arguments?
            """
        },
        
        # Party Agent Prompts
        "party": {
            "system_prompt": """
            You are the leader of the political party {party_name} ({party_acronym}).

            Party information:
            {party_info}

            Your task is to represent the party's position on various issues.
            When responding:
            1. Stay consistent with the party's ideology and platform
            2. Consider the opinions of party members
            3. Be persuasive but realistic
            4. Use a formal, parliamentary style of speech
            """,
            
            "stance_prompt": """
            You are the leader of the {party_name} party ({party_acronym}).
            Here are the opinions of your party members on the proposed legislation:

            {discussion_summary}

            Formulate a concise party position on this legislation.
            """,
            
            "question_prompt": """
            As the {party_name} party, answer the following question: {question}
            """
        },
        
        # Supervisor Agent Prompts
        "supervisor": {
            "system_prompt": """
            You are the supervisor of a parliamentary simulation system.
            Your role is to oversee the decision-making process and provide objective analysis.
            
            You should:
            1. Maintain neutrality and objectivity
            2. Provide clear summaries of complex political processes
            3. Explain why certain decisions were made
            4. Highlight key arguments from different parties
            
            When responding, use a formal, analytical tone appropriate for political analysis.
            """,
            
            "summary_prompt": """
            Summarize the results of the parliamentary simulation on the following legislation:
            
            Legislation: {legislation_text}
            
            Voting results:
            - Total votes: {total_votes}
            - Votes in favor: {votes_in_favor}
            - Votes against: {votes_against}
            - Abstained: {abstained}
            - Legislation passes: {legislation_passes}
            
            Party votes:
            {party_votes_formatted}
            
            {party_arguments_text}
            
            Provide a concise summary of the simulation, including the key arguments from each party
            and why the legislation passed or failed.
            """
        },
        
        # Simulation Prompts
        "simulation": {
            # Party Discussion Prompts
            "party_discussion.gather_opinions_prompt": """
            Bill draft: {legislation_text}
            
            As {politician_name}, express your opinion (2-3 sentences).
            Start with "I SUPPORT" or "I DO NOT SUPPORT", then provide your reasoning.
            """,
            
            "party_discussion.conduct_debate_prompt": """
            Opinions of party colleagues about the bill:
            {opinions_text}
            
            As {politician_name}, briefly (1-2 sentences) respond to the discussion.
            You can maintain your opinion or change it.
            """,
            
            "party_discussion.formulate_position_prompt": """
            As the leader of {party_name} party, summarize the discussion about the bill:
            {legislation_text}
            
            {full_discussion}
            
            Answer in this format:
            POSITION: [SUPPORTS or DOES NOT SUPPORT]
            ARGUMENT 1: [main argument]
            ARGUMENT 2: [second argument]
            ARGUMENT 3: [third argument]
            """,
            
            # Inter-Party Debate Prompts
            "inter_party_debate.opening_statement_prompt": """
            As {speaker_name} from the {party_name} party, present your party's position
            on the following bill:
            {legislation_text}
            
            Focus on the main arguments of your party (2-3 sentences).
            Begin with a clear statement whether you support or oppose the bill.
            """,
            
            "inter_party_debate.response_prompt": """
            As {speaker_name} from the {party_name} party, respond to the arguments from other parties.
            
            Recent arguments in the debate:
            {recent_arguments}
            
            Specifically address the argument made by {target_speaker} ({target_party}).
            Your response should be specific and substantive (2-3 sentences).
            """,
            
            "inter_party_debate.closing_statement_prompt": """
            As the leader of the {party_name} party, summarize the debate on the following bill:
            {legislation_text}
            
            Consider the main arguments presented during the debate.
            Confirm your party's final position (1-2 sentences).
            End with a clear statement: "The {party_name} party VOTES FOR/AGAINST the bill."
            """,
            
            # Voting System Prompts
            "voting_system.vote_prompt": """
            As {politician_name}, you must now cast your vote.
            Your party's official position is: {party_position}.
            
            Do you vote according to the party line, or do you have a different opinion?
            Answer with ONLY one word: FOR, AGAINST, or ABSTAIN
            """
        }
    }
    
    def __init__(self, prompts_file_path: Optional[str] = None):
        """
        Initialize the prompt manager by loading prompts from the YAML file.
        
        Args:
            prompts_file_path: Optional custom path to the prompts YAML file.
                              If not provided, defaults to the prompts.yml in the same directory.
        """
        if prompts_file_path is None:
            # Get the directory where this file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the src directory
            src_dir = os.path.dirname(current_dir)
            # Default prompts file path
            prompts_file_path = os.path.join(src_dir, 'prompts.yml')
        
        self.prompts_file_path = prompts_file_path
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, Any]:
        """
        Load the prompts from the YAML file.
        
        Returns:
            A dictionary containing all prompts from the YAML file.
        """
        try:
            with open(self.prompts_file_path, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
                logger.info(f"Successfully loaded prompts from {self.prompts_file_path}")
                return prompts
        except Exception as e:
            logger.error(f"Error loading prompts from {self.prompts_file_path}: {e}")
            # Return empty dict if file cannot be loaded
            return {}
    
    def get_prompt(self, agent_type: str, prompt_type: str) -> Optional[str]:
        """
        Get a prompt by agent type and prompt type.
        If the prompt is not found in the YAML file, return the default prompt.
        
        Args:
            agent_type: The type of agent (e.g., 'politician', 'party', 'supervisor')
            prompt_type: The type of prompt (e.g., 'system_prompt', 'beliefs_prompt')
            
        Returns:
            The prompt as a string, or None if the prompt is not found in both YAML and defaults.
        """
        try:
            # Try to get the prompt from the loaded YAML
            yaml_prompt = self.prompts.get(agent_type, {}).get(prompt_type)
            if yaml_prompt is not None:
                return yaml_prompt
            
            # If not found in YAML, try to get from defaults
            default_agent_prompts = self.DEFAULT_PROMPTS.get(agent_type, {})
            default_prompt = default_agent_prompts.get(prompt_type)
            
            if default_prompt is None:
                logger.warning(f"Prompt not found for agent_type={agent_type}, prompt_type={prompt_type}")
            
            return default_prompt
        except (KeyError, AttributeError) as e:
            logger.warning(f"Error retrieving prompt for agent_type={agent_type}, prompt_type={prompt_type}: {e}")
            return None
    
    def format_prompt(self, agent_type: str, prompt_type: str, **kwargs) -> Optional[str]:
        """
        Get a prompt and format it with the provided arguments.
        
        Args:
            agent_type: The type of agent (e.g., 'politician', 'party', 'supervisor')
            prompt_type: The type of prompt (e.g., 'system_prompt', 'beliefs_prompt')
            **kwargs: The arguments to format the prompt with
            
        Returns:
            The formatted prompt as a string, or None if the prompt is not found.
        """
        prompt_template = self.get_prompt(agent_type, prompt_type)
        if prompt_template is None:
            return None
        
        try:
            # Remove leading/trailing whitespace for cleaner output
            return prompt_template.strip().format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing key {e} when formatting prompt {agent_type}.{prompt_type}")
            return prompt_template.strip()  # Return unformatted template in case of error
        except Exception as e:
            logger.error(f"Error formatting prompt {agent_type}.{prompt_type}: {e}")
            return None
    
    def reload_prompts(self) -> bool:
        """
        Reload the prompts from the YAML file.
        
        Returns:
            True if prompts were successfully reloaded, False otherwise.
        """
        try:
            self.prompts = self._load_prompts()
            return True
        except Exception as e:
            logger.error(f"Failed to reload prompts: {e}")
            return False