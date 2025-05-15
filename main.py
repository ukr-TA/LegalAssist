from flask import Flask, request, jsonify, render_template
from query import ask_chatbot
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET'])
def chat_bot_page():
    return render_template('chat.html')

@app.route('/chat/query', methods=['POST'])
def chatbot_query():

    user_input = request.json.get("message")
    
    # For now, return a dummy response. Replace this with real logic later.
    response = ask_chatbot(user_input)
    print(response)
    
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=5000)


