import streamlit as st
from openai import OpenAI

# Set up Streamlit app
st.set_page_config(page_title="Chat with OpenAI", page_icon="💬")
st.title("💬 OpenAI Chatbot")

# Get OpenAI API Key
api_key = "key"

# Initialize OpenAI client
client = OpenAI(api_key=api_key) if api_key else None

# Initialize chat history if not already
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Type your message...")

if user_input and client:
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    try:
        # Call OpenAI API using new client format
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{'role': 'system', 'content': 'You are a helpful assistant'},
            {'role': 'user', 'content': user_input}],
        )
        bot_response = response.choices[0].message.content
        
        # Append assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        with st.chat_message("assistant"):
            st.markdown(bot_response)
    except Exception as e:
        st.error(f"Error: {e}")