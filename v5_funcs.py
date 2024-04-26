#VERSION_5 FUNCS
import pymongo
import json
dbconnection = pymongo.MongoClient("mongodb+srv://connorjones165:G2UrB1t990Bcyy06@cluster0.xqbxg1f.mongodb.net/?retryWrites=true&w=majority")
db = dbconnection["ShoeFlu"]
collection_logins = db["Logins"]
collection_inventory = db["Inventory"]


#GENERAL FUNCS
def to_diction(data):
    count = 0
    list_diction = []
    while count < len(data):
        temp = ""
        if data[count] == '{' :
            while data[count] != '}' :
                temp += data[count]
                count = count + 1
            temp += '}'
            list_diction.append(eval(temp.replace("'", "\"")))
            temp = ''
        count = count + 1
    return list_diction
###################################################################
#LOGINS COLLECTIONS
def addEmployee(name,pw,flag,working,salary):
    print(name, pw, flag, working,salary)
    name = name.lower()
    logins = [{
                "username": name,
                "password": pw,
                "admin": flag,
                "on_shift": working,
                "salary": salary
            }]
    data  = list(collection_logins.find({"username": name}).limit(1))
    for d in data:
        usernameValue = json.dumps(d["username"])
        usernameValue = usernameValue.replace('"', '')
        if(usernameValue == name):
            print("USER FOUND", name)
            return True
    print('adding user', name)
    collection_logins.insert_many(logins)
    return False
    
    
def delEmployee(name):
    name = name.lower()
    print("deleting employee:",name)
    # manual check
    delete_query = {"username": name}
    data  = list(collection_logins.find({"username": name}).limit(1))
    for d in data:
        usernameValue = json.dumps(d["username"])
        usernameValue = usernameValue.replace('"', '')
        if(usernameValue == name):
            print("USER FOUND", name)
            collection_logins.delete_one(delete_query)
            print(name, "has been removed from the database")
            return True
    print('user', name, 'does not exist')
    return False


def printEmployee(client_socket):
    client_socket.send('7'.encode('utf-8'))
    print('{:15s}{:15s}{:15s}{:15s}{:15s}'.format("Username","Password","Admin","On-Shift","Salary"))
    inv = to_diction(client_socket.recv(1024).decode('utf-8'))
    for x in inv:
        print('{:15s}{:15s}{:15s}{:15s}{:15s}'.format(x['username'],"*****",str(x["admin"]),str(x["on_shift"]),x['salary']))

def clockIn(name):
    print("clocking in", name)
    try:
        update_query = {"username": name}
        new_values = {"$set": {"on_shift": 1}}
        collection_logins.update_one(update_query, new_values)
    except Exception as e:
        print(f"An error occurred: {e}") 

def clockOut(name):
    print("clocking out", name)
    try:
        update_query = {"username": name}
        new_values = {"$set": {"on_shift": 0}}
        collection_logins.update_one(update_query, new_values)
    except Exception as e:
        print(f"An error occurred: {e}") 
        
def showMySalary(name):
    data = list(collection_logins.find({"username": name}))
    for d in data:
        dValue = json.dumps(d["salary"])
        print("\n",name,", your salary is:", dValue)
    
###################################################################
#INVENTORY COLLECTION
def printInventory(client_socket):
    client_socket.send('2'.encode('utf-8'))
    print('{:15s}{:15s}{:15s}{:15s}{:15s}'.format("Name","Brand","Price","Quantity","Size"))
    inv = to_diction(client_socket.recv(1024).decode('utf-8'))
    for x in inv:
        print('{:15s}{:15s}{:15s}{:15s}{:15s}'.format(x['name'],x['brand'],x["price"],x["quantity"],x['size']))
        
        
def orderInventory(name,brand,size,quantity,price):
    print(name,brand,size,quantity,price)
    inventory = [
    {
        "name": name,
        "brand": brand,
        "size": size,
        "quantity": quantity,
        "price": price
        }
    ]
    return inventory

