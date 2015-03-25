# -*- coding: utf-8 -*-
import SocketServer
import json
import datetime

connected_clients = []
online_usernames = {}


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        connected_clients.append(self)
        print 'Client connected! ' + self.ip + ':' + str(self.port)

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096)
            if not received_string:
                break
            data = json.loads(received_string)

            if data['request'] == 'login':
                if self.login(data['username']):
                    online_usernames[self.port] = data['username']
                    self.make_package('login', data['username'])
                    self.make_package('message', self.get_datetime() + ' - system : ' + data['username'] + ' joined the channel')

            elif data['request'] == 'logout':
                if not self.login(data['username']):
                    self.make_package('logout', self.get_datetime() + ' - system : ' + data['username'] + ' left the channel')
                    del online_usernames[self.port]

            elif data['request'] == 'users':
                users = self.get_datetime() + ' - system : online users - '
                for i in online_usernames:
                    users += online_usernames[i] + ', '
                self.make_package('users', users)

            elif data['request'] == 'message':
                message = self.get_datetime() + ' - ' + data['username'] + ' : ' + data['message']
                self.make_package('message', message)

    def make_package(self, response, message):
        self.broadcast(json.dumps({'response': response, 'message': message}))


    #When a new message is added, send this to all clients
    def broadcast(self, response):
        for client in connected_clients:
            client.request.sendall(response)

    @staticmethod
    def login(username):
        if username in online_usernames.values():
            return False
        return True

    @staticmethod
    def get_datetime():
        return str(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S'))




class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations is necessary
    """
    allow_reuse_address = True

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations is necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
