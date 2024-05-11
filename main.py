import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def _reset_users_list(self):
            USERS_LIST.clear()
            USERS_LIST.append({
                "id": 1,
                "username": "theUser",
                "firstName": "John",
                "lastName": "James",
                "email": "john@email.com",
                "password": "12345",
            })
    
    def do_GET(self):
        if self.path == '/reset':
            self._reset_users_list()
            self._set_response(200, USERS_LIST)
        elif self.path == '/users':
            self._set_response(200, USERS_LIST)
        elif self.path.startswith('/user/'):
            username = self.path.split('/')[-1]
            for user in USERS_LIST:
                if user['username'] == username:
                    self._set_response(200, user)
                    return
            self._set_response(400, {"error": "User not found"})

    def do_POST(self):
        if self.path == '/user':
            try:
                request_data = self._pars_body()
                if isinstance(request_data, dict):
                    if all(key in request_data for key in ["id", "username", "firstName", "lastName", "email", "password"]):
                        if any(request_data["id"] == user["id"] for user in USERS_LIST):
                            self._set_response(400, {})
                        else:
                            USERS_LIST.append(request_data)
                            self._set_response(201, request_data)
                    else:
                        self._set_response(400, {})
                elif isinstance(request_data, list):
                    if all(isinstance(item, dict) and all(key in item for key in ["id", "username", "firstName", "lastName", "email", "password"]) for item in request_data):
                        if any(item["id"] == user["id"] for user in USERS_LIST for item in request_data):
                            self._set_response(400, {})
                        else:
                            USERS_LIST.extend(request_data)
                            self._set_response(201, request_data)
                    else:
                        self._set_response(400, {})
                else:
                    self._set_response(400, {})
            except json.JSONDecodeError:
                self._set_response(400, {})

    def do_PUT(self):
        if self.path.startswith('/user/'):
            user_id = int(self.path.split('/')[-1])
            try:
                request_data = self._pars_body()
                if all(key in request_data for key in ["username", "firstName", "lastName", "email", "password"]):
                    for user in USERS_LIST:
                        if user["id"] == user_id:
                            user.update(request_data)
                            self._set_response(200, user)
                            return
                    self._set_response(404, {"error": "User not found"})
                else:
                    self._set_response(400, {"error": "not valid request data"})
            except json.JSONDecodeError:
                self._set_response(400, {})

    def do_DELETE(self):
        if self.path.startswith('/user/'):
            user_id = int(self.path.split('/')[-1])
            for i, user in enumerate(USERS_LIST):
                if user["id"] == user_id:
                    del USERS_LIST[i]
                    self._set_response(200, {})
                    return
            self._set_response(404, {"error": "User not found"})

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
