#!/usr/bin/python
#Then do py PythonChatServer.py 127.0.0.1 20000
# or py -3 PythonChatServer.py 127.0.0.1 8000
"""This is version 0.0 of the satellite-based python chat server.  
It will make NO attempts currently to work with the ground-based server
"""
import base64
import os
import re
import socket
import socketserver
import time
import pychatfuncs
from pychatfuncs import b, d, join, ClientError
#####STARTING LOG FILE#########
foo = time.asctime().split(' ')
l = [foo[4], foo[1], foo[2]]
ADMIN_EMAIL_ADDRESS = "joe@robodojo.io"
VALID_CHARS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
               'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
               'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd',
               'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
               'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']


##### END LOG FILE SECTION #####


class UserId():
   def __init__(self, name, userid=None):
      self.name = name
      if userid is not None:
         if type(userid) != str:
            userid = None
         else:
            if len(userid) != 9:
               userid = None
            self.userid = userid
      if userid is None:
         #We must have a new user, so we need to generate
         #a user id.  the id consists of 9 chars, each of
         # which can be a letter or number
         allowed = []##Do later
         raise Exception("Do stuff here")
         self.userid = None
   def text(self):
      return "UserId(\"%s\", \"%s\""%(self.name,self.userid)

class PythonChatServerSatt(socketserver.ThreadingTCPServer):
    "The server class for the satellite."

    def __init__(self, server_address, RequestHandlerClass, users_file):
        """Set up an initially empty mapping between a user's nickname
        and the file-like object used to send data to that user."""
        socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                 RequestHandlerClass)
        self.users = {}
        self.users_file = users_file
    def confirm_user(self, username):
        user_file = open(self.users_file, 'r')
        user_line = username
        for line in user_file:
            if line.strip() == user_line:
                return True
        del user_file, user_line, line
        return False
class RequestHandler(socketserver.StreamRequestHandler):
    """Handles the life cycle of a user's connection to the chat
    server: connecting, chatting, running server commands, and
    disconnecting."""

    NICKNAME = re.compile('^[A-Za-z0-9_-]+$') #Regex for a valid nickname
    def handle(self):
        """Handle the user's input.  No nickname is used, but
        user-id IS needed.  It takes in input in the form of
        a command, and can reply back.  A connection is quick, 
        with not much happening.
       """
        self.userid = None
        self.privateMessage("PythonChatServerSatt")
        #The above line is for authentication reasons
        username_userid = self._readline()
        if d(username_userid).count(":") != 1:
            self.privateMessage("Hey! Let the required client software")
            self.privateMessage("take care of that!")
            done = True
            return
        print("got username %s"%username)
        confirm = self.server.confirm_user(username_userid)
        if not confirm:
            self.privateMessage("Hey! You need a valid username and user-id")
            self.privateMessage("To get one, contact the system admins at")
            self.privateMessage(ADMIN_EMAIL_ADDRESS)
            return
        self.privateMessage("Valid login.")
        message = self._readline()
        self.continue_code(message)
    def continue_code(self, message):
        print(message)



    def processInput(self):
        """Reads a line from the socket input and either runs it as a
        command, or broadcasts it as chat text."""
        done = False
        l = self._readline()
        command, arg = self._parseCommand(l)
        if command:
            pychatfuncs.write_p("\"%s\" has executed %s.\n"%(d(self.nickname), d(l)) ,1)
            done = command(arg)
        else:
            l = '<%s> %s\n' % (d(self.nickname), d(l))
            pychatfuncs.write_p("To all: %s"%l)
            self.broadcast(l)
        return done
    def broadcast(self, message, includeThisUser=True):
        """Send a message to every connected user, possibly exempting the
        user who's the cause of the message."""
        message = self._ensureNewline(message)
        for user, output in self.server.users.items():
            if includeThisUser or user != self.nickname:
                output.write(b(message))

    def privateMessage(self, message):
        "Send a private message to this user."
        # message=encode_text(message)
        n=self._ensureNewline(message).encode()
        self.wfile.write(n)

    def _readline(self):
        "Reads a line, removing any whitespace."
        return self.rfile.readline().strip()

    def _ensureNewline(self, s):
        "Makes sure a string ends in a newline."
        if s and s[-1] != '\n':
            s += '\r\n'
        return s

    def _parseCommand(self, i):
        """Try to parse a string as a command to the server. If it's an
        implemented command, run the corresponding method."""
        try:
            i=d(i)
        except AttributeError:
            pychatfuncs.write_p("User %s tried to run '/_parse'."%d(self.nickname),1)
            raise ClientError("Don't try that!")
        commandMethod, arg = None, None
        if i and i[0] == '/':
            if len(i) < 2:
                raise ClientError( 'Invalid command: "%s"' % i)
            commandAndArg = i[1:].split(' ', 1)
            if len(commandAndArg) == 2:
                command, arg = commandAndArg
            else:
                command, = commandAndArg
            commandMethod = getattr(self, command + 'Command', None)
            if not commandMethod:
                raise ClientError( 'No such command: "%s"' % command)
        return commandMethod, arg
if __name__ == '__main__':
    import sys
    # sys.argv.append('127.0.0.1');sys.argv.append('27272')
    if len(sys.argv) == 1:
        print('Usage: %s [hostname] [port number]' % sys.argv[0])
        sys.exit(1)
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['help','commands','-h','--help']:
            print("Future help here")
            sys.exit(1)
        elif sys.argv[1] in ('log', 'logs'):
            print("Logs are in the ./logs folder.")
            sys.exit(1)
        else:
            print("Unknown command")
            sys.exit(1)
    elif len(sys.argv) > 3:
        print("[WARNING] Only first 3 args are used currently!  ")
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    try:
        PythonChatServerSatt((hostname, port), RequestHandler, "./users").serve_forever()
    except (KeyboardInterrupt, EOFError):
        print("Stopped Server")
        pychatfuncs.write_p("Stopped Server at %s\n"%time.asctime())
        sys.exit(0)