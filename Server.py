import socket
import threading

HOST = '127.0.0.1'
PORT= 1234
LISTENER_LIMIT = 5

clients = [] #lists of all connected clients
usernames = [] # lists of the usernames of connected clients
client_rooms = {} # dictionary that tracks which room each client is in


#main function
def main():
    #creating the server socket
     server = socket.socket(socket.AF_INET;socket.SOCK_STREAM)
     
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
        
        
        
if __name__== '__main__':
    main()     
         