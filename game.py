from swarm import Swarm, Agent
import os
import json
import openai
from dotenv import load_dotenv
import person_finder  # Finds executive details
import linkdin_findder  # Finds LinkedIn profile
import message_generator  # Generates LinkedIn message
import message_sender  # Sends LinkedIn message

# Load environment variables
load_dotenv()

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Swarm client
client = Swarm()

# ANSI escape codes for colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Define Agents with a Game-like twist
executive_finder = Agent(
    name="Agent Anderson - Executive Finder 🕵️‍♂️",
    instructions="Find the executive's name based on company and position.",
    functions=[person_finder.get_executive_details],  # Attach function
)

linkedin_finder = Agent(
    name="Agent Anderson - LinkedIn Finder 🔍",
    instructions="Find the LinkedIn profile of the executive.",
    functions=[linkdin_findder.get_linkedin_profiles],  # Attach function
)

message_creator = Agent(
    name="Agent Anderson - Message Creator ✨",
    instructions="Generate a short and friendly LinkedIn message.",
    functions=[message_generator.generate_linkedin_message],  # Attach function
)

message_sender_agent = Agent(
    name="Agent Anderson - LinkedIn Messenger 📩",
    instructions="Send a LinkedIn message to the first profile found.",
    functions=[message_sender.send_linkedin_message],  # Attach function
)

input_parser = Agent(
    name="Agent Anderson - Input Parser 🧩",
    instructions="Parse the user's input to extract the company name, position, and message.",
    functions=[],  # No external functions needed
)

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

        # Return the parsed data as a JSON object
        return json.loads(extracted_data)
    
    except Exception as e:
        print(f"{RED}❌ Error parsing response: {e}{RESET}")
        return None

# Dynamic user input
print(f"{CYAN}⚡ Agent Anderson! Reporting ⚡{RESET}")
print(f"{CYAN}🎮 I send LinkedIn messages to anyone, anywhere, anytime! 🎮{RESET}")

user_input = input(f"{CYAN}🔍 Please enter your request:\n{RESET}")

# Extract details using the new agent
print(f"{BLUE}🧩 Agent Anderson - Input Parser started...{RESET}")
parsed_details = extract_details_from_input(user_input, os.getenv("OPENAI_API_KEY"))

if not parsed_details:
    print(f"{RED}❌ Failed to parse user input. Please try again.{RESET}")
    exit()

# Extract parsed details
company_name = parsed_details.get("company_name")
position = parsed_details.get("position")
user_message = parsed_details.get("user_message")

# Validate extracted details
if not company_name or not position or not user_message:
    print(f"{RED}❌ Missing details in parsed input. Please try again.{RESET}")
    exit()

print(f"{GREEN}✅ Agent Anderson - Input Parser completed!{RESET}")
print(f"{GREEN}✅ Parsed Details:{RESET}")
print(f"Company: {company_name}")
print(f"Position: {position}")
print(f"Message: {user_message}")

# Start the operation
print(f"{CYAN}🚀 Operation Commenced...{RESET}")
print(f"{GREEN}💬 Agent Anderson here, I’m on the case. First, I’ll find the executive’s details for position {position}...{RESET}")

# Run Agent Anderson - Executive Finder 🕵️‍♂️ (Find executive name)
print(f"{BLUE}🕵️‍♂️ Agent Anderson - Executive Finder started...{RESET}")
response_a = client.run(
    agent=executive_finder,
    messages=[{"role": "user", "content": f"Find the {position} of {company_name}."}]
)
executive_name = response_a.messages[-1]["content"]
print(f"{GREEN}✅ Agent Anderson - Executive Finder completed: Found the {position}: {executive_name}!{RESET}")

# Run Agent Anderson - LinkedIn Finder 🔍 (Find LinkedIn profile)
print(f"{BLUE}🔍 Agent Anderson - LinkedIn Finder started...{RESET}")
response_b = client.run(
    agent=linkedin_finder,
    messages=[{"role": "user", "content": f"Find the LinkedIn profile of {executive_name}."}]
)
linkedin_profile = response_b.messages[-1]["content"]
print(f"{GREEN}✅ Agent Anderson - LinkedIn Finder completed: LinkedIn Profile found: {linkedin_profile}{RESET}")

# Run Agent Anderson - Message Creator ✨ (Generate LinkedIn message)
print(f"{BLUE}✨ Agent Anderson - Message Creator started...{RESET}")
linkedin_message = message_generator.generate_linkedin_message(
    executive_name, company_name, user_message, os.getenv("OPENAI_API_KEY")
)
print(f"{YELLOW}📜 Message Created by Agent Anderson:\n{linkedin_message}{RESET}")
print(f"{GREEN}✅ Agent Anderson - Message Creator completed!{RESET}")

# Run Agent Anderson - LinkedIn Messenger 📩 (Send the LinkedIn message)
print(f"{BLUE}📩 Agent Anderson - LinkedIn Messenger started...{RESET}")
response_d = client.run(
    agent=message_sender_agent,
    messages=[{"role": "user", "content": f"Send this message: '{linkedin_message}' to {linkedin_profile}"}]
)
print(f"{GREEN}✅ Agent Anderson - LinkedIn Messenger completed: Message Sent Status: {response_d.messages[-1]['content']}{RESET}")

# Final Summary
print(f"\n{CYAN}🚀 Mission Complete! Agent Anderson has successfully completed the task!{RESET}")
print(f"{GREEN}✅ {position} Name: {executive_name}{RESET}")
print(f"{GREEN}✅ LinkedIn Profile: {linkedin_profile}{RESET}")
print(f"{YELLOW}✉️ Suggested Message:\n{linkedin_message}{RESET}")
print(f"{GREEN}📨 The message has been successfully sent via LinkedIn! Mission Complete!{RESET}")