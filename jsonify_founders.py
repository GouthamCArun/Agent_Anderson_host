from dotenv import load_dotenv
import openai
import json
import os

load_dotenv()
# Set OpenAI API Key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI client
client = openai

def extract_positions(user_input: str):
    """Extracts the names of positions (e.g., CEO, CTO, etc.) from the input using OpenAI."""
    
    prompt = f"""
    Extract the names of positions or titles (such as CEO, CTO, etc.) mentioned in the following text:
    "{user_input}"

    Provide the result as a valid JSON dictionary with the key "positions" that contains a list of position names.
    """

    # Call OpenAI API for completion using client.chat.completions.create
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

# Example input with positions
# user_input = "The CEO of Zyadha is Anand, the CTO is Jeff, and the COO is Jamal."

# # Extract position names
# positions_data = extract_positions(user_input)

# # Print the extracted details
# if positions_data:
#     print(f"\n✅ Positions: {positions_data['positions']}")
# else:
#     print("❌ Error: Could not extract positions.")
