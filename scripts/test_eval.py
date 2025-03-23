import json
import requests
import sys

from eval import Evaluator

from tqdm import tqdm

questions = json.load(open("./data/JSON_Questions/WA_pointed.json"))
questions.extend(json.load(open("./data/JSON_Questions/WA_general.json")))

ENDPT = sys.argv[1]

model_responses = []
for question in tqdm(questions):
    try:
        # print(type(question.get("question")), question.get("question"))
        response = requests.post(
            f"http://127.0.0.1:5000/{ENDPT}",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"query": question.get("question")})
        )

        model_answer = response.json()

        model_responses.append(model_answer['response'])
    except Exception as e:
        model_responses.append("No answer")

evaluator = Evaluator(model_responses, questions)
evaluator.evaluate()
evaluator.save_evaluations(f"./evaluation/{ENDPT}_HP1.json")
print(ENDPT, evaluator.average_score())
print('\n'.join(['' for _ in range(15)]))