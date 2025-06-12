import os
import json
import requests
import streamlit as st

# Backend API URL (will come from environment in Docker)
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8000/api")


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
    url = f"{BACKEND_API_URL}/{endpoint}"
    
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
    """Initialize the session state variables."""
    if "simulation_created" not in st.session_state:
        st.session_state.simulation_created = False
    
    if "party_names" not in st.session_state:
        st.session_state.party_names = []
    
    if "party_abbreviations" not in st.session_state:
        st.session_state.party_abbreviations = []
    
    if "politicians_per_party" not in st.session_state:
        st.session_state.politicians_per_party = {}
    
    if "legislation_text" not in st.session_state:
        st.session_state.legislation_text = ""
    
    if "intra_party_results" not in st.session_state:
        st.session_state.intra_party_results = None
    
    if "inter_party_results" not in st.session_state:
        st.session_state.inter_party_results = None
    
    if "voting_results" not in st.session_state:
        st.session_state.voting_results = None
    
    if "simulation_summary" not in st.session_state:
        st.session_state.simulation_summary = None
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Initialize LLM configuration parameters
    if "model_name" not in st.session_state:
        st.session_state.model_name = "gpt-4"
    
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7
    
    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 2000
    
    # Initialize number of parties and MPs
    if "num_parties" not in st.session_state:
        st.session_state.num_parties = 2
    
    if "num_mps_per_party" not in st.session_state:
        st.session_state.num_mps_per_party = 2
        
    # Initialize default party and politician names
    if "default_party_data" not in st.session_state:
        st.session_state.default_party_data = {
            "Prawo i Sprawiedliwosc": [
                {"name": "Jaroslaw Kaczynski", "role": "Chairman"},
                {"name": "Antoni Macierewicz", "role": "Member"}
            ],
            "Koalicja Obywatelska": [
                {"name": "Donald Tusk", "role": "Chairman"},
                {"name": "Rafal Trzaskowski", "role": "Member"}
            ]
        }


