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
        content_length = int(self.headers['Content-Length'])
        return json.loads(self.rfile.read(content_length).decode('utf-8'))

    def do_GET(self):
        if self.path == '/reset':
            global USERS_LIST
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
            self._set_response(200, USERS_LIST)
        elif self.path == '/users':
            self._set_response(200, USERS_LIST)
        elif self.path.startswith('/user/'):
            username = self.path.split('/')[-1]
            user_data = next((user for user in USERS_LIST if user["username"] == username), None)
            if user_data:
                self._set_response(200, user_data)
            else:
                self._set_response(400, {"error": "User not found"})
        else:
            self._set_response(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == '/user':
            try:
                req_body = self._pars_body()
                if isinstance(req_body, dict):
                    USERS_LIST.append(req_body)
                    self._set_response(201, req_body)
                elif isinstance(req_body, list):
                    USERS_LIST.extend(req_body)
                    self._set_response(201, req_body)
                else:
                    self._set_response(400, {})
            except Exception as e:
                self._set_response(400, {})
        elif self.path == '/user/createWithList':
            try:
                req_body = self._pars_body()
                if isinstance(req_body, list):
                    ids = [user["id"] for user in USERS_LIST]
                    if any(user["id"] in ids for user in req_body):
                        self._set_response(400, {})
                    else:
                        USERS_LIST.extend(req_body)
                        self._set_response(201, req_body)
                else:
                    self._set_response(400, {})
            except Exception as e:
                self._set_response(400, {})
        else:
            self._set_response(404, {"error": "Not Found"})

    def do_PUT(self):
        if self.path.startswith('/user/'):
            user_id = int(self.path.split('/')[-1])
            try:
                req_body = self._pars_body()
                if all(key in req_body for key in ("username", "firstName", "lastName", "email", "password")):
                    index = next((i for i, user in enumerate(USERS_LIST) if user["id"] == user_id), None)
                    if index is not None:
                        USERS_LIST[index].update(req_body)
                        self._set_response(200, USERS_LIST[index])
                    else:
                        self._set_response(404, {"error": "User not found"})
                else:
                    self._set_response(400, {"error": "not valid request data"})
            except Exception as e:
                self._set_response(400, {})
        else:
            self._set_response(404, {"error": "Not Found"})

    def do_DELETE(self):
        if self.path.startswith('/user/'):
            user_id = int(self.path.split('/')[-1])
            index = next((i for i, user in enumerate(USERS_LIST) if user["id"] == user_id), None)
            if index is not None:
                del USERS_LIST[index]
                self._set_response(200, {})
            else:
                self._set_response(404, {"error": "User not found"})
        else:
            self._set_response(404, {"error": "Not Found"})

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
