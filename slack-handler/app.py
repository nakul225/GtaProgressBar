from chalice import Chalice, Response
import boto3
import pickle
from urlparse import urlparse, parse_qs
from botocore.vendored import requests
import json

app = Chalice(app_name='slack-handler')
app.debug=True

def __get_alfred_url():
    return "https://4v8uog9pw8.execute-api.us-west-2.amazonaws.com/api/process/message"

@app.route('/', methods=['POST','GET'], content_types=['application/x-www-form-urlencoded'])
def index():
    parsed = parse_qs(app.current_request.raw_body.decode())
    print "parsed:" + str(parsed)
    # str(parsed)
    return {'hello': 'world'}

'''
This handler merely takes in input from slack and forwards it to alfred
That way, we can have very small commands on slack that transalte to 
specific commands on alfred.
'''
@app.route('/process/message/{username}', methods=['POST'], content_types=['application/x-www-form-urlencoded'])
def process_message(username):
    # Extract command from body and just pass it to alfred
    parsed_input = parse_qs(app.current_request.raw_body.decode())
    input_text = parsed_input['text'][0]
    print "Making query to alfred using command: " + str(input_text)
    # Make http call to alfred
    headers = {'Content-type': 'application/json'}
    json_request_body = json.dumps(get_json_data_for(username,input_text))
    print "Making query with json body:", json_request_body
    response = requests.post(__get_alfred_url(), headers=headers, data=json_request_body )
    formatted_output = format_output(response.json())
    slack_response = {"text":"hello", "attachments":[{"title":"Goals","pretext":"Here are your goals and progress status:","fields":formatted_output,"color": "#3AA3E3"}]}
    return slack_response

def format_output(response):
    goals = response["result"]["response_message"]["goals"]
    goal_names = goals.keys()
    result = [] # list of dictionary per goal
    for goal in goal_names:
        goal_dict = {}
        goal_dict["title"]=goals[goal]["name"]
        goal_dict["value"]=goals[goal]["progress"] + " " + goals[goal]["progress_bar"]
        result.append(goal_dict)
    return result

class GoalOutput(object):
    def __init__(self, name, progress_percentage):
        self.name = name
        self.progress = progress_percentage


def get_json_data_for(username,input_text):
    data = {}
    data["username"]=username
    data["command"]=input_text
    return data
