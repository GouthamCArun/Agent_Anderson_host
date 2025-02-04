from swarm import Swarm, Agent
import os
from dotenv import load_dotenv
import person_finder  # Finds executive details
import linkdin_findder  # Finds LinkedIn profile
import openai  # For generating message content
import message_generator  # Generates LinkedIn message
import message_sender  # Sends LinkedIn message
from dotenv import load_dotenv  # Import dotenv to load environment variables


# Load environment variables
load_dotenv()

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Swarm client
client = Swarm()

# Function to extract company and position
def fetch_executive_details(company_name: str, position: str):
    """Calls person_finder to fetch executive details."""
    return person_finder.get_executive_details(company_name, position)

# Function to get LinkedIn profile
def fetch_linkedin_profile(executive_name: str):
    """Calls linkedin_finder to get LinkedIn profile."""
    return linkdin_findder.get_linkedin_profiles(executive_name)

# Define Agent A (Finds executive name)
agent_a = Agent(
    name="Agent A",
    instructions="Find the executive's name based on company and position.",
    functions=[person_finder.get_executive_details],  # Attach function
)

# Define Agent B (Finds LinkedIn profile)
agent_b = Agent(
    name="Agent B",
    instructions="Find the LinkedIn profile of the executive.",
    functions=[linkdin_findder.get_linkedin_profiles],  # Attach function
)

# Define Agent C (Generates LinkedIn message)
agent_c = Agent(
    name="Agent C",
    instructions="Generate a short and friendly LinkedIn message.",
    functions=[message_generator.generate_linkedin_message],  # Attach function
)

# Define Agent D (Sends LinkedIn message)
agent_d = Agent(
    name="Agent D",
    instructions="Send a LinkedIn message to the first profile found.",
    functions=[message_sender.send_linkedin_message],  # Attach function
)

# Example user query
user_input = "Send a message to the CEO of Zyadha saying we at Cognicor really liked your product and would love to collaborate."

# Extract company and message
company_name = user_input.split("CEO of ")[1].split(" saying ")[0].strip()
user_message = user_input.split(" saying ")[1].strip()

# Run Agent A (Find executive name)
response_a = client.run(
    agent=agent_a,
    messages=[{"role": "user", "content": f"Find the CEO of {company_name}."}]
)

# Extract executive's name
executive_name = response_a.messages[-1]["content"]

# Run Agent B (Find LinkedIn profile)
response_b = client.run(
    agent=agent_b,
    messages=[{"role": "user", "content": f"Find the LinkedIn profile of {executive_name}."}]
)

# Extract LinkedIn profile
linkedin_profile = response_b.messages[-1]["content"]

# Run Agent C (Generate LinkedIn message)
linkedin_message = message_generator.generate_linkedin_message(
    executive_name, company_name, user_message, os.getenv("OPENAI_API_KEY")
)

# Run Agent D (Send the LinkedIn message)
response_d = client.run(
    agent=agent_d,
    messages=[{"role": "user", "content": f"Send this message: '{linkedin_message}' to {linkedin_profile}"}]
)

# Display final results for verification
print("\n✅ Found the executive:")
print(f"Name: {executive_name}")
print(f"LinkedIn Profile: {linkedin_profile}")
print("\n✉️ Suggested LinkedIn Message:")
print(linkedin_message)
print("\n📨 Message Sent Status:")
print(response_d.messages[-1]["content"])
print("\n👉 The message has been sent via LinkedIn.")
