import os
import json
import requests
import streamlit as st
from config_manager import config


def call_backend_api(endpoint, method="GET", data=None):
    """
    Call the backend API.
    
    Args:
        endpoint: API endpoint to call
        method: HTTP method (GET, POST, etc.)
        data: Data to send (for POST requests)
        
    Returns:
        JSON response from the API
    """
    url = f"{config.backend_api_url}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling backend API: {str(e)}")
        return None


def initialize_session_state():
    """Initialize the session state variables using config manager."""
    defaults = config.get_session_state_defaults()
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def setup_page():
    """Set up the Streamlit page using config manager."""
    st.set_page_config(
        page_title=config.ui_page_title,
        page_icon=config.ui_page_icon,
        layout=config.ui_layout,
        initial_sidebar_state=config.ui_sidebar_state
    )


def sidebar_ui():
    """Create the sidebar UI for configuration using config manager."""
    with st.sidebar:
        st.title(f"{config.ui_page_icon} {config.get_text('titles', 'app_title')}")
        st.markdown(f"## {config.get_text('titles', 'configuration_title')}")
        
        # LLM Configuration Section
        st.markdown(f"#### {config.get_text('sections', 'llm_settings')}")
        
        st.session_state.model_name = st.selectbox(
            config.get_text('labels', 'model_label'), 
            options=config.llm_available_models, 
            index=config.llm_available_models.index(st.session_state.model_name)
        )
        
        st.session_state.temperature = st.slider(
            config.get_text('labels', 'temperature_label'), 
            min_value=config.llm_temperature_range[0], 
            max_value=config.llm_temperature_range[1], 
            value=st.session_state.temperature,
            step=config.llm_temperature_step,
            help=config.get_text('help_texts', 'temperature_help')
        )
        
        st.session_state.max_tokens = st.slider(
            config.get_text('labels', 'max_tokens_label'), 
            min_value=config.llm_max_tokens_range[0], 
            max_value=config.llm_max_tokens_range[1], 
            value=st.session_state.max_tokens,
            step=config.llm_max_tokens_step,
            help=config.get_text('help_texts', 'max_tokens_help')
        )
        
        # Parliament Configuration Section
        st.markdown(f"#### {config.get_text('sections', 'parliament_settings')}")
        
        st.session_state.num_parties = st.number_input(
            config.get_text('labels', 'num_parties_label'), 
            min_value=config.parliament_parties_range[0], 
            max_value=config.parliament_parties_range[1], 
            value=st.session_state.num_parties
        )
        
        # Party and MP Configuration
        st.markdown(f"#### {config.get_text('sections', 'party_configuration')}")
        
        party_names = []
        party_abbreviations = []
        politicians_per_party = {}
        
        # Get default party names from config
        default_party_names = config.get_default_party_names()
        
        for i in range(st.session_state.num_parties):
            # Get default party name for this index or use generic name
            default_party_name = default_party_names[i] if i < len(default_party_names) else f"{config.get_text('defaults', 'party_prefix')} {i+1}"
            default_abbreviation = config.get_default_abbreviation(default_party_name)
            
            with st.expander(f"{default_party_name}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    party_name = st.text_input(
                        config.get_text('labels', 'party_name_label'), 
                        value=default_party_name, 
                        key=f"party_{i}"
                    )
                
                with col2:
                    party_abbreviation = st.text_input(
                        config.get_text('labels', 'abbreviation_label'),
                        value=default_abbreviation,
                        key=f"party_abbr_{i}"
                    )
                
                party_names.append(party_name)
                party_abbreviations.append(party_abbreviation)
                
                # Get default politicians for this party from config
                default_politicians = config.get_default_politicians(default_party_name)
                if not default_politicians and i < len(default_party_names):
                    # Try with the original index-based key if the party name was changed
                    default_politicians = config.get_default_politicians(default_party_names[i])
                
                num_politicians = st.number_input(
                    config.get_text('labels', 'num_mps_label'), 
                    min_value=config.parliament_mps_range[0], 
                    max_value=config.parliament_mps_range[1], 
                    value=len(default_politicians) if default_politicians else st.session_state.num_mps_per_party,
                    key=f"num_pol_{i}"
                )

                st.markdown("---")
                st.markdown(f"##### {config.get_text('sections', 'mps_configuration')}")
                politicians = []
                for j in range(num_politicians):
                    # Get default values for this politician
                    default_name = default_politicians[j]["name"] if j < len(default_politicians) else f"{config.get_text('defaults', 'politician_prefix')} {j+1}"
                    default_role = default_politicians[j]["role"] if j < len(default_politicians) else config.get_text('defaults', 'role')

                    st.markdown(f"**{default_name}**")
                    col1, col2 = st.columns(2)

                    with col1:
                        politician_name = st.text_input(
                            config.get_text('labels', 'politician_name_label'),
                            value=default_name,
                            key=f"pol_name_{i}_{j}"
                        )
                    
                    with col2:
                        politician_role = st.text_input(
                            config.get_text('labels', 'politician_role_label'),
                            value=default_role,
                            key=f"pol_role_{i}_{j}"
                        )
                    
                    politicians.append({
                        "name": politician_name,
                        "role": politician_role
                    })
                    
                    # # Add a separator between MPs
                    # if j < num_politicians - 1:
                    #     st.markdown("---")
                
                politicians_per_party[party_name] = politicians
        
        # Control buttons
        st.markdown(f"#### {config.get_text('titles', 'controls_title')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_button = st.button(config.get_text('buttons', 'start_simulation'), use_container_width=True)
        
        with col2:
            reset_button = st.button(config.get_text('buttons', 'reset'), use_container_width=True)
        
        if start_button:
            data = {
                "party_names": party_names,
                "party_abbreviations": party_abbreviations,
                "politicians_per_party": politicians_per_party,
                "llm_config": {
                    "model_name": st.session_state.model_name,
                    "temperature": st.session_state.temperature,
                    "max_tokens": st.session_state.max_tokens
                }
            }
            
            # Call backend API to create simulation
            response = call_backend_api("create_simulation", method="POST", data=data)
            
            if response:
                st.session_state.simulation_created = True
                st.session_state.party_names = party_names
                st.session_state.party_abbreviations = party_abbreviations
                st.session_state.politicians_per_party = politicians_per_party
                
                st.success(config.get_text('messages', 'success', 'simulation_created'))
                
                # Add individual party creation messages to chat
                for party in response["parties"]:
                    # Make sure acronym exists and is not empty before including it in the message
                    party_name_display = party['name']
                    if 'acronym' in party and party['acronym']:
                        party_name_display = f"{party['name']} ({party['acronym']})"
                    
                    party_info = f"{config.get_text('chat', 'created_party')}: {party_name_display}"
                    politicians_info = "\n".join([f"• {pol['name']} ({pol['role']})" for pol in party["politicians"]])
                    
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": f"{party_info}\n{politicians_info}"
                    })
            else:
                st.error(config.get_text('messages', 'error', 'simulation_failed'))
        
        if reset_button:
            # Reset session state to defaults using config manager
            defaults = config.get_session_state_defaults()
            for key, value in defaults.items():
                st.session_state[key] = value
            st.rerun()


