import os
import json
import openai
import streamlit as st
from dotenv import load_dotenv
from swarm import Swarm, Agent
import person_finder
import linkdin_findder
import message_generator
import message_sender

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Swarm client
client = Swarm()

# Define Agents
executive_finder = Agent(
    name="Executive Finder",
    instructions="Find executive names based on company.",
    functions=[person_finder.get_executive_details],
)

linkedin_finder = Agent(
    name="LinkedIn Finder",
    instructions="Find LinkedIn profiles of executives.",
    functions=[linkdin_findder.get_linkedin_profiles],
)

message_sender_agent = Agent(
    name="LinkedIn Messenger",
    instructions="Send a LinkedIn message to a selected profile.",
    functions=[message_sender.send_linkedin_message],
)

# Streamlit UI
st.title("Agent Anderson👾")
user_input = st.text_input("Enter your request (company and message):")

# Initialize session state variables if not present
if "company_name" not in st.session_state:
    st.session_state.company_name = ""
if "user_message" not in st.session_state:
    st.session_state.user_message = ""
if "executives" not in st.session_state:
    st.session_state.executives = {}
if "linkedin_profiles" not in st.session_state:
    st.session_state.linkedin_profiles = []
if "linkedin_message" not in st.session_state:
    st.session_state.linkedin_message = ""

def extract_details_from_input(user_input: str, openai_api_key: str):
    """Extracts company_name and user_message from the user's input using OpenAI."""
    if not openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    client = openai.OpenAI(api_key=openai_api_key)
    
    prompt = f"""
    Extract the following details from the user's input:
    - Company Name
    - Message to send
    
    User Input: "{user_input}"
    
    Provide the result as a valid JSON dictionary with the following keys:
    - company_name
    - user_message
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional input parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    try:
        extracted_data = response.choices[0].message.content.strip()
        return json.loads(extracted_data)
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        return None

if user_input:
    with st.spinner("Extracting details..."):
        parsed_details = extract_details_from_input(user_input, openai.api_key)
    
    if parsed_details:
        st.session_state.company_name, st.session_state.user_message = parsed_details.values()
        st.success(f"**Company:** {st.session_state.company_name}\n**Message:** {st.session_state.user_message}")
    else:
        st.error("Error extracting details. Please try again.")
        st.stop()

    # Find executives
    st.session_state.executives = person_finder.get_executive_details(st.session_state.company_name, "ceo") or {}
    
    if st.session_state.executives:
        exec_options = [f"{title}: {name}" for title, name in st.session_state.executives.items() if name]
        
        if exec_options:
            executive_selection = st.selectbox("Select an executive to message:", exec_options)
            selected_title, selected_executive = executive_selection.split(": ", 1)
            
            with st.spinner(f"Finding LinkedIn profile for {selected_executive}..."):
                response = client.run(
                    agent=linkedin_finder, 
                    messages=[{"role": "user", "content": f"Find LinkedIn profile for {selected_executive} from {st.session_state.company_name}."}]
                )
            
            profiles = [line for line in response.messages[-1]["content"].split("\n") if "linkedin.com" in line]
            
            if profiles:
                st.session_state.linkedin_profiles = profiles
                
                # Display clickable LinkedIn links
                st.markdown("### LinkedIn Profiles:")
                for profile in st.session_state.linkedin_profiles:
                    st.markdown(f"- [LinkedIn Profile]({profile})")
                
                with st.spinner("Generating message..."):
                    st.session_state.linkedin_message = message_generator.generate_linkedin_message(
                        selected_executive, st.session_state.company_name, st.session_state.user_message, openai.api_key
                    )
                
                edited_message = st.text_area("Edit your message:", st.session_state.linkedin_message)
                
                if st.button("Send Message"):
                    with st.spinner("Sending message..."):
                        response = client.run(
                            agent=message_sender_agent, 
                            messages=[{"role": "user", "content": f"Send message '{edited_message}' to {st.session_state.linkedin_profiles[0]}"}]
                        )
                    st.success("✅ Message Sent!")
            else:
                st.error("No LinkedIn profiles found.")
                st.stop()
        else:
            st.warning("No valid executives found. Trying LinkedIn search...")
    else:
        st.warning("No executives found. Trying LinkedIn search...")