from flask import Flask, render_template, request, jsonify 
from openai import AzureOpenAI
from Agent import Smart_Agent
from tooling import AVAILABLE_FUNCTIONS, FUNCTIONS_SPEC,  PERSONA


app = Flask(__name__) 
functions = FUNCTIONS_SPEC.copy()
agent = Smart_Agent(persona=PERSONA,functions_list=AVAILABLE_FUNCTIONS, functions_spec=functions)

# OpenAI API Key 
client = AzureOpenAI(
    azure_endpoint = "https://tunji-service.openai.azure.com/openai/deployments/tunji-model/chat/completions?api-version=2023-07-01-preview",
    api_key = "1c5f09b472cd44cf8d28542f9ae25c03",
    api_version = "2023-07-01-preview"
)
Conversation=[{'role':'system','content':PERSONA},]
print(Conversation)

def get_completion(prompt):
	stream_out, query_used, history, agent_response = agent.run(user_input=prompt, conversation=Conversation, stream=False)
	response = agent_response
	Conversation.append({"role":"user", "content":prompt})
	Conversation.append({"role":"assistant", "content":response})
	#print(len(Conversation))
	return response 

@app.route("/", methods=['POST', 'GET']) 
def query_view(): 
	if request.method == 'POST': 
		print('step1') 
		prompt = request.form['prompt'] 
		response = get_completion(prompt) 
		print(response) 

		return jsonify({'response': response}) 
	return render_template('index.html') 



if __name__ == "__main__": 
	app.run(debug=True) 