def editInventory(shoe,amount):
    dValue = ""
    amount = int(amount)
    data = list(collection_inventory.find({"name": shoe}))
    for d in data:
        dValue = json.dumps(d["quantity"])
        dValue = dValue.replace('"', '')
        dValue = int(dValue)
        print("Original quantity: ",dValue)

    try:
        dValue = dValue - amount
        print("new quantity: ",dValue)
        update_query = {"name": shoe}
        new_values = {"$set": {"quantity": str(dValue)}}
        collection_inventory.update_one(update_query, new_values)
    except Exception as e:
        print(f"An error occurred: {e}") 
        
def shoeExists(shoe):
    data = list(collection_inventory.find({"name": shoe}))
    for d in data:
        dValue = json.dumps(d["name"])
        dValue = dValue.replace('"', '')
        if dValue == shoe:
            return True
        else:
            return False
###################################################################

def manager(client_socket):
    while True:
        print("\nManager Menu")
        print("1) Add Employee")
        print("2) Check Inventory")
        print("3) Remove Employee")
        print("4) Order Inventory")
        print("5) Check Employee List")
        print("6) Logout")
        select = input("Enter Selection: ")
        if select == "1":
            try:
                client_socket.send('4'.encode('utf-8'))
                message = client_socket.recv(1024).decode('utf-8')
                name = input(message)
                client_socket.send(name.encode('utf-8'))
                message = client_socket.recv(1024).decode('utf-8')
                pw = input(message)
                client_socket.send(pw.encode('utf-8'))
                message = client_socket.recv(1024).decode('utf-8')
                flag = input(message)
                while True:
                    if flag == '2' or flag == '1':
                        break
                    else:
                        print('Invalid input, try again')
                client_socket.send(flag.encode('utf-8'))
                message = client_socket.recv(1024)
                print(message)
            except Exception as e:
                print(f"An error occurred: {e}")   
            
        elif select == "2":
            printInventory(client_socket)
        
        elif select == "3":
            client_socket.send("5".encode('utf-8'))
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                name = input(message)
                client_socket.send(name.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
                
            print(client_socket.recv(1024).decode('utf-8'))
        
        elif select == "4":
            #order inventory
            client_socket.send("6".encode('utf-8'))
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                name = input(message)
                client_socket.send(name.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
            try:
                message = client_socket.recv(1024).decode('utf-8')
                brand = input(message)
                client_socket.send(brand.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
            try:
                message = client_socket.recv(1024).decode('utf-8')
                size = input(message)
                client_socket.send(size.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")    
            try:
                message = client_socket.recv(1024).decode('utf-8')
                quantity = input(message)
                client_socket.send(quantity.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")    
            try:
                message = client_socket.recv(1024).decode('utf-8')
                price = input(message)
                client_socket.send(price.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")        
        elif select == "5":
            printEmployee(client_socket)
        elif select == "6":
            #logout
            break
        else:
            print("wrong input")

def employee(client_socket, username):
    while True:
        print("\nEmployee Menu")
        print("1) Clock IN")
        print("2) Clock OUT")
        print("3) Check Inventory")
        print("4) Update Inventory")
        print("5) Show Salary")
        print("6) Logout")
        select = input("Enter Selection: ")
        if select == "1":
            #clock in
            client_socket.send("8".encode('utf-8'))
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                print(message)
            except Exception as e:
                print(f"An error occurred: {e}")
        
        elif select == "2":
            #clock out
            client_socket.send("9".encode('utf-8'))
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                print(message)
            except Exception as e:
                print(f"An error occurred: {e}")
        elif select == "3":
            printInventory(client_socket)
        elif select == "4":
            #edit inventory
            client_socket.send("10".encode('utf-8'))
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                shoe = input(message)
                while not shoeExists(shoe):
                    print("That shoe doesn't exist!")
                    print("try again...")
                    shoe = input(message)
                client_socket.send(shoe.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                amount = input(message)
                client_socket.send(amount.encode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
        elif select == "5":
            showMySalary(username)
        elif select == "6":
            #logout
            break
        else:
            print("wrong input")



