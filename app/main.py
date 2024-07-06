# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost",4221), reuse_port=True)
    # server_socket.accept() # wait for client
    # server_socket.accept()[0].sendall(b"HTTP/1.1 200 OK\r\n\r\n")


    while True:
        connection, address = server_socket.accept()
        raw_request = connection.recv(1024)

        request = raw_request.decode()
        print(request)

        request_elems = parse_request(request) #request elements
        target_request = request_elems["request-target"]

        
        # [R] stands for response line
        handle_client(connection, target_request, request_elems)
        






def parse_request(request):
    lines = request.split('\r\n')
    method, request_target, protocol = lines[0].split(' ')
    # server_socket, usr_agent, accepted_media = lines[1].split('\r\n')

    header_cnt = 0
    for i in lines:
        if i.find(": ") != -1:
            header_cnt += 1

    request_elems = {
        "protocol": protocol,
        "method": method,
        "request-target": request_target,
        # lines[1].split(": ")[0].lower(): lines[1].split(": ")[1],
        # lines[2].split(": ")[0].lower(): lines[2].split(": ")[1],
        # lines[3].split(": ")[0].lower(): lines[3].split(": ")[1]
    }

    for i in range(header_cnt):
        request_elems.update({lines[i+1].split(": ")[0].lower() : lines[i+1].split(": ")[1]})

    print(request_elems)
    # print("[000] lines: ",  lines)
    # print("DICTIONARY: ", request_elems)

    return request_elems

def create_response(protocol, status_code, status_message, content_type, content):
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
    
def handle_client(connection, target_request, request_elems):
    response = ''
    if target_request == '/':
        print("target_request is / ", target_request)
        response = create_response("HTTP/1.1", "200", "OK", "text/plain", '')

    elif target_request.find('echo') != -1:
        echo = request_elems["request-target"][len("/echo/"):]
        # print("[R] echo:", echo)
        response = create_response("HTTP/1.1", "200", "OK", "text/plain", echo)

    elif target_request == '/user-agent':
        response = create_response("HTTP/1.1", "200", "OK", "text/plain", request_elems["user-agent"])

    else:
        print("target request wrong", target_request)
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    connection.sendall(response.encode())
    print("\n response:",response)
    connection.close()

if __name__ == "__main__":
    main()
