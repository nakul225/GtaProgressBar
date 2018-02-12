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
        LOG_HANDLER_URL=""
        TEST_HANDLER_URL=""
        BODY_MEASUREMENTS_HANDLER_URL=""
        READ_HANDLER_URL=""

        handlers = {} # Key: MessageType, Value: Handler
        handlers[MessageType.TEST]=[LOG_HANDLER_URL, TEST_HANDLER_URL]
        handlers[MessageType.WEIGHT]=[LOG_HANDLER_URL, BODY_MEASUREMENTS_HANDLER_URL]
        handlers[MessageType.READ]=[LOG_HANDLER_URL, READ_HANDLER_URL]
        return handlers
    
    def log(self, message):
        '''
        Use this to print to console or log to file.
        '''
        print message

    def register_handler(self, message_type, handler):
        if handler.name in self.handlers[message_type]:
            self.log("handler with name: ",name," already registered for processing message of type: ",message_type,". Not taking any further action"
            return None
        
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
            self.log("No handler registered for message type: ",message.type

