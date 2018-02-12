'''
Test handler
'''

class HandlerEcho:
    def __init__(self):
        pass

    def process_message(self, message):
        print "message.type: " + str(message.type)
        print "message.body : " + str(message.body)
        return Response(body=str(message.body),
                status_code=200)
    

