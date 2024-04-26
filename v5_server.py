#VERSION_5 COMBINED CODE SERVER TEST - JADEN AND CONNOR
import socket
import threading
import sys
import pymongo
import json

from v5_funcs import addEmployee
from v5_funcs import delEmployee
from v5_funcs import orderInventory
from v5_funcs import clockIn
from v5_funcs import clockOut
from v5_funcs import editInventory

dbconnection = pymongo.MongoClient("mongodb+srv://connorjones165:G2UrB1t990Bcyy06@cluster0.xqbxg1f.mongodb.net/?retryWrites=true&w=majority")
db = dbconnection["ShoeFlu"]
collection_logins = db["Logins"]
collection_inventory = db["Inventory"]

clients_lock = threading.Lock()
clients = []
running = True
us_data = ""#GLOBAL USERNAME - need this for clock in/out

#CONNOR FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def check_logins(username, password):
    data  = list(collection_logins.find({"$and": [{"username": username}, {"password": password}]}).limit(1))
    for d in data:
        usernameValue = json.dumps(d["username"])
        passwordValue = json.dumps(d["password"])# converts dictionary to string
        flagValue = json.dumps(d["admin"])
        #print(flagValue)
        usernameValue = usernameValue.replace('"', '')
        passwordValue = passwordValue.replace('"', '')
        
        if(usernameValue == username and passwordValue == password and flagValue == "1"):
            print("\nADMIN FOUND and PASSWORD MATCHES", username)
            return 1
        elif(usernameValue == username and passwordValue == password and flagValue == "0"):
            print("\nEMPLOYEE FOUND and PASSWORD MATCHES", username)
            return 2
        
    print("user not found/pw doesn't match")
    return 0
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



#JADEN FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_data(coll):
    data = []
    for x in coll.find():
        del x['_id']
        data.append(x)
    return str(data)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def handle_client(client_socket, client_address):
    global clients
    print('Connected to', client_address)

    with clients_lock:
        clients.append(client_socket)

    try:
        while True:
             # Receive a message from the client
            message = client_socket.recv(1024).decode('utf-8')
            if message == "1":
                print("\n1: Checking database for credentials...")
                us_data = client_socket.recv(1024).decode()
                print('Client username: ', us_data)
                pw_data = client_socket.recv(1024).decode()
                print("Client password: ", pw_data)
                if check_logins(us_data,pw_data) == 1:
                    user_msg = "1"
                    client_socket.send(user_msg.encode('utf-8'))
                elif check_logins(us_data,pw_data) == 0:
                    user_msg = "0"
                    client_socket.send(user_msg.encode('utf-8'))
                elif check_logins(us_data,pw_data) == 2:
                    user_msg = "2"
                    client_socket.send(user_msg.encode('utf-8'))
                  
            if message == "2":
                print("\n2: Sending inventory list to client...")
                client_socket.send(get_data(collection_inventory).encode('utf-8'))
                
            if message == "4":
                print("\n4: Client is adding user to database...")
                name = ""
                pw = ""
                flag = 0
                working = 0
                salary = "$40,000"
                user_msg = "Enter name of employee you wish to add: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    name = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                user_msg = "Enter password for user: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    pw = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                user_msg = "Is this user: 1)Admin or 2)General Staff\nEnter 1 or 2: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    flagmsg = client_socket.recv(1024).decode('utf-8')
                    if flagmsg == "1":
                        flag = 1
                        salary = "$100,000"
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                userexist = addEmployee(name,pw,flag,working,salary)
                if userexist:
                    client_socket.send("user already exist".encode('utf-8'))
                else:
                    client_socket.send("user added".encode('utf-8'))
                
                
            if message == "5":
                print("\n5: Client is deleting user from database..")
                name = ""
                user_msg = "Enter name of employee you wish to remove: "
                client_socket.send(user_msg.encode('utf-8'))
                try:
                    name = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                success = delEmployee(name)
                if success:
                    client_socket.send('User deleted'.encode('utf-8'))
                else: 
                    client_socket.send("User does not exist".encode('utf-8'))
            
            if message == "6":
                print("\n6: ordering inventory function")
                name = ""
                brand = ""
                size = ""
                quantity = ""
                price = ""
                user_msg = "Enter name of shoe you wish to order: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    name = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                user_msg = "Enter shoe brand: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    brand = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                user_msg = "Enter shoe size:"
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    size = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                    
                user_msg = "Enter integer quantity you wish to order: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    quantity = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                user_msg = "Enter shoe price: "
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    price = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
               
                collection_inventory.insert_many(orderInventory(name,brand,size,quantity,price))
            
            if message == "7":
                print("\n7: Client is printing employee list...")
                client_socket.send(get_data(collection_logins).encode('utf-8'))
                
            if message == "8":
                print("\n8: Client is clocking in...")
                try:
                    clockIn(us_data)
                    user_msg = "\nYou are now on the clock. Get to work!"
                    client_socket.send(user_msg.encode('utf-8'))
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
            if message == "9":
                print("\n8: Client is clocking out...")
                try:
                    clockOut(us_data)
                    user_msg = "\nYou are now off the clock. Go Home!"
                    client_socket.send(user_msg.encode('utf-8'))
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                    
            if message == "10":
                print("\n10: Client just sold some shoes...")
                user_msg = "Which shoe did you sell?\n"
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    shoe = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                    
                user_msg = "How many pairs did you sell?\n"
                client_socket.send(user_msg.encode('utf-8'))
                
                try:
                    amount = client_socket.recv(1024).decode('utf-8')
                except Exception as e:
                    print(f"[!] An exception occurred with {client_address}: {e}")
                
                editInventory(shoe,amount)
                    
            if message.lower() == 'exit':  # Check if the client sent the exit command
                farewell_message = f"{client_address} has left the server."
                print(farewell_message)
                break
            
            

    except ConnectionResetError:
        print(f"[-] Connection reset by {client_address}")
    except Exception as e:
        print(f"[!] An exception occurred with {client_address}: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        client_socket.close()
        print(f"[-] Connection from {client_address} has been closed.")

    
def main():
    global running
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#ignore error
    #REUSE address,in case u kill program and run it again
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#ignore erro
    # Bind the socket to a specific address and port
    server_address = ('0.0.0.0', 12345) #keep as 0000
    server_socket.bind(server_address)
    
    #max clients in queue will be 5
    server_socket.listen(5)
    
    print('Server is listening on', server_address)
    
    try:
        while running:
            client_socket, addr = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_handler.daemon = True
            client_handler.start()
    except Exception as e:
        print(f"[!] An exception occurred: {e}") #printf format
        
if __name__ == "__main__":
    main()