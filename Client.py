import socket
import threading

HOST = '127.0.0.1'
PORT = 1234




#fn to continuosly receive messages from the server
def receive_messages(client):
    while True:
        
        try:
            message = client.recv(1024).decode('utf-8')
            
            if message:
                print(message)
                
            else:
                print("Disconnected from server")    
                break 
            
        except:
            print("connection is closed")
            break







def main():
    #creating a socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #connect to server
    #use try and except block to detect if the server is down and unableto connect
    try:
        client.connect((HOST,PORT))
        print(f"Connected to server")
    except:
        print(f"Unable to connect to server{HOST} {PORT}")
        return
    
    
    #ask for username and send it to server
    while True:
        username = input("Enter your username:  ")
        client.send(username.encode('utf-8'))

        response = client.recv(1024).decode('utf-8')
        print(response)

        if "Username accepted" in response:
            break

    
    
    
    threading.Thread(target=receive_messages, args=(client,)).start()
    
    #sending messages loop
    while True:
        message = input("")
        
        if message:
            client.send(message.encode('utf-8'))

if __name__=='__main__':
    main()
