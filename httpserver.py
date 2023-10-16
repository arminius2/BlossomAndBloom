from http.server import HTTPServer, BaseHTTPRequestHandler
import youtube_stream

# Move the streaming_pid to this module
streaming_pid = None

def toggle_youtube_stream():
    global streaming_pid
    if streaming_pid is None:
        start_youtube_stream()
    else:
        stop_youtube_stream()

def start_youtube_stream():
    global streaming_pid
    if streaming_pid is not None:
        print("Stream already running.")
        return

    # Start youtube_stream.py in a new thread
    stream_thread = threading.Thread(target=youtube_stream.start_stream)
    stream_thread.start()
    streaming_pid = stream_thread.ident

def stop_youtube_stream():
    global streaming_pid
    if streaming_pid is None:
        print("No stream is running.")
        return

    youtube_stream.stop_stream()
    streaming_pid = None

class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Received GET request:" + self.path)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        if streaming_pid is None:
            message = "Start Streaming"
        else:
            message = "Stop Streaming"
        
        self.wfile.write(f"<html><body><a href='/toggle'>{message}</a></body></html>".encode('utf-8'))

    def do_POST(self):
        print("Received POST request:" + self.path)
        self.send_response(200)
        if self.path == "/toggle":
            toggle_youtube_stream()
        self.end_headers()

def run_http_server(PORT):
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    httpd.serve_forever()