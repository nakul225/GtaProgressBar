from enum import Enum

class Message:
    def __init__(self, message_name, message_type, message_body):
        self.name = message_name
        self.type = message_type # Has to be one of the MessageType enums
        self.body = message_body
        #TODO Add validation on MessageType value

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
