import socket
import threading

HOST = '127.0.0.1'
PORT= 1234
LISTENER_LIMIT = 5

clients = [] #lists of all connected clients
usernames = [] # lists of the usernames of connected clients
client_rooms = {} # dictionary that tracks which room each client is in

disconnected_users = {} #stores users who are disconnected

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
        client.send(f"Room '{new_room}' does not exist".encode('utf-8'))
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
            
            
#function to remove client when the disconnect
def remove_client(client):
    if client not in clients:
        return
    
    #get info about the user and which room they are in
    index = clients.index(client)
    username = usernames[index]
    current_room = client_rooms[client]

    #save room for reconnection
    disconnected_users[username] = current_room

    #remove client from the room
    if client in rooms[current_room]:
        rooms[current_room].remove.client

    #remove client from tracking lists
    clients.remove(client)
    username.pop(index)

    del client_rooms[client]

    #Notify the room
    broadcast(
        f"{username} is disconnected", None, current_room
    )
    
    #close the socket connection
    client.close()
    print(f"{username} disconnected")



 #creating chat rooms
def create_room(client, room_name):
    if room_name in rooms:
        client.send(f"Room '{room_name}' already exists".encode('utf-8'))
    else:
        rooms[room_name] = []
        client.send(f"Created '{room_name}' room successfully".encode('utf-8'))           
            
            
# Receives the username and places the client into the main chat
#continuosly listens for messages from the connected client
def handle_client(client):
    try:
        username = client.recv(1024).decode('utf-8') # receives the username from the client 
        
        #checks whether the user has disconnected before
        if username in disconnected_users:
            #get the previous room
            room = disconnected_users[username]
            # add to the list of clients
            clients.append(client)
            usernames.append(username)
            #put them in the same room
            client_rooms[client] = room
            rooms[room].append(client)

            del disconnected_users[username] #remove from disconnected users list

            client.send(
                f"Welcome back, you have reconnected to {room}".encode('utf-8')
            )
        else:  #New user
            client.append(client)
            usernames.append(username)

            client_rooms[client] = 'main_chat'
            rooms["main_chat"].append(client)

            client.send(
                "You joined main chat".encode('utf-8')
            )


        clients.append(client)
        usernames.append(username)
        
        client_rooms[client] = 'main_chat'
        rooms['main_chat'].append(client)
        
        print(f"{username} joined main chat")
        client.send("You joined main chat".encode('utf-8'))

        #Sending available rooms to the client
        available_rooms = ", ".join(rooms.keys())
        client.send(
            f"Available rooms: {available_rooms}\n"
            "Use /switch room_name to join a chat room\n"
            "Use /create room_name to create a chat room".encode('utf-8')

        )
       
            
            
        broadcast(f"{username} has joined the chat", client, 'main_chat')
        
       
        
        #keep listening for messages
        while True:
            message = client.recv(1024).decode('utf-8')
            
            if not message: #if message is empty disconnect
                break
            

                #Check if user wants to create a new chat room

            if message.startswith('/create'):
                parts = message.split()

                if len(parts) == 2:
                 room_name = parts[1]
                 create_room(client, room_name)
                else:
                   client.send("ERROR! Usage: /create room_name".encode('utf-8'))

              
               
                
              #switch room
               
            elif message.startswith('/switch'):
                parts = message.split()
            
                if len(parts) == 2:
                    new_room = parts[1]
                    switch_room(client, new_room)
                
                else:
                    client.send("Switch room name".encode('utf-8'))    
            

            else:
                current_room = client_rooms[client]
                broadcast(f"{username} : {message}", client, current_room)
            
                
            
            
            
                
                
                
    except:
        pass
    
    finally:
        remove_client(client)
         






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
        