from chalice import Chalice
import boto3

app = Chalice(app_name='log-handler')

@app.route('/')
def index():
    return {'hello': 'world'}

@app.route('/process/message', methods=['POST'])
def process_message():
    client = boto3.client('s3')
    message = app.current_request.json_body
    message = client.list_buckets()
    return "Logging event with body: " + str(message)

# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
