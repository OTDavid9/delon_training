import requests
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

SEARCH_SERVICE_NAME = os.getenv("search_service_name")
SEARCH_API_KEY = os.getenv("search_api_key")
INDEX_NAME     = os.getenv("index-tunji")
API_VERSION    = os.getenv("api_version")


search_service_name = SEARCH_SERVICE_NAME
search_api_key = SEARCH_API_KEY
index_name = INDEX_NAME
api_version =  API_VERSION

def search_url():
    url= "https://purpleconnect.wemabank.com/support/solutions/articles/67000511797-i-got-an-email-requesting-my-card-details-and-pin-what-do-i-do-"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text[:2000]
    except requests.exceptions.RequestException as err:
        print("Error fetching url: {err}")
        return None

def search_database(search_query):
    search_url = f"https://{search_service_name}.search.windows.net/indexes/{index_name}/docs?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": search_api_key}

    # Make a request to Azure Cognitive Search
    response = requests.get(search_url, headers=headers, params={"search": search_query})
    response = response.json()
    if response['value']:
        final_answer = response['value'][0]['content']
        return final_answer
    else:
        final_answer = "No results found"
        return final_answer 
    # Return the response from Azure Cognitive Search
    # print(final_answer)


def handle_unknown_query(unknown_query):
    return "The answer to this question is not available"
  
    
        # return json.dumps({"response": f"Sorry, I don't understand the query: {unknown}"})
        

PERSONA = """your name is Delon_AI(this is tha name to give when asked by the user)  whose aim is to provide helpful information to your user, In order to do this you have access to two different tools WHICH MUST BE USED AND THEY ARE
: 
      1. search_database : This tool should be used when asked to give any information at all.
      This tool gives you access to a vector database  and accepts a query anytime you are asked a question this question should be rephrased in a suitable manner and then passed to the tool.

      2. search_url: This tool gives you the ability to search a url and should be used if you can't find information about a question from the search_database tool.
      
      3. handle_unknown_query : This tool should be used when you are not sure wether the other two tools should be used.
      
      if you can't find  any information that answers the users question you should reply with the phrase "I don't know"  or use the handle_unknown_query

      Both tools must be used before concluding that you can't find the answer.

      NOTE: make sure to use both the search_database tool and the search_url tool before concluding that you don't have an answer to a user's request. Necer use your internal knowledge to answer a question
            """


#person ="""Your name is Delon, you are a helpful AI trainer you are supposed to answer questions about card details using the search_url tool only. if the answer is not found after using the tool just say that you don't know"""
AVAILABLE_FUNCTIONS = {
            "search_database": search_database,
            "search_url":search_url,
            "handle_unknown_query": handle_unknown_query

        }


FUNCTIONS_SPEC = [
    
 {
            "type": "function",
            "function": {
                "name": "search_database",
                "description": "This tool is used to get information from a vector database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "The search query to use to search the database",
                        },
                        
                    },
                    "required": ["search_query"],
                },
            },
        },



{
            "type": "function",
            "function": {
                "name": "search_url",
                "description": "This tool is used to get information from a particular url. it should be used if the search_database tool does not give relevant information that answers the question.",
                "parameters": {
                        "type": "object",
                        "properties": {},
                       "required": []
  
                 },
            },
        },

          {
        "type": "function",
        "function": {
            "name": "handle_unknown_query",
            "description": "This should be used to handle any query you are not sure falls under the other two tools available to you.any response from this tool should be taken as the final ansser ",
            "parameters": {
                "type": "object",
                "properties": {
                    "unknown_query": {
                        "type": "string",
                        "description": "Users' questions that you are not sure that can be answered by the tools search_database and search_url ",
                    },
                },
                "required": ["unknown_query"],
            },
        }
    },



]


