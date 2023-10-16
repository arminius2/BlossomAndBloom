from http.server import HTTPServer, BaseHTTPRequestHandler
import youtube_stream

class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        from main import streaming_pid
        global streaming_pid  # This should be a shared variable with main.py
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if streaming_pid is None:
            message = "Start Streaming"
        else:
            message = "Stop Streaming"
        
        self.wfile.write(f"<html><body><a href='/toggle'>{message}</a></body></html>".encode('utf-8'))

    def do_POST(self):
        from main import toggle_youtube_stream
        self.send_response(200)
        if self.path == "/toggle":
            toggle_youtube_stream()  # This function should be accessible from here
        self.end_headers()

def run_http_server(PORT):
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    httpd.serve_forever()
