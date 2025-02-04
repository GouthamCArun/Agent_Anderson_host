from langchain_community.utilities import GoogleSerperAPIWrapper
import os

# Set your Serper API key
serper_key = os.getenv("SERPER_API_KEY") # Replace with your actual API key

# Initialize the Serper API
search = GoogleSerperAPIWrapper()

def get_linkedin_profiles(query: str):
    # Perform the search using the query
    query+=" linkedin"
    results = search.results(query)
    
    # Initialize an empty list to store the LinkedIn profile links
    profile_links = []

    # Check if results are available
    if results and 'organic' in results:
        for result in results['organic']:
            # Check if the result contains a LinkedIn link
            if 'link' in result:
                profile_links.append(result['link'])
    
    # Return the list of LinkedIn profile links
    return profile_links

# Test the function with a sample query
# query = "Goutham c arun"
# profiles = get_linkedin_profiles(query)

# # Output the extracted LinkedIn profile links
# print(profiles)
