from openai import AzureOpenAI
import inspect
from tenacity import retry, wait_random_exponential, stop_after_attempt
import os
import json
from dotenv import load_dotenv
load_dotenv()
AZURE_OPENAI_API_KEY = os.getenv("azure_openai_api")



azure_openai_endpoint = "https://tunji-service.openai.azure.com/openai/deployments/tunji-model/chat/completions?api-version=2023-07-01-preview"
azure_openai_api_key = AZURE_OPENAI_API_KEY
azure_openai_api_version ="2023-07-01-preview"
client = AzureOpenAI(
    azure_endpoint = azure_openai_endpoint ,
    api_key = azure_openai_api_key ,
    api_version = azure_openai_api_version
)


def gpt_stream_wrapper(response):
    for chunk in response:
        chunk_msg= chunk['choices'][0]['delta']
        chunk_msg= chunk_msg.get('content',"")
        yield chunk_msg

class Agent(): #Base class for Agent
    def __init__(self, engine,persona, name=None, init_message=None):
        if init_message is not None:
            init_hist =[{"role":"system", "content":persona}, {"role":"assistant", "content":init_message}]
        else:
            init_hist =[{"role":"system", "content":persona}]

        self.init_history =  init_hist
        self.persona = persona
        self.engine = engine
        self.name= name
    def generate_response(self, new_input,history=None, stream = False,request_timeout =20,api_version = "2023-05-15"):
        azure_openai_api_version = "2023-05-15"
        if new_input is None: # return init message 
            return self.init_history[1]["content"]
        messages = self.init_history.copy()
        if history is not None:
            for user_question, bot_response in history:
                messages.append({"role":"user", "content":user_question})
                messages.append({"role":"assistant", "content":bot_response})
        messages.append({"role":"user", "content":new_input})
        response = client.chat.completions.create(
            engine=self.engine,
            messages=messages,
            stream=stream,
            request_timeout =request_timeout
        )
        if not stream:
            return response['choices'][0]['message']['content']
        else:
            return gpt_stream_wrapper(response)
    def run(self, **kwargs):
        return self.generate_response(**kwargs)



def check_args(function, args):
    sig = inspect.signature(function)
    params = sig.parameters

    # Check if there are extra arguments
    for name in args:
        if name not in params:
            return False
    # Check if the required arguments are provided 
    for name, param in params.items():
        if param.default is param.empty and name not in args:
            return False

    return True


class Smart_Agent(Agent):
    """
    Agent that can use other agents and tools to answer questions.

    Args:
        persona (str): The persona of the agent.
        tools (list): A list of {"tool_name":tool} that the agent can use to answer questions. Tool must have a run method that takes a question and returns an answer.
        stop (list): A list of strings that the agent will use to stop the conversation.
        init_message (str): The initial message of the agent. Defaults to None.
        engine (str): The name of the GPT engine to use. Defaults to "gpt-35-turbo".

    Methods:
        llm(new_input, stop, history=None, stream=False): Generates a response to the input using the LLM model.
        _run(new_input, stop, history=None, stream=False): Runs the agent and generates a response to the input.
        run(new_input, history=None, stream=False): Runs the agent and generates a response to the input.

    Attributes:
        persona (str): The persona of the agent.
        tools (list): A list of {"tool_name":tool} that the agent can use to answer questions. Tool must have a run method that takes a question and returns an answer.
        stop (list): A list of strings that the agent will use to stop the conversation.
        init_message (str): The initial message of the agent.
        engine (str): The name of the GPT engine to use.
    """

    def __init__(self, persona,functions_spec, functions_list, name=None, init_message=None, engine = "delonAcademy" ):
        super().__init__(engine=engine,persona=persona, init_message=init_message, name=name)
        self.functions_spec = functions_spec
        self.functions_list= functions_list
        
    
    def run(self, user_input, conversation=None, stream = False, api_version = "2023-07-01-preview"):
        azure_openai_api_version = api_version
        if user_input is None: #if no input return init message
            return self.init_history, self.init_history[1]["content"]
        if conversation is None: #if no history return init message
            conversation = self.init_history.copy()
            print(conversation)
        conversation.append({"role": "user", "content": user_input})
        i=0
        query_used = None

        while True:

            response = client.chat.completions.create(
                model=self.engine, # The deployment name you chose when you deployed the GPT-35-turbo or GPT-4 model.
                messages=conversation,
                tools =  self.functions_spec,
                tool_choice="auto",
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

                # Step 2: check if GPT wanted to call a function
            if  tool_calls:
                print("Recommended Function call:")
                print(response_message.tool_calls)
                print()
                
                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                
                function_name = tool_calls[0].function.name
                
                # verify function exists
                if function_name not in self.functions_list:
                    raise Exception("Function " + function_name + " does not exist")
                   
                function_to_call = self.functions_list[function_name]  
                
                # verify function has correct number of arguments
                function_args = json.loads(tool_calls[0].function.arguments)

                if check_args(function_to_call, function_args) is False:
                    raise Exception("Invalid number of arguments for function: " + function_name)
                #search_query = function_args["search_query"]
                #print("search_query", search_query)

          

                function_response = function_to_call(**function_args)
                print("Output of function call:")
                print(function_response)
                print()

                
                # Step 4: send the info on the function call and function response to GPT
                
                # adding assistant response to messages
                conversation.append(
                    {
                        "tool_calls": tool_calls,
                        "role": "assistant",
                    }

                )

                # adding function response to messages
                conversation.append(
                    {
                        "tool_call_id": tool_calls[0].id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                        
                    }
                )  # extend conversation with function response
                continue
            else:
                break #if no function call break out of loop as this indicates that the agent finished the research and is ready to respond to the user

        if not stream:
            assistant_response = response_message.content
            conversation.append({"role": "assistant", "content": assistant_response})

        else:
            assistant_response = response_message

        return stream,query_used, conversation, assistant_response