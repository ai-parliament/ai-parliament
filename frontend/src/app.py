"""
Streamlit frontend for the AI Parliament system.
"""

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


def setup_page():
    """Set up the Streamlit page."""
    st.set_page_config(
        page_title="AI Parliament",
        page_icon="🏛️",
        layout="wide"
    )
    
    st.title("🏛️ AI Parliament Simulation")
    st.markdown(
        """
        Welcome to the AI Parliament simulation! 
        This application simulates parliamentary deliberation, debate, and voting.
        """
    )


def create_simulation_ui():
    """Create the UI for simulation setup."""
    with st.expander("Simulation Setup", expanded=not st.session_state.simulation_created):
        num_parties = st.number_input("Number of Parties", min_value=1, max_value=10, value=3)
        
        party_names = []
        politicians_per_party = {}
        
        for i in range(num_parties):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                party_name = st.text_input(f"Party {i+1} Name", value=f"Party {i+1}", key=f"party_{i}")
                party_names.append(party_name)
            
            with col2:
                num_politicians = st.number_input(
                    f"Number of Politicians for {party_name}",
                    min_value=1,
                    max_value=5,
                    value=2,
                    key=f"num_pol_{i}"
                )
            
            politicians = []
            for j in range(num_politicians):
                pol_col1, pol_col2 = st.columns(2)
                
                with pol_col1:
                    politician_name = st.text_input(
                        f"Name (Party {i+1}, Politician {j+1})",
                        value=f"Politician {j+1}",
                        key=f"pol_name_{i}_{j}"
                    )
                
                with pol_col2:
                    politician_role = st.text_input(
                        f"Role (Party {i+1}, Politician {j+1})",
                        value=f"Member",
                        key=f"pol_role_{i}_{j}"
                    )
                
                politicians.append({
                    "name": politician_name,
                    "role": politician_role
                })
            
            politicians_per_party[party_name] = politicians
        
        if st.button("Create Simulation"):
            data = {
                "party_names": party_names,
                "politicians_per_party": politicians_per_party
            }
            
            # Call backend API to create simulation
            response = call_backend_api("create_simulation", method="POST", data=data)
            
            if response:
                st.session_state.simulation_created = True
                st.session_state.party_names = party_names
                st.session_state.politicians_per_party = politicians_per_party
                
                st.success("Simulation created successfully!")
                
                # Add to chat
                st.session_state.chat_messages.append({
                    "role": "system",
                    "content": "Simulation created with the following parties:"
                })
                
                for party in response["parties"]:
                    party_info = f"- {party['name']} ({party['acronym']})"
                    politicians_info = "\n".join([f"  - {pol['name']} ({pol['role']})" for pol in party["politicians"]])
                    
                    st.session_state.chat_messages.append({
                        "role": "system",
                        "content": f"{party_info}\n{politicians_info}"
                    })
            else:
                st.error("Failed to create simulation")


def run_simulation_ui():
    """Run the simulation UI."""
    if not st.session_state.simulation_created:
        return
    
    with st.expander("Run Simulation", expanded=True):
        legislation_topic = st.text_input("Enter a topic for legislation (e.g., 'Renewable Energy Subsidies'):")
        
        if st.button("Generate Legislation") and legislation_topic:
            # Call backend API to generate legislation
            response = call_backend_api(
                "generate_legislation", 
                method="POST", 
                data={"topic": legislation_topic}
            )
            
            if response:
                st.session_state.legislation_text = response["legislation_text"]
                
                # Add to chat
                st.session_state.chat_messages.append({
                    "role": "system",
                    "content": f"Generated legislation on topic: {legislation_topic}"
                })
                
                st.session_state.chat_messages.append({
                    "role": "system",
                    "content": f"**Legislation Text:**\n\n{st.session_state.legislation_text}"
                })
                
                st.success("Legislation generated successfully!")
            else:
                st.error("Failed to generate legislation")
        
        if st.session_state.legislation_text:
            st.markdown("### Legislation Text")
            st.text_area("", value=st.session_state.legislation_text, height=200, disabled=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Run Intra-Party Deliberation"):
                    # Call backend API for intra-party deliberation
                    with st.spinner("Running intra-party deliberation..."):
                        response = call_backend_api(
                            "run_intra_party_deliberation", 
                            method="POST", 
                            data={"legislation_text": st.session_state.legislation_text}
                        )
                    
                    if response:
                        st.session_state.intra_party_results = response
                        
                        # Add to chat
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": "**Intra-Party Deliberation Results:**"
                        })
                        
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
                                    "content": f"Position: {stance}"
                                })
                        
                        st.success("Intra-party deliberation completed")
                    else:
                        st.error("Failed to run intra-party deliberation")
            
            with col2:
                if st.button("Run Inter-Party Debate"):
                    # Call backend API for inter-party debate
                    with st.spinner("Running inter-party debate..."):
                        response = call_backend_api(
                            "run_inter_party_debate", 
                            method="POST", 
                            data={"legislation_text": st.session_state.legislation_text}
                        )
                    
                    if response:
                        st.session_state.inter_party_results = response
                        
                        # Add to chat
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": "**Inter-Party Debate Results:**"
                        })
                        
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
                if st.button("Run Voting"):
                    # Call backend API for voting
                    with st.spinner("Running voting..."):
                        response = call_backend_api(
                            "run_voting", 
                            method="POST", 
                            data={"legislation_text": st.session_state.legislation_text}
                        )
                    
                    if response:
                        st.session_state.voting_results = response
                        
                        results = response["voting_results"]
                        
                        # Add to chat
                        st.session_state.chat_messages.append({
                            "role": "system",
                            "content": "**Voting Results:**"
                        })
                        
                        vote_result = f"Total votes: {results['total_votes']}\n"
                        vote_result += f"Votes in favor: {results['votes_in_favor']}\n"
                        vote_result += f"Legislation passes: {'Yes' if results['legislation_passes'] else 'No'}"
                        
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


def display_chat():
    """Display the chat-like interface with simulation results."""
    st.markdown("### Simulation Results")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "system":
                st.markdown(f"**System**: {message['content']}")
            elif message["role"] == "party":
                st.markdown(f"**{message['party']}**: {message['content']}")
            elif message["role"] == "politician":
                st.markdown(f"**{message['politician']} ({message['party']})**: {message['content']}")


def main():
    """Main function for the Streamlit app."""
    initialize_session_state()
    setup_page()
    
    create_simulation_ui()
    run_simulation_ui()
    
    if st.session_state.chat_messages:
        display_chat()


if __name__ == "__main__":
    main()