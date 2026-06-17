import socket
import threading

HOST = '127.0.0.1'
PORT= 1234
LISTENER_LIMIT = 5

clients = [] #lists of all connected clients
usernames = [] # lists of the usernames of connected clients
client_rooms = {} # dictionary that tracks which room each client is in
pending_invites={} #dictionary to store all pending invites to chat rooms

disconnected_users = {} #stores users who are disconnected

rooms = {
    'main_chat': [],
    'dresses': [],
    'shoes': [],
    'pants': [],
    'shirts': []
}
     



#function to define username
def get_username(client):
    if client in clients:
        index = clients.index(client)
        return usernames[index]
    
    return "unknown"


#shows clients connected in the current room
def show_users(client):
    current_room = client_rooms[client] #get the room the client is currently in
    room_users = [] #stores the list of clients connected in the current room
   #loop through all clients in the room
    for room_client in rooms[current_room]:
        username = get_username(room_client)
        room_users.append(username)

    users_list = ", ".join(room_users)
    
    #sends list back to the person who requested the list
    client.send(
        f"Users in {current_room}: {users_list}".encode('utf-8')
    )

#function to show all connected clients
def show_all_users(client):
    #check if there are any connected clients
    if len(usernames) == 0:
        client.send("No clients connected".encode('utf-8'))

    users_list = ", ".join(usernames)

    #send list back to client
    client.send(
        f"Connected clients: {users_list}".encode('utf-8')
    )


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
                        remove_client(client)
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
        rooms[current_room].remove(client)

    #remove client from tracking lists
    clients.remove(client)
    usernames.pop(index)

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
        
        
        
        
        
        
        
#function to switch chat rooms
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
    broadcast(f"{username} left the room ", client, old_room)
    broadcast(f"{username} joined the room", client, new_room)          
    
    
    
    
    
    
#function to invite clients to a chat room
def invite_user(client, invited_username,room_name):
    
    #check if the room exists in rooms list
    if room_name not in rooms:
        client.send("Room not found".encode('utf-8'))
        return
    
    #check if the username  exists in the users list
    if invited_username not in usernames:
        client.send("User not found".encode('utf-8'))
        return
    
   
    
     
    #find the position of the invited user in the users list,get user socket
    index= usernames.index(invited_username)
    invited_client= clients[index]
    
    #check if invited user is already in the room:
    if invited_client  in rooms[room_name]:
      client.send("User already in the room".encode('utf-8'))
      return
    
    #which room and who sent the invitation
    pending_invites[invited_client] = {
        'room': room_name,
        'inviter': client 
    }
  
    inviter_username = get_username(client)
    invited_client.send(f"{inviter_username} is inviting you to join {room_name}.Type /accept to join or /decline to reject.".encode('utf-8'))         
    client.send(f"invitation sent to {invited_username}".encode('utf-8'))        
            
            
            
            
 #allows users to accept invites           
def accept_invite(client):
    #check if the client has any pending inivites
    if client not in pending_invites:
        client.send("You have no pending invitations".encode('utf-8'))
        return
    
    invite_info = pending_invites[client] #get room name
    room_name = invite_info['room']
    inviter = invite_info['inviter']
    
    del pending_invites[client]# remove invite when client accepts
    switch_room(client, room_name)
    
   

#allow users to decline invite offers
def decline_invite(client):
    #check if client has any pending invitations
    if client not in pending_invites:
        client.send("You have no pending inivitations.".encode('utf-8'))
        return
    
    invite_info = pending_invites[client]

    room_name = invite_info['room']
    inviter = invite_info['inviter']

    declined_user = get_username(client)
    try:
        inviter.send(
            f"{declined_user} has declined your invitation to join {room_name}\n".encode('utf-8')
        )
    except:
        pass
    
    del pending_invites[client]
    client.send(f"You declined the invitation to join {room_name}\n".encode('utf-8'))
    
    
                
            
            
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
                f"Welcome back, you have reconnected to {room}\n".encode('utf-8')
            )
        else:  #New user
            clients.append(client)
            usernames.append(username)

            client_rooms[client] = 'main_chat'
            rooms["main_chat"].append(client)

            client.send(
                "You joined main chat\n".encode('utf-8')
            )
            print(f"{username} joined main chat\n")        

        #Sending available rooms to the client
        available_rooms = ", ".join(rooms.keys())
        client.send((
           f"Available rooms: {available_rooms}\n"
           "Commands to use :\n"
           "/switch room_name  - join a chat room\n"
           "/create room_name  - create a new chat room\n"
           "/invite username room_name  - invite a user to a room\n"
           "/accept  - accept a room invitation\n"
           "/decline  - decline a room invitation\n"
           "/who - show users in current room\n"
           "/who all - show all connected users\n"
           "/quit  - exit the chat"
           ).encode('utf-8'))
        broadcast(f"{username} has joined the chat\n", client, 'main_chat')
        
        #keep listening for messages
        while True:
            message = client.recv(1024).decode('utf-8')
            
            if not message: #if message is empty disconnect
                break
            

                #Check if user wants to create a new chat room

         #Check if user wants to create a new chat room
            if message.startswith('/create'):
                parts = message.split()

                if len(parts) == 2:
                 room_name = parts[1]
                 create_room(client, room_name)
                else:
                   client.send("ERROR! Usage: /create room_name\n".encode('utf-8'))

             
         #check if user wants to switch rooms      
            elif message.startswith('/switch'):
                parts = message.split()
            
                if len(parts) == 2:
                    new_room = parts[1]
                    switch_room(client, new_room)
                
                else:
                    client.send("Switch room name\n".encode('utf-8'))    
          
         
         #check if user wants to invite another user to a room
            elif message.startswith('/invite'):
                parts = message.split()
                 
                 
                if len(parts) == 3:
                    invite_username = parts[1]    
                    room_name = parts[2]   
                    invite_user(client, invite_username, room_name)    
                else:
                    client.send("ERROR! Usage: /invite username room_name\n".encode('utf-8'))
                    

        #check if user wants to exit the chat
            elif message.startswith('/quit'):
                client.send("Goodbye! You are disconnected.\n".encode('utf-8'))
                break

        #check if user accepts a room invitation      
            elif message == '/accept':
                accept_invite(client)
                
             #check if user declined the invitation   
            elif message == '/decline':
                decline_invite(client) 
        
        #show users in current room
            elif message == '/who':
                show_users(client)  

        #show all connected users
            elif message == '/who all':
                show_all_users(client)
                  
                         
            

            else:
                current_room = client_rooms[client]
                broadcast(f"{username} : {message}", client, current_room)
                      
    except Exception as e:
       
     print(f"Client disconnected because of error: {e}\n") 

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
         print(f"Unable to bind host {HOST} and port {PORT}\n")    
         
         
    # set server limit
     server.listen(LISTENER_LIMIT)    
     print(f"Server is listening on {HOST}:{PORT}")
     print("Waiting for clients to connect...")
    
    #server to keep listening to new client connections
     while 1:
        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")
        
        threading.Thread(target=handle_client, args=(client,)).start()
        
        
        
if __name__== '__main__':
    main()     
        