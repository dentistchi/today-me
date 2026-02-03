import multiprocessing
import uvicorn
import http.server
import socketserver

def run_api_server():
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

def run_frontend_server():
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=run_api_server)
    p2 = multiprocessing.Process(target=run_frontend_server)
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
