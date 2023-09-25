from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
# Import the necessary libraries and set up OpenAI API key
import nest_asyncio
import openai
from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms import OpenAI
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine
import json
# Initialize Flask app
app = Flask(__name__)
CORS(app)
# Set up OpenAI API key
api_key = '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'
openai.api_key = api_key

# Set up the llama-index components
nest_asyncio.apply()
llm = OpenAI(temperature=0, model="gpt-3.5-turbo", max_tokens=-1)
divya = SimpleDirectoryReader(input_files=["/home/ec2-user/data/divya_interview.pdf"]).load_data()
flince = SimpleDirectoryReader(input_files=["/home/ec2-user/data/flince_interview.pdf"]).load_data()
mm = SimpleDirectoryReader(input_files=["/home/ec2-user/data/MM Interview.pdf"]).load_data()
divya_index = VectorStoreIndex.from_documents(divya)
flince_index = VectorStoreIndex.from_documents(flince)
mm_index = VectorStoreIndex.from_documents(mm)
divya_engine = divya_index.as_query_engine(similarity_top_k=3)
flince_engine = flince_index.as_query_engine(similarity_top_k=3)
mm_engine = mm_index.as_query_engine(similarity_top_k=3)

# Set up query engine tools
query_engine_tools = [
    QueryEngineTool(
        query_engine=divya_engine,
        metadata=ToolMetadata(
            name="divya",
            description="Provides information about clinical trials",
        ),
    ),
    QueryEngineTool(
        query_engine=flince_engine,
        metadata=ToolMetadata(
            name="flince",
            description="Provides information about primary market research and drivers and barriers research study",
        ),
    ),
    QueryEngineTool(
        query_engine=mm_engine,
        metadata=ToolMetadata(
            name="mm",
            description="Provides information about clinical trials",
        ),
    ),
]

s_engine = SubQuestionQueryEngine.from_defaults(query_engine_tools=query_engine_tools)


@app.route("/ask", methods=["GET", 'POST'])
def generate_response():
    if request.method == 'GET':
        return app.send_static_file('index.html')
    elif request.method == 'POST':
        data = request.get_json()
        query = data.get("input", "")

        # Uncomment the below code when using the OpenAI API
        #prompt = f"{custom_text_data}\nUser: {query}\nAssistant:"
        response = s_engine.query(query)
        return jsonify({"response": str(response)})
        #response = json.dumps(str(response))
        #return response
        #return jsonify({"response":response['choices'][0]['text']})
        #return json.dumps(response)
        #return print(str(response))
        #response.json()
        #return jsonify({"response": response['text']})
        #return make_response(jsonify(str(response)), 200)
    #jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)