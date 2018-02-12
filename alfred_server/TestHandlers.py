import unittest
from Message import Message
from Message import MessageType
from HandlerEcho import HandlerEcho

class TestHandlers(unittest.TestCase):
    def test_echo_handler_processes_message(self):
        message = Message("name", MessageType.TEST, '{"testing":"maps"}')
        handler = HandlerEcho()
        handler.process_message(message)


if __name__ == '__main__':
        unittest.main()
