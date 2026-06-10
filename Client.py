import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

clients = [] # list of all connected clients
usernames = []
client_rooms = {} # dictionary that tracks which roo each client is in 





# broadcast messages to all clients except the sender
def broadcast(message, sender_socket = None, room_name='main_chat'):
    
    if room_name in rooms:
        for client in rooms[room_name]: #loop throgh every client in this room
            if client != sender_socket:
                try:
                    client.send(message.encode('utf-8'))
                    print("message send successfully")
                except:
                    #if sending fails maybe the client is disconnected
                    
                    if client in clients:
                        index = clients.index(client)
                        username = username[index]
                        print(f"client {username} is disconnected")    
            

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


if __name__=='__main__':
    main()
