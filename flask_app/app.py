from datetime import datetime, timedelta

from timescale_db_utils import answer_user_question_timescale, answer_user_question_ts_self_query, answer_user_question_sem_chunk_sq, answer_user_question_sem_chunk, check_usefulness

from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

def get_filter_dates(today):
    return [
        today-timedelta(days=1), today-timedelta(days=8), today-timedelta(days=31),
        today-timedelta(days=61), today-timedelta(days=92), today-timedelta(days=182),
        today-timedelta(days=365), today-timedelta(days=365*2), today-timedelta(days=365*5),
        today-timedelta(days=365*7), today-timedelta(days=365*10), datetime(2000, 1, 1)
    ]

def try_date_ranges(query, today, answer_fn):
    end_dt = today
    for start_dt in get_filter_dates(today):
        generated_text, grounded_flag, metadata = answer_fn(query, start_dt, end_dt)
        usefulness_flag = check_usefulness(query, generated_text)
        if usefulness_flag == 'yes':
            return generated_text, grounded_flag, metadata
    return "No messages match your query", "No", []

def get_response(query, answer_fn):
    start_dt = datetime(2000, 1, 1)
    end_dt = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999)

    if query.lower().find('recent') >= 0:
        return try_date_ranges(query, end_dt, answer_fn)
    else:
        return answer_fn(query, start_dt, end_dt)

def get_default_user():
    return {
        'firstName': 'Krishna', 'lastName': 'Saxena', 'phone': '19717270030', 'discordID': 'ksax.', 'whatsAppID': 'Krishna Saxena'
    }

def get_default_friends():
    return [
        {
            '001':{'firstName': 'Kasten', 'lastName': 'Welsh', 'discordID': 'dunsparce0p'}
        },
        {
            '002': {'firstName': 'Richard', 'lastName': 'Tran', 'discordID': 'silverdots'}
        }
    ]

def get_user_friend_aliases(user_info, friend_info):
    user_aliases = {
        f'@{user_info["phone"]}' : f'{user_info["firstName"]} {user_info["lastName"]}',
        user_info["discordID"] : f'{user_info["firstName"]} {user_info["lastName"]}'
    }
    friend_aliases = {}
    for f_id, friend in friend_info.items():
        friend_aliases.update({friend["discordID"] : f'{friend["firstName"]} {friend["lastName"]}'})
    return user_aliases, friend_aliases

@app.route('/generateTimeScale', methods=['POST'])
def generate_text_timescale():
    # Get the input data from the request
    data = request.json
    query = data.get('query', None)
    user_info = data.get('user', get_default_user())
    friend_info = data.get('friends', get_default_friends())
    user_aliases, friend_aliases = get_user_friend_aliases(user_info, friend_info)

    # Generate text using the language model
    generated_text, grounded_flag, metadata = get_response(query, answer_user_question_timescale, user_aliases, friend_aliases)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'grounded': grounded_flag,
            'snippets':metadata
        }
    )

@app.route('/generateTSSelfQuery', methods=['POST'])
def generate_text_timescale_self_query():
    data = request.json
    query = data.get('query', None)
    user_info = data.get('user', get_default_user())
    friend_info = data.get('friends', get_default_friends())
    user_aliases, friend_aliases = get_user_friend_aliases(user_info, friend_info)

    # Generate text using the language model
    generated_text, grounded_flag, metadata = get_response(query, answer_user_question_ts_self_query, user_aliases, friend_aliases)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'grounded': grounded_flag,
            'snippets':metadata
        }
    )

@app.route('/generateTSSemChunk', methods=['POST'])
def generate_text_timescale_sem_chunk():
    data = request.json
    query = data.get('query', None)
    user_info = data.get('user', get_default_user())
    friend_info = data.get('friends', get_default_friends())
    user_aliases, friend_aliases = get_user_friend_aliases(user_info, friend_info)

    generated_text, grounded_flag, metadata = get_response(query, answer_user_question_sem_chunk, user_aliases, friend_aliases)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'grounded': grounded_flag,
            'snippets':metadata
        }
    )

@app.route('/generateTSSemChunkSQ', methods=['POST'])
def generate_text_timescale_sem_chunk_sq():
    data = request.json
    query = data.get('query', None)
    user_info = data.get('user', get_default_user())
    friend_info = data.get('friends', get_default_friends())
    user_aliases, friend_aliases = get_user_friend_aliases(user_info, friend_info)

    generated_text, grounded_flag, metadata = get_response(query, answer_user_question_sem_chunk_sq, user_aliases, friend_aliases)

    # Return the generated text as a JSON response
    return jsonify(
        {
            'response':generated_text,
            'grounded': grounded_flag,
            'snippets':metadata
        }
    )

if __name__ == '__main__':
    app.run(debug=True)