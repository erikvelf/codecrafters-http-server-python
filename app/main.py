import socket
import sys
import argparse
import threading

HTTP = "HTTP/1.1"
PATH_SLASH = '/'
STATUS = {
    200: "OK",
    201: "Created",
    404: "Not Found"
}

# def cron_job(time: float, threads):
#     for thread in threads:
#         thread.join()
    
def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    which_os = "linux" # DON NOT FORGET AFTER DEBUG TO SWITCH IT TO NONE
    # check for slash symbol used in path
    while not(which_os == "linux" or which_os == "windows"):
        which_os = input("[0] Enter FULL name of the OS you are using.\nIt is very important for pulling/posting files!\n")
    if which_os.lower() == "windows":
        PATH_SLASH = '\\'
    print(f"\n[0] Using {which_os}.")

    IP = "localhost"
    PORT = 4221
    handled_connections = 0
    server_socket = socket.create_server((IP,PORT), reuse_port=True)

    # server_socket.accept() # wait for client
    print(f"\n[*] Listening on {IP}:{PORT}...\n\n")

 
    # threads = []

    # cron = threading.Thread(args=(1.0, threads), target=cron_job)
    # cron.start()

    while True:
        connection, address = server_socket.accept()
        # print(f"[*] Connection accepted from {address[0]}:{address[1]}")

        # req = Request().parse_from_string(connection.recv(2048).decode())

        # req = Request().parse_from_string(connection.recv(2048).decode())

        # target_request = req.path
        # print(f"[R] [{address[0]}] requested {req.method} {req.path}")
        
        # thread = threading.Thread(args=(req, connection), target=handle_connections)
        # thread.start()
        
        # thread = threading.Thread(target=handle_connections, args=(req, connection))
        thread = threading.Thread(target=handle_connections, args=(connection,))
        thread.start()

        # threads.append(thread)
        
        # thread.join()
        # threading.Thread(args=(req, connection), target=handle_connections).start()

        handled_connections += 1 
        print(f"\n\n[H] Connections handled: {handled_connections}\n\n")



class Request:
    def __init__(self):
        self.protocol = HTTP
        self.method = "GET"
        self.path = None
        self.headers = None
        self.body = ""
  
    def get_header_value(self, header_name: str):
        try:
            return self.headers[header_name]
        except:
            return None
    
    def get_encodings(self) -> list:
        encodings = self.get_header_value("Accept-Encoding")

        if encodings == None:
            return list()
        else:
            return encodings.split(', ')

    def parse_from_string(self, request: str):
        lines = request.split('\r\n') 
        method, path, protocol = lines[0].split(' ')
        body = lines[-1]

        header_cnt = 0
        for i in lines:
            if i.find(": ") != -1:
                header_cnt += 1

        headers = {}
        # the first line is method, path, protocol
        # the last line is body

        # other lines in between first
        for i in range(header_cnt):
            header_name = lines[i+1].split(': ')[0]
            header_value = lines[i+1].split(": ")[1]

            # headers.update({lines[i+1].split(": ")[0] : lines[i+1].split(": ")[1]})
            headers.update({header_name: header_value})


        self.path = path
        self.method = method
        self.headers = headers
        self.body = body

        print(f"FROM PARSE_FROM_STRING lines are: {lines}")


        return self


class Response:
    def __init__(self, supported_encodings = ["gzip"]):
        self.protocol = HTTP
        self.status_code = 200
        self.body = ""
        self.headers = {} # dict
        self.supported_encodings = supported_encodings
        
    
    
    def with_header(self, header_name, header_value):
        self.headers.update({header_name: header_value})
        return self


    def with_protocol(self, protocol):
        self.protocol = protocol
        return self
    
    def with_content_type(self, content_type):
        self.with_header("Content-Type", content_type)
        return self
    
    def with_body(self, body):
        if body == None:
            self.body = ""
        else:
            self.body = body
        return self
    
    def with_encoding(self, list_of_encodings):
        for encoding in list_of_encodings:
            if encoding in self.supported_encodings:
                self.with_header("Content-Encoding", encoding)
                break

        return self
    
    def with_status_code(self, code):
        self.status_code = code
        return self
    
    def build(self):
        self.with_header("Content-Length", len(self.body))

        headers = map(lambda kv: f'{kv[0]}: {kv[1]}\r\n', self.headers.items())
        headers = ''.join(headers)

        response = f"{self.protocol} {self.status_code} {STATUS[self.status_code]}\r\n{headers}\r\n{self.body}"
        return response

def handle_connections(connection: socket):
    # getting the request and reading it
    request = Request().parse_from_string(connection.recv(1024).decode())
    
    target_request = request.path
    response = ''
    protocol = request.protocol

    encodings = request.get_encodings()

    # print(f"Request method is: [{request.method}]")
    STATUS_NOT_FOUND = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    # argv[2] takes the second argument of the command line: ./your_server.sh --directory /tmp/
    # ./your_server.sh is argument N0, so /tmp/ is N2 since indexing starts with 0
    # if there are more than 2 arguments, there is a path in the command line
    FILE_PATH = sys.argv[2] if len(sys.argv) > 2 else f".{PATH_SLASH}files/"

    if request.path == '/':
        response = Response().with_content_type("text/plain").build()

    elif request.path.startswith("/echo/"):
        echo = request.path[len("/echo/"):]
        response = Response().with_content_type("text/plain").with_body(echo).with_status_code(200).with_encoding(encodings).build()

    elif request.path == '/user-agent':
        response = Response().with_content_type("text/plain").with_body(request.headers["User-Agent"]).with_encoding(encodings).build()
    
    elif request.path.startswith("/files/"):
        file_name = target_request[len("/files/"):]
        # if i search for a file in a folder that is in ./files, i might get an error on Windows
        
        if request.method == "GET":
            # print(f"[R] File \"{file_name}\" requested.")
            # try block makes that if there is an error it will execute the except statement 
            try:
                with open(f"{FILE_PATH}{file_name}", 'r') as file:
                    file_content = file.read()
                    # response = create_response(status_code_ok, status_message, "application/octet-stream", file_content)
                    response = Response().with_content_type("application/octet-stream").with_body(file_content).build()
            except:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
        
        elif request.method == "POST":
            print(f"FILE PATH IS: {FILE_PATH}{file_name}")
            create_file(f"{FILE_PATH}{file_name}", request.body)
            response = Response().with_status_code(201).build()
            
            
    else:
        response = Response().with_status_code(404).build()
    
    # print(f"[D] RESPONSE:\r\n{response}")
    connection.sendall(response.encode())
    connection.close()


def create_file(FILE_PATH: str, file_content):
    new_file = open(FILE_PATH, "w")
    new_file.write(file_content)
    new_file.close()
    



if __name__ == "__main__":
    main()
