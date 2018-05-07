#!/usr/bin/python
import socket
import select
import sys
import os
from threading import Thread
def b(text):return text.encode()
def d(text):return text.decode()
class ChatClient:
    """run with the following commands
cd C:\\Users\\Joshua Bowe\\Downloads\\python code downloaded\\Chapter 16
python PythonChatClient.py 127.0.0.1 20000 joshb"""
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.input = self.socket.makefile('rb', 0)
        self.output = self.socket.makefile('wb', 0)
        username = input("username: ")
        userid = input("userid: ")

        authenticationDemand = self.input.readline()
        if d(authenticationDemand).count('PythonChatServerSatt')!= 1:
            raise Exception("Not a python chat satellite")
        self.output.write(b("%s:%s"%(username, userid)))
        print(self.input.readline())
        return
        self.run()

    def run(self):
        """Start a separate thread to gather the input from the
        keyboard even as we wait for messages to come over the
        network. This makes it possible for the user to simultaneously
        send and receive chat text."""
        
        propagateStandardInput = self.PropagateStandardInput(self.output)
        propagateStandardInput.start()

        #Read from the network and print everything received to standard
        #output. Once data stops coming in from the network, it means
        #we've disconnected.
        inputText = True
        while inputText:
            inputText = self.input.readline()
            if inputText:
                if d(inputText).startswith('~!kick'):
                    if d(inputText) == '~!kick%s\r\n'%nickname:
                        print("Kicked by server admins...")
                        self.output.write(b("/quit Oh poop I got kicked!\r\n"))
                    # propagateStandardInput.done = True
                else:
                    print(d(inputText.strip()))
        propagateStandardInput.done = True

    class PropagateStandardInput(Thread):
        """A class that mirrors standard input to the chat server
        until it's told to stop."""

        def __init__(self, output):
            """Make this thread a daemon thread, so that if the Python
            interpreter needs to quit it won't be held up waiting for this
            thread to die."""
            Thread.__init__(self)
            self.setDaemon(True)
            self.output = output
            self.done = False

        def run(self):
            "Echo standard input to the chat server until told to stop."
            while not self.done:
                inputText = sys.stdin.readline().strip()
                if inputText:
                    self.output.write(b(inputText + '\r\n'))

if __name__ == '__main__':
    import sys
    hostname = sys.argv[1]
    port = int(sys.argv[2])

    ChatClient(hostname, port)
##    josh = ChatClient('127.0.0.1',20000,'joshb')
