import openai

def generate_linkedin_message(executive_name: str, company_name: str, user_message: str, openai_api_key: str):
    """Uses OpenAI to generate a friendly LinkedIn message."""
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)

    # Define the prompt for GPT-4
    prompt = f"Write a short in 20 words, friendly LinkedIn message to {executive_name}, the CEO of {company_name}, based on this request: '{user_message}'.Remember its not a mail its message dont follow fromat of a mail. Keep it professional but engaging.dont include beest regards and other formalities."

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional linkedin message generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7  # Slight variation for natural tone
    )

    # ✅ Correct way to access the response content
    return response.choices[0].message.content.strip()

# Example usage
# api_key = 'DA2uE9zokOUIsh7CtW7sAq7Dwed7VBiTbJT3BlbkFJAxme7nNpktcm3zYKZAwcLz7xOCwFVMaX26SsOeJ5h4SJsDk-UZaBFhvnykouP6Ihx0BFjQ25MA'
# executive_name = "John Doe"
# company_name = "XYZ Corp"
# user_message = "We at Cognicor really liked your product and would love to collaborate."

# linkedin_message = generate_linkedin_message(executive_name, company_name, user_message, api_key)
# print(linkedin_message)
