#
# COMP 332, Spring 2018
# Chat client
#
# Example usage:
#
#   python3 chat_client.py <chat_host> <chat_port>
#
#**************************************************************************
#              Homework 5: Transport protocols and a chat app
#                       Author: Shota Nakamura
#**************************************************************************
import socket
import sys
import threading


class ChatClient:

    def __init__(self, chat_host, chat_port):
        self.chat_host = chat_host
        self.chat_port = chat_port
        self.username = input('Enter Username: ')
        self.start()

    def start(self):

        # Open connection to chat
        try:
            chat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            chat_sock.connect((self.chat_host, self.chat_port))
            print("Connected to socket")
        except OSError as e:
            print("Unable to connect to socket: ")
            if chat_sock:
                chat_sock.close()
            sys.exit(1)

        threading.Thread(target=self.write_sock, args=(chat_sock,)).start()
        threading.Thread(target=self.read_sock, args=(chat_sock,)).start()

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

        #Throw exception if no value
        except ValueError as e:
            print('Field not found: ', e)
            return -1

    def write_sock(self, sock):
        while True:
            #Prompt User to add Message
            msg = input()

            #Size of the message 
            m_size = str(len(msg))

            #Header Construction
            construct = ('Message Size: ' + m_size + 'end_size' +  'Username: ' + self.username + 'endname' +  'end_header' + msg).encode('utf-8')
            sock.sendall(construct)

        print("In write sock")
    def read_sock(self, sock):
        data = b""
        while True:
            #Receive the data
            data += (sock.recv(4096))
            #Decode the data 
            decode_data = data.decode('utf-8')
            try:
                #Taking headers of fields 
                #Get the size of the whole message
                size = int(self.get_value(decode_data, 'Message Size: ', 'end_size'))

                #Get the username of the client
                username = self.get_value(decode_data, 'Username: ', 'endname')

                #Get the beginning of the message (index)
                start_msg = decode_data.find('end_header') + len('end_header')

                #End of message index
                end_msg = start_msg + size
                
                if len(decode_data) >= int(end_msg):
                    print(username + ": " + decode_data[start_msg: end_msg])

                data = data[end_msg :]
            except ValueError:
                print("Value Error")
                    
        print("In read sock")

def main():

    print (sys.argv, len(sys.argv))
    chat_host = 'localhost'
    chat_port = 50007

    if len(sys.argv) > 1:
        chat_host = sys.argv[1]
        chat_port = int(sys.argv[2])

    chat_client = ChatClient(chat_host, chat_port)

if __name__ == '__main__':
    main()
