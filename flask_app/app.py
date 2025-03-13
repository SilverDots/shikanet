from timescale_db_utils import answer_user_question_timescale, answer_user_question_ts_self_query, answer_user_question_sem_chunk

from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

@app.route('/generateTimeScale', methods=['POST'])
def generate_text_timescale():
    # Get the input data from the request
    data = request.json
    query = data.get('query', None)

    # Generate text using the language model
    generated_text, metadata = answer_user_question_timescale(query)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'snippets':metadata
        }
    )

@app.route('/generateTSSelfQuery', methods=['POST'])
def generate_text_timescale_self_query():
    # Get the input data from the request
    data = request.json
    query = data.get('query', None)

    # Generate text using the language model
    generated_text, metadata = answer_user_question_ts_self_query(query)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'snippets':metadata
        }
    )

@app.route('/generateTSSemChunk', methods=['POST'])
def generate_text_timescale_sem_chunk():
    # Get the input data from the request
    data = request.json
    query = data.get('query', None)

    # Generate text using the language model
    generated_text, metadata = answer_user_question_sem_chunk(query)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'snippets':metadata
        }
    )

if __name__ == '__main__':
    app.run(debug=True)