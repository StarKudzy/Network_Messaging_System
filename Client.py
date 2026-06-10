import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

clients = [] # list of all connected clients
usernames = []
client_rooms = {} # dictionary that tracks which roo each client is in 



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
