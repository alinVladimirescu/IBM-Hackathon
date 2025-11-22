import streamlit as st
import requests
import os
import json
import pandas as pd

API_KEY = os.environ.get("WATSONX_API_KEY", "API_KEY_PLACEHOLDER") 
ORCHESTRATE_ENDPOINT = os.environ.get("WATSONX_ORCHESTRATE_ENDPOINT", "https://api.us-south.orchestrate.watson.cloud.ibm.com/v1/agents/YOUR_AGENT_ID/chat")

st.set_page_config(page_title="Watsonx Orchestrate Chat", layout="centered")
st.title("🤖 Orchestrate Agent + File Upload")

with st.sidebar:
    st.header("Configuration")
    st.info(f"API Key Status: {'✅ Loaded' if API_KEY else '❌ Missing'}")
    
    st.divider()
    
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Attach a file (Text, CSV, JSON)", type=["txt", "csv", "json"])
    
    file_content = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/json":
                data = json.load(uploaded_file)
                file_content = json.dumps(data, indent=2)
                st.success("JSON loaded successfully!")
            elif uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
                file_content = df.to_string()
                st.success("CSV loaded successfully!")
            else:
                stringio = uploaded_file.getvalue().decode("utf-8")
                file_content = stringio
                st.success("Text file loaded successfully!")
            
            with st.expander("Preview File Content"):
                st.code(file_content[:500] + "..." if len(file_content) > 500 else file_content)
                
        except Exception as e:
            st.error(f"Error reading file: {e}")


def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        st.error(f"Authentication Failed: {e}")
        return None

def call_watsonx_orchestrate(messages):
    if not API_KEY or not ORCHESTRATE_ENDPOINT:
        return "Error: Configuration missing. Please check API Key and Endpoint."

    access_token = get_iam_token(API_KEY)
    if not access_token:
        return "Error: Could not generate access token."

    last_user_message = messages[-1]["content"]
    
    payload = {
        "input": {
            "message_type": "text",
            "text": last_user_message
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        with st.spinner("Waiting for Orchestrate Agent..."):
            response = requests.post(
                ORCHESTRATE_ENDPOINT, 
                headers=headers, 
                json=payload, 
                timeout=30
            )
            
            if response.status_code != 200:
                return f"Error {response.status_code}: {response.text}"

            response_data = response.json()
            
            if 'output' in response_data and 'text' in response_data['output']:
                text_response = response_data['output']['text']
                return "\n".join(text_response) if isinstance(text_response, list) else text_response
            elif 'choices' in response_data:
                return response_data['choices'][0]['message']['content']
            else:
                return f"Raw Response: {json.dumps(response_data, indent=2)}"

    except Exception as e:
        return f"Connection Error: {e}"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Upload a file or ask me a question."}
    ]
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
if prompt := st.chat_input("Type your message..."):
    
    final_prompt = prompt
    if file_content:
        final_prompt = f"Context from uploaded file:\n\n{file_content}\n\nUser Question:\n{prompt}"
        st.toast("File content added to message!", icon="📎")

    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    api_messages = st.session_state.messages.copy()
    api_messages[-1]["content"] = final_prompt

    response_text = call_watsonx_orchestrate(api_messages)
    
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})