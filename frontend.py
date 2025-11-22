import streamlit as st
import requests
import os
import json
import time

# --- Configuration ---
# You MUST set these environment variables before running the application:
# 1. WATSONX_ORCHESTRATE_ENDPOINT: The URL to your Orchestrate chat completions endpoint.
#    e.g., "https://orchestrate.ibm.cloud/api/v1/orchestrate/AGENT_ID/chat/completions"
# 2. WATSONX_API_KEY: Your IBM Cloud/watsonx API key.
# 3. WATSONX_PROJECT_ID: Your watsonx Project ID (if required by your agent).
# You can set them in your terminal:
# export WATSONX_ORCHESTRATE_ENDPOINT="<YOUR_ENDPOINT>"
# export WATSONX_API_KEY="<YOUR_API_KEY>"

# Load configuration from environment variables
ORCHESTRATE_ENDPOINT = os.getenv("WATSONX_ORCHESTRATE_ENDPOINT")
API_KEY = os.getenv("WATSONX_API_KEY")

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Watsonx Orchestrate Chat", layout="centered")
st.title("🤖 Orchestrate Agent Chat")
st.markdown("Interact with your watsonx Orchestrate Agent.")

# --- Helper Functions ---

def call_watsonx_orchestrate(messages):
    """
    Simulates calling the watsonx Orchestrate chat completions endpoint.
    
    NOTE: This is the function you must customize with your specific
    API integration details, including the correct payload and headers.
    """
    if not API_KEY or not ORCHESTRATE_ENDPOINT:
        st.error("API Key or Orchestrate Endpoint not configured. Please set WATSONX_API_KEY and WATSONX_ORCHESTRATE_ENDPOINT environment variables.")
        return "Error: Backend configuration missing."

    # The messages list will be the conversation history from Streamlit session state
    # formatted for the Orchestrate API (often compatible with OpenAI's format).
    
    # Extract the 'content' part of the last user message to use as the query
    # The Orchestrate API often accepts the entire history, but we'll focus on the content
    # for a simple prompt.
    user_query = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else "Hello"

    # Define the payload for the watsonx Orchestrate API call
    # This structure is often used for agents/orchestrators.
    payload = {
        "messages": [
            {"role": "user", "content": user_query}
        ],
        # You may need to add other parameters depending on your agent/model
        "additional_parameters": {},
        "context": {},
        "stream": False # Set to True if you want to implement streaming logic
    }
    
    # Headers for Bearer Token Authentication
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # The timeout prevents the app from hanging indefinitely
        with st.spinner("Waiting for Orchestrate Agent..."):
            response = requests.post(
                ORCHESTRATE_ENDPOINT, 
                headers=headers, 
                json=payload, 
                timeout=30 # 30 second timeout for the response
            )
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

            # Process the response JSON
            response_data = response.json()
            
            # The structure often follows the OpenAI chat format:
            # response_data["choices"][0]["message"]["content"]
            
            # Handle possible empty or unexpected responses
            if 'choices' in response_data and response_data['choices']:
                agent_message = response_data['choices'][0]['message']['content']
                return agent_message
            else:
                return f"Agent returned an empty or unrecognized response: {json.dumps(response_data, indent=2)}"

    except requests.exceptions.RequestException as e:
        return f"An API request error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- Main Application Logic ---

# 1. Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am connected to the watsonx Orchestrate Agent. How can I help you today?"}
    ]

# 2. Display existing messages
for message in st.session_state.messages:
    # Use 'user' for user messages and 'assistant' for the agent's responses
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 3. Handle new user input
if prompt := st.chat_input("Ask your watsonx Orchestrate agent a question..."):
    # Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Prepare the messages list for the API call
    # We pass the entire history for context
    messages_for_api = st.session_state.messages

    # Call the Orchestrate Agent
    assistant_response_content = call_watsonx_orchestrate(messages_for_api)
    
    # Display and save the response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(assistant_response_content)
    
    # Append the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})

# Optional: Configuration sidebar for debugging (useful for local development)
st.sidebar.title("Configuration Status")
if API_KEY:
    st.sidebar.success("API Key is configured.")
else:
    st.sidebar.error("WATSONX_API_KEY missing.")

if ORCHESTRATE_ENDPOINT:
    st.sidebar.success("Orchestrate Endpoint is configured.")
    st.sidebar.info(f"Endpoint: {ORCHESTRATE_ENDPOINT.split('/chat/completions')[0]}")
else:
    st.sidebar.error("WATSONX_ORCHESTRATE_ENDPOINT missing.")