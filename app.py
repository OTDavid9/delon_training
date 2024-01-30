from flask import Flask, render_template, request
from openai import AzureOpenAI
import json
import requests
from tools import tools_listing
import os
import requests
from openai import AzureOpenAI
from extract import extract_information_from_url
from prompts import system_message
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

AZURE_OPENAI_API_KEY = os.getenv("azure_openai_api_key")
SEARCH_API_KEY = os.getenv("search_api_key")

# Original functions and variables
azure_openai_endpoint = "https://tunji-service.openai.azure.com/openai/deployments/tunji-model/chat/completions?api-version=2023-07-01-preview"
azure_openai_api_key = AZURE_OPENAI_API_KEY
azure_openai_api_version = "2023-05-15"

client = AzureOpenAI(
    azure_endpoint="https://tunji-service.openai.azure.com",
    api_key= AZURE_OPENAI_API_KEY,
    api_version="2023-07-01-preview"
)

def search_cognitive_service(cognitive_query):
    # Azure Cognitive Search configuration
    search_service_name = "tunji-ai-search-3"
    search_api_key = SEARCH_API_KEY
    index_name = "yes"
    api_version = "2023-07-01-preview"

    search_url = f"https://{search_service_name}.search.windows.net/indexes/{index_name}/docs?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": search_api_key}

    # Make a request to Azure Cognitive Search
    response = requests.get(search_url, headers=headers, params={"search": cognitive_query})

    # Return the response from Azure Cognitive Search
    return json.dumps(response.json()['value'][0]['content'])

def url_database(url_query):
    client = AzureOpenAI(
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key,
        api_version=azure_openai_api_version
    )

    url_content = extract_information_from_url()

    conversation = [
        {"role": "system", "content": " Always use the function url_databases to answer user question."},
        {"role": "user", "content": url_query}
    ]

    max_url_content_length = 2000
    truncated_url_content = url_content[:max_url_content_length]

    if truncated_url_content:
        conversation.append({"role": "user", "content": f"I found some information from the URL: \n{truncated_url_content}"})

    response = client.chat.completions.create(
        model="tunji-model",
        messages=conversation
    )

    return json.dumps((response.choices[0].message.content))

def handle_unknown_query(unknown_query):
    """
    This function handles unknown user queries.
    The user's query that is not recognized as coginitive or url"
    """
    
    return json.dumps(f"Sorry, I don't understand the query: {unknown_query}")
    # return json.dumps({str("'I CAN'T ANSWER")})

def run_conversation(user_query):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query}
    ]
    tools = tools_listing
    response = client.chat.completions.create(
        model="tunji-model",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions = {
            "search_cognitive_service": search_cognitive_service,
            "url_database": url_database,
            "handle_unknown_query": handle_unknown_query
        }

        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "search_cognitive_service":
                function_response = function_to_call(
                    cognitive_query=function_args.get("cognitive_query")
                )
            elif function_name == "url_database":
                function_response = function_to_call(
                    url_query=function_args.get("url_query")
                )
            elif function_name == "handle_unknown_query":
                function_response = function_to_call(
                    unknown_query=function_args.get("unknown_query")
                )

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        second_response = client.chat.completions.create(
            model="tunji-model",
            messages=messages,
        )

        return second_response.choices[0].message.content

    return "No tool calls detected."

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_query = request.form.get("user_query")
        response_content = run_conversation(user_query)
        return render_template("index.html", user_query=user_query, response_content=response_content)
    return render_template("index.html", user_query="", response_content="")

if __name__ == "__main__":
    app.run(debug=True)
