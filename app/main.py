# Uncomment this to pass the first stage
import socket
import threading
import sys

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")


    IP = "localhost"
    PORT = 4221
    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server((IP,PORT), reuse_port=True)
    # server_socket.accept() # wait for client
    # server_socket.accept()[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")


    while True:
        connection, address = server_socket.accept()
        request = connection.recv(1024)
        request = request.decode()
        print(request)

        request_elems = parse_request(request) #request elements
        target_request = request_elems["request-target"]

        thread = threading.Thread(args=(connection, request_elems), target=handle_client)
        
        # [R] stands for response line
        handle_client(connection, request_elems)
        






def parse_request(request):
    lines = request.split('\r\n')
    method, request_target, protocol = lines[0].split(' ')
    # server_socket, usr_agent, accepted_media = lines[1].split('\r\n')
    # print("PRINTING LINES OF HTTP REQUEST:\n", lines, "\n\n")
    body = lines[-1]

    # print("BODY: ", body, '\n\n')
    header_cnt = 0
    for i in lines:
        if i.find(": ") != -1:
            header_cnt += 1

    request_elems = {
        "protocol": protocol,
        "method": method,
        "request-target": request_target,
        "body": body
        # lines[1].split(": ")[0].lower(): lines[1].split(": ")[1],
        # lines[2].split(": ")[0].lower(): lines[2].split(": ")[1],
        # lines[3].split(": ")[0].lower(): lines[3].split(": ")[1]
    }

    for i in range(header_cnt):
        request_elems.update({lines[i+1].split(": ")[0].lower() : lines[i+1].split(": ")[1]})

    print("[D] REQUEST ELEMS from parse_request():",request_elems)
    # print("[000] lines: ",  lines)
    # print("DICTIONARY: ", request_elems)

    return request_elems

def create_response(protocol, status_code, status_message, content_type, content):  
    if content_type == "":
        response = f"{protocol} {status_code} {status_message}\r\n\r\n"
    else:
        response = f"{protocol} {status_code} {status_message}\r\nContent-Type: {content_type}\r\nContent-Length: {len(content)}\r\n\r\n{content}"

    return response



    # while True:
    #     connection, address = server_socket.accept()
    #     request = connection.recv(1024)
    #     print(requsest.decode())
    #     if request.decode() == "/abcdefg":
    #         connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    #     else:
    #         connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    
def handle_client(connection, request_elems):
    target_request = request_elems["request-target"]
    protocol = request_elems["protocol"]
    response = ''

    status_message = "OK"
    status_code_ok = "200"


    # argv[2] takes the second argument of the command line: ./your_server.sh --directory /tmp/
    # ./your_server.sh is argument N0, so /tmp/ is N2 since indexing starts with 0
    # if there are more than 2 arguments, there is a path in the command line
    FILE_PATH = sys.argv[2] if len(sys.argv) > 2 else "./files/" 



    if target_request == '/':
        print("target_request is / ", target_request)
        response = create_response(protocol, status_code_ok, "OK", "text/plain", '')

    elif target_request.find('echo') != -1:
        echo = request_elems["request-target"][len("/echo/"):]
        # print("[R] echo:", echo)
        response = create_response(protocol, status_code_ok, "OK", "text/plain", echo)

    elif target_request == '/user-agent':
        response = create_response(protocol,"200", "OK", "text/plain", request_elems["user-agent"])
    
    elif target_request[:len("/files/")] == "/files/":
        file_name = target_request[len("/files/"):]  
        print("file request: ", file_name, FILE_PATH)
        if request_elems["method"] == "GET":

            # try block makes that if there is an error it will execyte the except statement 
            try:
                with open(f"{FILE_PATH}/{file_name}", 'r') as file:
                    file_content = file.read()
                    response = create_response(protocol, status_code_ok, status_message, "application/octet-stream", file_content)
            except:
                response = "HTTP/1.1 404 Not Found\r\n\r\n"
        
        elif request_elems["method"] == "POST":
            create_file(f"{FILE_PATH}/{file_name}", request_elems)
            response = create_response(request_elems["protocol"], "201", "Created", "", "")
            
            
    else:
        # print("target request wrong", target_request)
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    connection.sendall(response.encode())
    print("\n response:",response)

    connection.close()


def create_file(FILE_PATH, request_elems):
    new_file = open(FILE_PATH, "w")
    new_file.write(request_elems["body"])
    new_file.close



if __name__ == "__main__":
    main()
