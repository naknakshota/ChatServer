# COMP 332, Spring 2018
# Chat server
#
# Usage:
#   python3 chat_server.py <host> <port>
#
#**************************************************************************
#              Homework 5: Transport protocols and a chat app
#                       Author: Shota Nakamura
#**************************************************************************
import socket
import sys
import threading

class ChatProxy():

    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.server_backlog = 1
        self.chat_list = {}
        self.chat_id = 0
        self.lock = threading.Lock()
        self.start()

    def start(self):

        # Initialize server socket on which to listen for connections
        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind((self.server_host, self.server_port))
            server_sock.listen(self.server_backlog)
        except OSError as e:
            print ("Unable to open server socket")
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Wait for user connection
        while True:
            conn, addr = server_sock.accept()
            self.add_user(conn, addr)
            thread = threading.Thread(target = self.serve_user,
                    args = (conn, addr, self.chat_id))
            thread.start()

    def add_user(self, conn, addr):
        print ('User has connected', addr)
        self.chat_id = self.chat_id + 1
        self.lock.acquire()
        self.chat_list[self.chat_id] = (conn, addr)
        self.lock.release()

    def get_value(self, msg, name, endflag):
        try:
            #Find indices with starting name 
            start_name = msg.find(name)
			
            #Add the length of the value to get ending indices
            end_name = len(name) + start_name
            end_value = msg[end_name: ].index(endflag) + end_name 

            #Get the value of a field 
            value = msg[end_name : end_value]
            return value
        #Throw exception if field does not exist
        except ValueError as e:
            print('Field not found: ', e)
            return -1


    def read_data(self, conn):
        data = b""
        while True:
            #Receive Data
            data += (conn.recv(4096))

            #Decode the data
            decode_data = data.decode('utf-8')

            try:
                #Save size header
                size = int(self.get_value(decode_data, 'Message Size: ', 'end_size'))

                #Save the actual input as data 
                start_msg = decode_data.find('end_header') + len('end_header')
                end_msg = start_msg + size
                data = data[end_msg :]
                
                return (decode_data[: end_msg]).encode('utf-8')

            except ValueError:
                print("Value Error")
                    
            
        print("In read data")

        return data

    def send_data(self, user, data):
        self.lock.acquire()
        for i in self.chat_list:
            if i != user: #Broadcasts to everyone
                (self.chat_list[i][0]).sendall(data)

        self.lock.release()

    def cleanup(self, conn, user):
        self.lock.acquire()
        #Pop is the call for a dictionary
        (self.chat_list).pop(user)

        print("In cleanup")

        self.lock.release()

    def serve_user(self, conn, addr, user):
        while True:
            data = self.read_data(conn)
            if (data).decode('utf-8') == "":
                self.cleanup(conn, user)
                print("User Number"+ str(user) + " removed from chat list")
                return               
            self.send_data(user, data)
            print("Serving User" + str(user))


def main():

    print (sys.argv, len(sys.argv))
    server_host = 'localhost'
    server_port = 50007

    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    chat_server = ChatProxy(server_host, server_port)

if __name__ == '__main__':
    main()
