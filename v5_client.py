#VERSION_5 COMBINED CODE JADEN AND CONNOR - CLIENT PROGRAM
import socket
import threading
import sys
import pymongo
import json
from v5_funcs import *
username = ""

dbconnection = pymongo.MongoClient("mongodb+srv://connorjones165:G2UrB1t990Bcyy06@cluster0.xqbxg1f.mongodb.net/?retryWrites=true&w=majority")
db = dbconnection["ShoeFlu"]
collection_logins = db["Logins"]
collection_inventory = db["Inventory"]



def send(client_socket):

    global username
    while True:

        print("\nMenu")
        print("1) Log In")
        print("2) Check Inventory")
        print("3) Exit")
        select = input("Enter Selection: ")
        if select == "1":
            client_socket.send(select.encode('utf-8'))
            username = input("USERNAME: ")
            try:
                client_socket.send(username.encode('utf-8'))
            except BrokenPipeError:
                print("Cannot send message. Server might be down.")
                break
            password = input("Password: ")
            try:
                client_socket.send(password.encode('utf-8'))
            except BrokenPipeError:
                print("Cannot send message. Server might be down.")
                break
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                if message == "Server is shutting down.":
                    print(message)
                    break
                if message == "0":
                    print("\nInvalid Credentials...")
                    print("\nPlease try again:")
                if message == "1":
                    print("\nYou are successfully logged in", username, "!")
                    manager(client_socket)
                if message == "2":
                    employee(client_socket, username)
            except ConnectionResetError:
                print("The connection was lost.")
            except Exception as e:
                print(f"An error occurred: {e}")

                
        elif select == "2":
            printInventory(client_socket)
        elif select == "3":
            print("GoodBye!")
            try:
                client_socket.send(f"exit".encode('utf-8'))
            except BrokenPipeError:
                pass  # If the server is down, we can't send the message
            client_socket.close()
            sys.exit()
        else:
            print("\nWrong input!")



def main():
    print("Welcome to The Shoe Flu Employee Database")
    server_address = ('127.0.0.1', 12345)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #ignore error
    #try connecting, throw error if server isnt up
    try:
        client_socket.connect(server_address)
    except ConnectionRefusedError:
        sys.exit("Server is not running.")
        

    send(client_socket)
    
    
    
main()