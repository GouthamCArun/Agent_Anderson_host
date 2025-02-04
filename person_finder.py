import os
import json
import openai
from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API keys
oai_key = os.getenv("OPENAI_API_KEY")
serper_key = os.getenv("SERPER_API_KEY")

if not oai_key:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")
if not serper_key:
    raise ValueError("SERPER_API_KEY is not set in the .env file.")

# Initialize GoogleSerperAPIWrapper
search = GoogleSerperAPIWrapper()

def extract_cxo_names(company_info: str, roles: list, openai_api_key: str):
    """Extracts CXO-level executive names from company information using OpenAI's API."""

    if not openai_api_key:
        raise ValueError("OpenAI API key is missing.")

    # Set OpenAI API key
    client = openai.OpenAI(api_key=openai_api_key)

    # Convert roles list to a string
    roles_str = ", ".join(roles)

    # Define the prompt for GPT-4
    prompt = f"""
    Extract the names of the following CXO-level executives ({roles_str}) from the following company information:
    {company_info}
    
    Provide the result as a valid JSON dictionary with positions as keys and names as values.
    If a position is not found, set its value to null.
    """

    # Call OpenAI API for completion
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional linkedin message generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Slight variation for natural tone
    )
    print(response)  # Debugging response
    try:
        # Extract the content from the API response
        extracted_data = response.choices[0].message.content.strip()

        # Return the parsed data as a JSON object
        return json.loads(extracted_data)
    
    except Exception as e:
        print("Error parsing response:", e)
        return {}

def get_executive_details(company_name: str, position: str):
    # Include "Co-founder" as an alternative role for "CEO"
    if position.lower() == "ceo":
        query = f"{company_name} CEO OR Co-founder"
    else:
        query = f"{company_name} {position}"
    
    results = search.run(query)
    # print("Search Results:", results)  # Debugging search results
    
    if results:
        return extract_cxo_names(results, [position, "Co-founder"], oai_key)
    else:
        return "No results found for the company."

# Example usage
# company_name = "Zyadha"
# position = "CEO"
# executive_details = get_executive_details(company_name, position)
# print(executive_details)