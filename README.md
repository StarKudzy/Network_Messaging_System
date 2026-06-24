## TCP Chat Application

### Description

This project is a simple TCP client-server chat application built with Python. It allows multiple users to connect to one server, send real-time messages, create chat rooms, switch rooms, and invite other users to join rooms. 

### How the System Works

The server starts first and waits for clients to connect. Ech client connects using the same host and port. When a user joins, they enter a username and are placed in the main chat room. The server manages all connected users, chat rooms, messages, and invitations.

### Requirements

- Python3
- Vs Code or any code editor
- Terminal 

### How to Run
- Open the project folder in VS code.
- Open the terminal in VS Code
- Run the server first:
python Server.py
- Open another terminal and run the client:
python Client.py
- Repeat the client commands to connect more users


### Commands
- /rooms - show available rooms
- /users - show users in the current room
- /all users - show all connected users
- /create room_name - create a new room
- /switch room_name - switch to another room
- /invite username room_name - invite a user to a room
- /accept - accept an invitation
- /decline - reject an invitation
- /quit - leave the chat



