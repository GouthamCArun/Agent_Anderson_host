import os
import json
import openai
from dotenv import load_dotenv
from swarm import Swarm, Agent
import person_finder
import linkdin_findder
import message_generator
import message_sender
import jsonify_founders

# Load environment variables
load_dotenv()

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Swarm client
client = Swarm()

# Define Agents
executive_finder = Agent(
    name="Executive Finder",
    instructions="Find executives based on company and position.",
    functions=[person_finder.get_executive_details],
)

linkedin_finder = Agent(
    name="LinkedIn Finder",
    instructions="Find LinkedIn profiles of executives.",
    functions=[linkdin_findder.get_linkedin_profiles],
)

message_creator = Agent(
    name="Message Creator",
    instructions="Generate a short LinkedIn message.",
    functions=[message_generator.generate_linkedin_message],
)

message_sender_agent = Agent(
    name="LinkedIn Messenger",
    instructions="Send a LinkedIn message to a selected profile.",
    functions=[message_sender.send_linkedin_message],
)

def chat_input(prompt):
    return input(f"\n{prompt}\n> ")

def extract_details_from_input(user_input: str, openai_api_key: str):
    """Extracts company_name, position, and user_message from the user's input using OpenAI."""
    if not openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    # Set OpenAI API key
    client = openai.OpenAI(api_key=openai_api_key)

    # Define the prompt for GPT
    prompt = f"""
    Extract the following details from the user's input:
    - Company Name
    - Position (e.g., CEO, CTO, etc.)
    - Message to send

    User Input: "{user_input}"

    Provide the result as a valid JSON dictionary with the following keys:
    - company_name
    - position
    - user_message
    """

    # Call OpenAI API for completion
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional input parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Slight variation for natural tone
    )

    try:
        # Extract the content from the API response
        extracted_data = response.choices[0].message.content.strip()
        print(extracted_data)
        # Return the parsed data as a JSON object
        return json.loads(extracted_data)
    
    except Exception as e:
        print(f"❌ Error parsing response: {e}")
        return None

# Start Chatbot
print("\n🤖 Welcome to Agent Anderson! Let's find and connect with executives on LinkedIn.")
user_input = chat_input("Enter your request (company, position, message):")

parsed_details = extract_details_from_input(user_input, openai.api_key)
if not parsed_details:
    print("❌ Error: Could not parse details from input.")
    exit()

company_name, position, user_message = parsed_details.values()
print(f"\n✅ Company: {company_name}\n✅ Position: {position}\n✅ Message: {user_message}")

# Find Executives
print("\n🔍 Searching for executives...")
response = client.run(agent=executive_finder, messages=[{"role": "user", "content": f"Find executives at {company_name} for position {position}."}])
print(response.messages)
last_message = response.messages[-1]["content"] if response.messages else "[]"
executives = jsonify_founders.extract_positions(last_message)

# Check if executives are found and handle the response
if not executives or "positions" not in executives:
    print("❌ No executives found.")
    exit()

# Access the list of positions (could be any position, not just founders)
positions = executives["positions"]

# Handle the list of positions
if len(positions) > 1:
    for i, exec in enumerate(positions, 1):
        print(f"{i}. {exec}")
    choice = int(chat_input("Select an executive by number:")) - 1
    executive_name = positions[choice]
else:
    executive_name = positions[0]

# After the executive is selected
print(f"\n✅ Selected Executive: {executive_name}")

# Trigger LinkedIn Finder to get the profile
print("\n🔍 Searching for LinkedIn profiles...")

response = client.run(agent=linkedin_finder, messages=[{"role": "user", "content": f"Find LinkedIn profiles for {executive_name} from {company_name}."}])

# Handle the LinkedIn profiles
last_message = response.messages[-1]["content"] if response.messages else "LinkedIn profiles not found."
# Print the raw response to debug
print(f"LinkedIn profiles response:\n{last_message}")

# Check if we have LinkedIn URLs in the response text
if "linkedin.com" in last_message.lower():
    # Split the response by newlines or other delimiters and extract the URLs
    profiles = [line for line in last_message.split("\n") if "linkedin.com" in line]
    print("Profiles found:", profiles)
else:
    print("❌ No LinkedIn profiles found.")
    exit()

# If multiple profiles are found, prompt the user to select one
if len(profiles) > 1:
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile}")
    choice = int(chat_input("Select the correct LinkedIn profile:")) - 1
    linkedin_profile = profiles[choice]
else:
    linkedin_profile = profiles[0]

print(f"\n✅ Selected LinkedIn Profile: {linkedin_profile}")

# Generate Message
print("\n💬 Generating LinkedIn message...")
linkedin_message = message_generator.generate_linkedin_message(executive_name, company_name, user_message,openai.api_key)
print(f"\n📜 Suggested Message:\n{linkedin_message}")

if chat_input("Do you want to edit the message? (yes/no)").lower() == "yes":
    linkedin_message = chat_input("Enter your revised message:")

# Send Message
if chat_input("Do you want to send this message? (yes/no)").lower() == "yes":
    response = client.run(agent=message_sender_agent, messages=[{"role": "user", "content": f"Send message '{linkedin_message}' to {linkedin_profile}"}])
    last_message = response.messages[-1]["content"] if response.messages else "Message send status unknown."
    print(f"\n✅ Message Sent Status: {last_message}")
else:
    print("\n🚀 Message not sent. You can copy and send it manually.")

print("\n🎯 Mission Complete! Agent Anderson has finished the task.")
