import requests
from openai import AzureOpenAI

azure_openai_endpoint = "https://tunji-service.openai.azure.com/openai/deployments/tunji-model/chat/completions?api-version=2023-07-01-preview"
azure_openai_api_key = "1c5f09b472cd44cf8d28542f9ae25c03"
azure_openai_api_version = "2023-05-15"

# Function to extract information from a URL using this function
# url = "https://purpleconnect.wemabank.com/support/solutions/articles/67000511710-what-is-alat-"

def extract_information_from_url():
    url = "https://purpleconnect.wemabank.com/support/solutions/articles/67000511710-what-is-alat-"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as err:
        print(f"Error fetching URL : {err}")
        return None

# def url_database(question="What is ALAT"):

#     client = AzureOpenAI(
#     azure_endpoint = azure_openai_endpoint,
#     api_key = azure_openai_api_key,
#     api_version = azure_openai_api_version)

#     url_content = extract_information_from_url()

#     conversation = [
#     {"role":"system", "content":"You are an AI assistant that helps people find information."},
#     {"role":"user", "content":question}]

#     max_url_content_length = 2000
#     truncated_url_content = url_content[:max_url_content_length]

#     if truncated_url_content:
#          conversation.append({"role":"user", "content":f"I found some information from the URL: \n{truncated_url_content}"})
         
         
#     response = client.chat.completions.create(
#          model="tunji-model",
#          messages=conversation)
    
#     return print(response.choices[0].message.content)


# url_database(question="What is ALAT")




