def setup_page():
    """Set up the Streamlit page."""
    st.set_page_config(
        page_title="AI Parliament",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def sidebar_ui():
    """Create the sidebar UI for configuration."""
    with st.sidebar:
        st.title("🏛️ AI Parliament")
        st.markdown("## ⚙️ Configuration")
        
        # LLM Configuration Section
        st.markdown("#### 🤖 LLM Settings")
        
        model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        st.session_state.model_name = st.selectbox(
            "Model", 
            options=model_options, 
            index=model_options.index(st.session_state.model_name)
        )
        
        st.session_state.temperature = st.slider(
            "Temperature", 
            min_value=0.0, 
            max_value=1.0, 
            value=st.session_state.temperature,
            step=0.1,
            help="Controls randomness. Lower values are more deterministic."
        )
        
        st.session_state.max_tokens = st.slider(
            "Max Tokens", 
            min_value=500, 
            max_value=4000, 
            value=st.session_state.max_tokens,
            step=100,
            help="Maximum number of tokens to generate per response."
        )
        
        # Parliament Configuration Section
        st.markdown("#### 🏛️ Parliament Settings")
        
        st.session_state.num_parties = st.number_input(
            "Number of Parties", 
            min_value=1, 
            max_value=10, 
            value=st.session_state.num_parties
        )
        
        # Party and MP Configuration
        st.markdown("#### 🏢 Party Configuration")
        
        party_names = []
        party_abbreviations = []
        politicians_per_party = {}
        
        # Get default party names
        default_party_names = list(st.session_state.default_party_data.keys())
        default_party_abbreviations = {
            "Prawo i Sprawiedliwosc": "PiS",
            "Koalicja Obywatelska": "KO"
        }
        
        for i in range(st.session_state.num_parties):
            # Get default party name for this index or use generic name
            default_party_name = default_party_names[i] if i < len(default_party_names) else f"Party {i+1}"
            default_abbreviation = default_party_abbreviations.get(default_party_name, "")
            
            with st.expander(f"{default_party_name}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    party_name = st.text_input(
                        "Party Name", 
                        value=default_party_name, 
                        key=f"party_{i}"
                    )
                
                with col2:
                    party_abbreviation = st.text_input(
                        "Abbreviation",
                        value=default_abbreviation,
                        key=f"party_abbr_{i}"
                    )
                
                party_names.append(party_name)
                party_abbreviations.append(party_abbreviation)
                
                # Get default politicians for this party
                default_politicians = st.session_state.default_party_data.get(default_party_name, [])
                if not default_politicians and i < len(default_party_names):
                    # Try with the original index-based key if the party name was changed
                    default_politicians = st.session_state.default_party_data.get(default_party_names[i], [])
                
                num_politicians = st.number_input(
                    "Number of MPs", 
                    min_value=1, 
                    max_value=5, 
                    value=len(default_politicians) if default_politicians else st.session_state.num_mps_per_party,
                    key=f"num_pol_{i}"
                )

                st.markdown("---")
                st.markdown("##### 👥 MPs Configuration")
                politicians = []
                for j in range(num_politicians):
                    # Get default values for this politician
                    default_name = default_politicians[j]["name"] if j < len(default_politicians) else f"Politician {j+1}"
                    default_role = default_politicians[j]["role"] if j < len(default_politicians) else "Member"

                    st.markdown(f"**{default_name}**")
                    col1, col2 = st.columns(2)

                    with col1:
                        politician_name = st.text_input(
                            "Name",
                            value=default_name,
                            key=f"pol_name_{i}_{j}"
                        )
                    
                    with col2:
                        politician_role = st.text_input(
                            "Role",
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
        st.markdown("#### 🎮 Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_button = st.button("Start Simulation", use_container_width=True)
        
        with col2:
            reset_button = st.button("Reset", use_container_width=True)
        
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
                
                st.success("Simulation created successfully!")
                
                # Add individual party creation messages to chat
                for party in response["parties"]:
                    # Make sure acronym exists and is not empty before including it in the message
                    party_name_display = party['name']
                    if 'acronym' in party and party['acronym']:
                        party_name_display = f"{party['name']} ({party['acronym']})"
                    
                    party_info = f"Created party: {party_name_display}"
                    politicians_info = "\n".join([f"• {pol['name']} ({pol['role']})" for pol in party["politicians"]])
                    
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": f"{party_info}\n{politicians_info}"
                    })
            else:
                st.error("Failed to create simulation")
        
        if reset_button:
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            initialize_session_state()
            st.experimental_rerun()


def main_screen():
    """Create the main screen UI."""
    if not st.session_state.simulation_created:
        st.markdown("""
        ## Welcome to AI Parliament
        
        Configure your parliament in the sidebar and click "Start Simulation" to begin.
        
        This application simulates parliamentary deliberation, debate, and voting on legislation topics 
        using AI models to emulate different parties and politicians.
        """)
        
        return
    
    # Main content area with question input and chat display
    st.markdown("## AI Parliament Session")
    
    # Topic Input
    with st.container():
        st.markdown("### Enter a topic for parliamentary discussion")
        
        # Use a form for the topic input
        with st.form(key="topic_form"):
            legislation_topic = st.text_input(
                "Topic for parliamentary discussion",
                placeholder="e.g., 'Renewable Energy Subsidies', 'Privacy Regulation Reform', 'Education Budget'...",
                help="Enter a topic or question for the parliament to discuss and vote on."
            )
            
            submit_button = st.form_submit_button("Start Discussion", use_container_width=True)
            
            if submit_button and legislation_topic:
                # Call backend API to generate legislation
                with st.spinner("Preparing discussion topic..."):
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
                        "content": f"Starting parliamentary discussion on topic: **{legislation_topic}**"
                    })
                    
                    st.success("Discussion topic set successfully!")
                else:
                    st.error("Failed to set discussion topic")
    
    # Only show simulation actions when legislation is available
    if st.session_state.legislation_text:
        # Action buttons for simulation steps
        st.markdown("### Simulation Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Run Intra-Party Deliberation", use_container_width=True):
                # Call backend API for intra-party deliberation
                with st.spinner("Running intra-party deliberation..."):
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
                            "content": f"**Party Stance:** {data['stance']}"
                        })
                        
                        for politician_name, stance in data["opinions"].items():
                            st.session_state.chat_messages.append({
                                "role": "politician",
                                "party": party_name,
                                "politician": politician_name,
                                "content": stance
                            })
                    
                    st.success("Intra-party deliberation completed")
                else:
                    st.error("Failed to run intra-party deliberation")
        
        with col2:
            if st.button("Run Inter-Party Debate", use_container_width=True):
                # Call backend API for inter-party debate
                with st.spinner("Running inter-party debate..."):
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
                    
                    # Add debate results directly without the header
                    for party_name, response_text in response["debate_results"].items():
                        st.session_state.chat_messages.append({
                            "role": "party",
                            "party": party_name,
                            "content": response_text
                        })
                    
                    st.success("Inter-party debate completed")
                else:
                    st.error("Failed to run inter-party debate")
        
        with col3:
            if st.button("Run Voting", use_container_width=True):
                # Call backend API for voting
                with st.spinner("Running voting..."):
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
                    vote_result = f"📊 **Voting Results:**\nTotal votes: {results['total_votes']}\n"
                    vote_result += f"Votes in favor: {results['votes_in_favor']}\n"
                    vote_result += f"Legislation passes: {'Yes ✅' if results['legislation_passes'] else 'No ❌'}"
                    
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": vote_result
                    })
                    
                    for party_name, vote_data in results["party_votes"].items():
                        st.session_state.chat_messages.append({
                            "role": "party",
                            "party": party_name,
                            "content": f"Vote: {vote_data['vote']} ({vote_data['num_votes']} votes)"
                        })
                    
                    st.success("Voting completed")
                    
                    # Get simulation summary
                    summary_response = call_backend_api("get_simulation_summary", method="GET")
                    
                    if summary_response:
                        st.session_state.simulation_summary = summary_response
                        
                        # Add to chat
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": "**Simulation Summary:**"
                        })
                        
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": summary_response["summary"]
                        })
                else:
                    st.error("Failed to run voting")
    
    # Parliament Debate Chat Display
    display_chat()


