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
        request = connection.recv(1024)
        print(request.decode())
        url = request.decode().split(' ') 

        target_request = url[1]



        
        

        if target_request == '/':
            print("target_request is / ", target_request)
            connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        elif target_request.find('echo') != -1:
            echo = url[1].split("/")[-1]
            print("echo:", echo)

            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(echo)}\r\n\r\n{echo}"
            connection.sendall((response.encode()))
        else:
            print("target request wrong", target_request)
            connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


    # while True:
    #     connection, address = server_socket.accept()
    #     request = connection.recv(1024)
    #     print(requsest.decode())
    #     if request.decode() == "/abcdefg":
    #         connection.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    #     else:
    #         connection.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    
    

if __name__ == "__main__":
    main()
