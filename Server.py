import socket
import threading

HOST = '127.0.0.1'
PORT= 1234
LISTENER_LIMIT = 5

clients = [] #lists of all connected clients
usernames = [] # lists of the usernames of connected clients
client_rooms = {} # dictionary that tracks which room each client is in

rooms = {
    'main_chat': [],
    'dresses': [],
    'shoes': [],
    'orders': [],
    'shipping': []
}
#function to switch room between clients
def switch_room(client, new_room):
    username = get_username(client)
    
    if new_room not in rooms:
        client.send(f"Room '{new_room}' does not exixt". encode())
        return
    
    old_room = client_rooms[client]
    
    rooms[old_room].remove(client)
    rooms[new_room].append(client)
    client_rooms[client] = new_room
    
    client.send(f"You switched to {new_room}".encode('utf-8'))
    broadcast(f"{username} left the room, client, old room")
    broadcast(f"{username} joined the room", client, new_room)
    
        

#function to define username
def get_username(client):
    if client in clients:
        index = clients.index(client)
        return usernames[index]
    
    return "unknown"



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
                        
                        username = get_username(client)
                        print(f"client {username} is disconnected")    
            
            
            
            
            
# Receives the username and places the client into the main chat
#continuosly listens for messages from the connected client
def handle_client(client):
    try:
        username = client.recv(1024).decode('utf-8') # receives the username from the client 
        
        clients.append(client)
        usernames.append(username)
        
        client_rooms[client] = 'main_chat'
        rooms['main_chat'].append(client)
        
        print(f"{username} joined main chat")
        client.send("You joined main chat".encode('utf-8'))
       
            
            
        broadcast(f"{username} has joined the chat", client, 'main_chat')
        
        
        #keep listening for messages
        while True:
            message = client.recv(1024).decode('utf-8')
            
            if message:
                
              #switch room
               
                 if message.startswitch('/switch'):
                    parts = message.split()
            
                    if len(parts) == 2:
                        new_room = parts[1]
                        switch_room(client, new_room)
                
                    else:
                        client.send("Switch room name".encode('utf-8'))    
            
                 else:
                     current_room = client_rooms[client]
                     broadcast(f"{username} : {message}", client, current_room)
            
                
            
            
            else:
                current_room = client_rooms[client]
                broadcast(f"{username}: {message}", client, current_room)
                
                
                
    except:
        print("client disconnected")    




#main function
def main():
    #creating the server socket
     server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
     
#try and catch  block

     try:
    # provide server with an address in the form of HOST and PORT
    
         server.bind((HOST,PORT))
    
     except:
         print(f"Unable to bind host {HOST} and port {PORT}")    
         
         
    # set server limit
     server.listen(LISTENER_LIMIT)     
    
    #server to keep listening to new client connections
     while 1:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")
        
        threading.Thread(target=handle_client, args=(client,)).start
        
        
        
if __name__== '__main__':
    main()     
        