def main_screen():
    """Create the main screen UI using config manager."""
    if not st.session_state.simulation_created:
        st.markdown(config.get_text('welcome', 'message'))
        return
    
    # Main content area with question input and chat display
    st.markdown(f"## {config.get_text('titles', 'session_title')}")
    
    # Topic Input
    with st.container():
        st.markdown(config.get_text('sections', 'topic_input_section'))
        
        # Use a form for the topic input
        with st.form(key="topic_form"):
            legislation_topic = st.text_input(
                config.get_text('labels', 'topic_input_label'),
                placeholder=config.get_text('placeholders', 'topic_input_placeholder'),
                help=config.get_text('help_texts', 'topic_input_help')
            )
            
            submit_button = st.form_submit_button(config.get_text('buttons', 'start_discussion'), use_container_width=True)
            
            if submit_button and legislation_topic:
                # Call backend API to generate legislation
                with st.spinner(config.get_text('messages', 'loading', 'preparing_topic')):
                    response = call_backend_api(
                        "generate_legislation", 
                        method="POST", 
                        data={
                            "topic": legislation_topic,
                            "llm_config": {
                                "model_name": st.session_state.model_name,
                                "temperature": st.session_state.temperature,
                                "max_tokens": st.session_state.max_tokens
                            }
                        }
                    )
                
                if response:
                    st.session_state.legislation_text = response["legislation_text"]
                    
                    # Add to chat
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": f"{config.get_text('chat', 'starting_discussion')}: **{legislation_topic}**"
                    })
                    
                    st.success(config.get_text('messages', 'success', 'topic_set'))
                else:
                    st.error(config.get_text('messages', 'error', 'topic_failed'))
    
    # Only show simulation actions when legislation is available
    if st.session_state.legislation_text:
        # Action buttons for simulation steps
        st.markdown(f"### {config.get_text('sections', 'simulation_actions')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(config.get_text('buttons', 'run_intra_party'), use_container_width=True):
                # Call backend API for intra-party deliberation
                with st.spinner(config.get_text('messages', 'loading', 'running_intra_party')):
                    response = call_backend_api(
                        "run_intra_party_deliberation", 
                        method="POST", 
                        data={
                            "legislation_text": st.session_state.legislation_text,
                            "llm_config": {
                                "model_name": st.session_state.model_name,
                                "temperature": st.session_state.temperature,
                                "max_tokens": st.session_state.max_tokens
                            }
                        }
                    )
                
                if response:
                    st.session_state.intra_party_results = response
                    
                    # Add party stances directly without the header
                    for party_name, data in response["party_stances"].items():
                        st.session_state.chat_messages.append({
                            "role": "party",
                            "party": party_name,
                            "content": f"{config.get_text('chat', 'party_stance')} {data['stance']}"
                        })
                        
                        for politician_name, stance in data["opinions"].items():
                            st.session_state.chat_messages.append({
                                "role": "politician",
                                "party": party_name,
                                "politician": politician_name,
                                "content": stance
                            })
                    
                    st.success(config.get_text('messages', 'success', 'intra_party_completed'))
                else:
                    st.error(config.get_text('messages', 'error', 'intra_party_failed'))
        
        with col2:
            if st.button(config.get_text('buttons', 'run_inter_party'), use_container_width=True):
                # Call backend API for inter-party debate
                with st.spinner(config.get_text('messages', 'loading', 'running_inter_party')):
                    response = call_backend_api(
                        "run_inter_party_debate", 
                        method="POST", 
                        data={
                            "legislation_text": st.session_state.legislation_text,
                            "llm_config": {
                                "model_name": st.session_state.model_name,
                                "temperature": st.session_state.temperature,
                                "max_tokens": st.session_state.max_tokens
                            }
                        }
                    )
                
                if response:
                    st.session_state.inter_party_results = response
                    
                    # Add politician speeches if available
                    if "debate_speeches" in response and response["debate_speeches"]:
                        for speech in response["debate_speeches"]:
                            st.session_state.chat_messages.append({
                                "role": "politician",
                                "politician": speech["politician"],
                                "party": speech["party"],
                                "content": speech["content"],
                                "supporting": speech["supporting"]
                            })
                    
                    # Add debate results directly without the header
                    for party_name, response_text in response["debate_results"].items():
                        st.session_state.chat_messages.append({
                            "role": "party",
                            "party": party_name,
                            "content": response_text
                        })
                    
                    st.success(config.get_text('messages', 'success', 'inter_party_completed'))
                else:
                    st.error(config.get_text('messages', 'error', 'inter_party_failed'))
        
        with col3:
            if st.button(config.get_text('buttons', 'run_voting'), use_container_width=True):
                # Call backend API for voting
                with st.spinner(config.get_text('messages', 'loading', 'running_voting')):
                    response = call_backend_api(
                        "run_voting", 
                        method="POST", 
                        data={
                            "legislation_text": st.session_state.legislation_text,
                            "llm_config": {
                                "model_name": st.session_state.model_name,
                                "temperature": st.session_state.temperature,
                                "max_tokens": st.session_state.max_tokens
                            }
                        }
                    )
                
                if response:
                    st.session_state.voting_results = response
                    results = response["voting_results"]
                    
                    # Add voting results directly without the header
                    vote_result = f"{config.get_text('chat', 'voting_results')}\n{config.get_text('chat', 'total_votes')} {results['total_votes']}\n"
                    vote_result += f"{config.get_text('chat', 'votes_in_favor')} {results['votes_in_favor']}\n"
                    vote_result += f"{config.get_text('chat', 'legislation_passes')} {config.get_text('chat', 'yes') if results['legislation_passes'] else config.get_text('chat', 'no')}"
                    
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": vote_result
                    })
                    
                    for party_name, vote_data in results["party_votes"].items():
                        st.session_state.chat_messages.append({
                            "role": "party",
                            "party": party_name,
                            "content": f"{config.get_text('chat', 'vote')}: {vote_data['vote']} ({vote_data['num_votes']} {config.get_text('chat', 'votes')})"
                        })
                    
                    st.success(config.get_text('messages', 'success', 'voting_completed'))
                    
                    # Get simulation summary
                    summary_response = call_backend_api("get_simulation_summary", method="GET")
                    
                    if summary_response:
                        st.session_state.simulation_summary = summary_response
                        
                        # Add to chat
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": config.get_text('chat', 'simulation_summary')
                        })
                        
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": summary_response["summary"]
                        })
                else:
                    st.error(config.get_text('messages', 'error', 'voting_failed'))
    
    # Parliament Debate Chat Display
    display_chat()


