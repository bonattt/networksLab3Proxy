
class Request:

    def __init__(self):
        self.headers = {}
        self.version = b'1.1'
        self.method = b'GET'
        self.body = b''
        
    def get_message(self):
        return b''
        
        
    def send_to(self, sock):
        print('TODO send request')
        
        
class Response:
    
    def __init__(self):
        self.headers = {}
        self.version = b'1.1'
        self.method = b'GET'
        self.body = b''
        self.status = 400
        
    
        