def display_chat():
    """Display the chat-like interface with simulation results."""
    if not st.session_state.chat_messages:
        return
    
    st.markdown("### Parliamentary Debate")
    
    # Create a styled chat container
    chat_container = st.container()
    
    with chat_container:
        # Custom CSS for chat bubbles with improved markdown rendering
        st.markdown("""
        <style>
        .chat-message {
            padding: 1.5rem; 
            border-radius: 0.5rem; 
            margin-bottom: 1rem; 
            display: flex;
            flex-direction: column;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .system-message {
            background-color: #f0f2f6;
            border-left: 5px solid #4e8cff;
        }
        .party-message {
            background-color: #e6f3ff;
            border-left: 5px solid #0068c9;
        }
        .politician-message {
            background-color: #f5f5f5;
            border-left: 5px solid #ff9500;
        }
        .message-header {
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #333;
            font-size: 1.1em;
        }
        .message-content {
            margin-top: 0.5rem;
            white-space: pre-wrap;
            line-height: 1.5;
        }
        .message-content p {
            margin-bottom: 0.8rem;
        }
        h4 {
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #eee;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Group all messages by type
        system_messages = []
        politician_messages = []
        party_messages = []
        summary_messages = []
        
        # First, categorize all messages
        for message in st.session_state.chat_messages:
            # Handle summary messages separately
            if message["role"] == "system" and "Simulation Summary" in message.get("content", ""):
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
            st.markdown("#### 📢 System Announcements")
            for message in system_messages:
                st.markdown(f"""
                <div class="chat-message system-message">
                    <div class="message-header">System</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            # Display politician messages before party messages
        if politician_messages:
            st.markdown("#### 👥 Politician Speeches")
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
                
                st.markdown(f"""
                <div class="chat-message politician-message">
                    <div class="message-header">{message['politician']} ({party_info})</div>
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
    if st.session_state.simulation_summary and not summary_messages:
        st.markdown("## 📝 OFFICIAL PARLIAMENTARY ANNOUNCEMENT")
        # Create a styled box for the summary
        st.markdown("""
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
                {0}
            </div>
        </div>
        """.format(st.session_state.simulation_summary["summary"]), unsafe_allow_html=True)


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