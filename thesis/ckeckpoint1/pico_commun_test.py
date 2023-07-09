from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        message = self.path[1:]
        print('message recieved:',message)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        
        
server = HTTPServer(('0.0.0.0', 8080), RequestHandler)
print('server running on port 8080...')
server.serve_forever()
