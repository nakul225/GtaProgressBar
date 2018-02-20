from chalice import Chalice, Response
from enum import Enum
from botocore.vendored import requests

app = Chalice(app_name='alfred_server')
app.debug=True

@app.route('/')
def index():
    return {'status': 'healthy'}

@app.route('/process/message', methods=['POST'])
def process_message():
    alfred = Alfred()
    request_body = app.current_request.json_body
    input_message_type = request_body["type"] #Message has to have a type matching MessageType enum
    handler_urls=alfred.handlers[input_message_type.upper()]
    for handler_url in handler_urls:
        # Process message by each handler
        send_message_to_handler(handler_url, request_body)
    response_body={"body":request_body,"handler_urls":handler_urls}
    return Response(body=response_body)

def send_message_to_handler(handler_url, message):
    response = requests.post(handler_url, message)
    return response

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

class MessageType(Enum):
    WEIGHT = 'weight'
    HEIGHT = 'height'
    MEDITATION = 'meditation'
    NUTRITION = 'nutrition'
    WORKOUT = 'workout'
    READ = 'read'
    WATCH_TV = 'watch tv'
    PRACTICE_MUSIC = 'practice music'
    TODO ='daily todos'
    REMINDER = 'reminder'
    TEST = 'test'

class Alfred:
    '''
    This class forwards message to registered handlers. Each message given to alfred would have a type and handlers for particular type would register themselves with alfred. 
    When processing the message, alfred will call respective handler.
    '''
    def __init__(self):
        self.handlers = self.__get_registered_handlers()

    def __get_registered_handlers(self):
        '''
        Eventually this will be persisted so that we can restart alfred without losing data.
        '''
        LOG_HANDLER_URL="https://ingfvutz8b.execute-api.us-west-2.amazonaws.com/api/process/message"
        BODY_MEASUREMENTS_HANDLER_URL=""
        READ_HANDLER_URL=""
        TASKS_HANDLER_URL="https://4v8uog9pw8.execute-api.us-west-2.amazonaws.com/api/process/message"

        handlers = {} # Key: MessageType, Value: Handler
        handlers[MessageType.TEST.name]=[LOG_HANDLER_URL]
        handlers[MessageType.WEIGHT.name]=[LOG_HANDLER_URL, BODY_MEASUREMENTS_HANDLER_URL]
        handlers[MessageType.READ.name]=[LOG_HANDLER_URL, READ_HANDLER_URL]
        return handlers

    def log(self, message):
        '''
        Use this to print to console or log to file.
        '''
        print message

    def register_handler(self, message_type, handler):
        if handler.name in self.handlers[message_type]:
            self.log("handler with name: ",name," already registered for processing message of type: ",message_type,". Not taking any further action")
            return Nonde
        # Register handler
        # TODO persist handler data
        if message_type in self.handlers.keys():
            # Add to the list of handlers for the message type
            self.handlers[message_type].extend(handler)
        else:
            self.handlers[message_type] = [handler]

    def deregister_handler(self):
        #TODO complete this
        pass

    def process_message(self, message):
        '''
        Call every registered handler to process message
        '''
        if message.type in self.handlers.keys():
            # call handlers
            for handler in self.handlers[message.type]:
                try:
                    handler.process_message(message)
                except:
                    self.log("Exception in processing message with handler: ", handler.name)
        else:
            # No handler registered
            self.log("No handler registered for message type: ",message.type)