def display_chat():
    """Display the chat-like interface with simulation results."""
    if not st.session_state.chat_messages:
        return
    
    st.markdown(f"### {config.get_text('sections', 'parliamentary_debate')}")
    
    # Create a styled chat container
    chat_container = st.container()
    
    with chat_container:
        # Custom CSS for chat bubbles with improved markdown rendering
        st.markdown(config.get_chat_css(), unsafe_allow_html=True)
        
        # Group all messages by type
        system_messages = []
        politician_messages = []
        party_messages = []
        summary_messages = []
        
        # First, categorize all messages
        for message in st.session_state.chat_messages:
            # Handle summary messages separately
            if message["role"] == "system" and config.get_text('chat', 'simulation_summary') in message.get("content", ""):
                summary_messages.append(message)
                continue
            
            if message["role"] == "system":
                system_messages.append(message)
            elif message["role"] == "politician":
                politician_messages.append(message)
            elif message["role"] == "party":
                party_messages.append(message)
        
        # Display system messages first
        if system_messages:
            st.markdown(f"#### {config.get_text('sections', 'system_announcements')}")
            for message in system_messages:
                st.markdown(f"""
                <div class="chat-message system-message">
                    <div class="message-header">{config.get_text('defaults', 'system')}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            # Display politician messages before party messages
        if politician_messages:
            st.markdown(f"#### {config.get_text('sections', 'politician_speeches')}")
            for message in politician_messages:
    
                # Find the abbreviation for this party
                party_abbr = ""
                if 'party' in message:
                    party_name = message['party']
                    if hasattr(st.session_state, 'party_abbreviations') and st.session_state.party_abbreviations:
                        try:
                            idx = st.session_state.party_names.index(party_name)
                            if idx < len(st.session_state.party_abbreviations):
                                party_abbr = st.session_state.party_abbreviations[idx]
                        except ValueError:
                            pass
                
                party_info = message['party']
                if party_abbr:
                    party_info = f"{message['party']} ({party_abbr})"
                
                # Get stance information
                stance_info = ""
                if 'supporting' in message:
                    stance_info = "FOR" if message['supporting'] else "AGAINST"
                
                st.markdown(f"""
                <div class="chat-message politician-message">
                    <div class="message-header">{message['politician']} ({party_info}) - {stance_info}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Display party messages last
        if party_messages:
            st.markdown("#### 🏢 Party Statements")
            for message in party_messages:
                # Find the abbreviation for this party
                party_abbr = ""
                if 'party' in message:
                    party_name = message['party']
                    if hasattr(st.session_state, 'party_abbreviations') and st.session_state.party_abbreviations:
                        try:
                            idx = st.session_state.party_names.index(party_name)
                            if idx < len(st.session_state.party_abbreviations):
                                party_abbr = st.session_state.party_abbreviations[idx]
                        except ValueError:
                            pass
                
                party_header = message['party']
                if party_abbr:
                    party_header = f"{message['party']} ({party_abbr})"
                
                st.markdown(f"""
                <div class="chat-message party-message">
                    <div class="message-header">{party_header}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Display summary if available, only once at the end
    if st.session_state.simulation_summary:
        st.markdown("## 📝 OFFICIAL PARLIAMENTARY ANNOUNCEMENT")
        
        # Count votes for the vote tally
        for_count = 0
        against_count = 0
        
        # Track politicians who have already voted to avoid counting twice
        counted_politicians = set()
        
        # Check both intra-party and debate speeches (where 'supporting' is explicitly set)
        for message in st.session_state.chat_messages:
            if message['role'] == 'politician':
                politician_id = f"{message['politician']}_{message['party']}"
                
                # Skip if we've already counted this politician
                if politician_id in counted_politicians:
                    continue
                    
                # If the message has explicit support indicator
                if 'supporting' in message:
                    counted_politicians.add(politician_id)
                    if message['supporting']:
                        for_count += 1
                    else:
                        against_count += 1
        
        total_votes = for_count + against_count
        for_percentage = (for_count / total_votes * 100) if total_votes > 0 else 0
        against_percentage = (against_count / total_votes * 100) if total_votes > 0 else 0
        
        vote_summary_html = f"""
        <div style="
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            background-color: #f8f9fa;
            margin-top: 15px;
            margin-bottom: 15px;
        ">
            <h4 style="border-bottom: 1px solid #dee2e6; padding-bottom: 8px; margin-bottom: 12px;">
                Vote Tally
            </h4>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <div><strong>FOR:</strong> {for_count} ({for_percentage:.1f}%)</div>
                <div><strong>AGAINST:</strong> {against_count} ({against_percentage:.1f}%)</div>
                <div><strong>TOTAL VOTES:</strong> {total_votes}</div>
            </div>
        </div>
        """
        
        # Create a styled box for the summary
        st.markdown(f"""
        <div style="
            border: 2px solid #0068c9; 
            border-radius: 10px; 
            padding: 20px; 
            background-color: #f8f9fa;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            margin-bottom: 30px;
        ">
            <h3 style="color: #0068c9; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; margin-bottom: 15px;">
                🏛️ Final Summary of Parliamentary Proceedings
            </h3>
            <div style="font-size: 16px; line-height: 1.6;">
                {st.session_state.simulation_summary["summary"]}
            </div>
            {vote_summary_html}
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main function for the Streamlit app."""
    initialize_session_state()
    setup_page()
    
    # Create the sidebar
    sidebar_ui()
    
    # Create the main screen
    main_screen()


if __name__ == "__main__":
    main()