from http.server import HTTPServer, BaseHTTPRequestHandler
import youtube_stream
import urllib.parse

# Move the streaming_pid to this module
streaming_pid = None
streaming = False

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

    # Wait for 5 seconds
    time.sleep(5)

    # Fetch and print the streaming URL
    youtube = youtube_stream.get_youtube_client()  # Make sure you have this function in youtube_stream.py
    print("Stream URL: " + youtube_stream.get_streaming_url(youtube))


def stop_youtube_stream():
    global streaming_pid
    if streaming_pid is None:
        print("No stream is running.")
        return

    youtube_stream.stop_stream()
    streaming_pid = None

class MyHTTPHandler(BaseHTTPRequestHandler):
     def do_GET(self):
        global streaming  # Declare streaming as global to modify it

        # If the path is '/toggle', toggle the streaming state
        if self.path == '/toggle':
            streaming = not streaming

            print(f"Streaming state toggled: {'ON' if streaming else 'OFF'}")

            # Redirect back to the root path
            self.send_response(303)  # 303 See Other
            self.send_header('Location', '/')
            self.end_headers()
            if streaming:
                start_youtube_stream()
            else:
                stop_youtube_stream()
        
        # Otherwise, just display the state
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            message = f"<html><body>Streaming is {'ON' if streaming else 'OFF'}<br><a href='/toggle'>Toggle Stream</a></body></html>"
            self.wfile.write(message.encode('utf-8'))


def run_http_server(PORT):
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MyHTTPHandler)
    httpd.serve_forever()