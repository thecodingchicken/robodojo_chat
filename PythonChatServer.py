#!/usr/bin/python
#Then do py PythonChatServer.py 127.0.0.1 20000
# or py -3 PythonChatServer.py 127.0.0.1 8000
"""This is version 0.0 of the satellite-based python chat server.  
It will make NO attempts currently to work with the ground-based server
"""
import socketserver
import re
import socket
import os
import base64
import time##import time, so you can create the log file for the day
#####STARTING LOG FILE#########
foo = time.asctime().split(' ')
l = [foo[4], foo[1], foo[2]]

def make_log_name(l):
    """you take in a list.  It contains the year, month, and day in that order.  It
returns a nicely formatted name"""
    f = "%s_%s-%s"%(l[0], l[1], l[2])
    return f
def write_text(text):
    bar = open(filen,'a')
    bar.write(text)
    bar.close()
    del bar

def write_p(text, p=0):
    """write text to the file filen in global and if p == 1: print it"""
    if p == 1:print(text)
    write_text(text)
filen = os.path.join('logs', make_log_name(l))
write_p("Started server at \"%s\"\n"%time.asctime())
print("Wrote to log file %s"%filen)
del foo, l, make_log_name

#############END LOG FILE SECTION
def b(string):
    "translate str to bytes"
    return string.encode()
def d(Bytes):
    "translate bytes to str"
    return Bytes.decode()
def join(S, it):
    foo = ""
    it = list(it)
    for i in range(len(it) - 1):
        foo += "%s%s"%(d(it[i]), S)
    foo += '%s'%d(it[-1])
    return foo
##users={'joshb':'Woof!!!','bowej':'!!!fooW'}##Testing
##print(join(', ',users.keys()))##Testing
class ClientError(Exception):
    "An exception thrown because the client gave bad input to the server."
    pass

class PythonChatServer(socketserver.ThreadingTCPServer):
    "The server class."

    def __init__(self, server_address, RequestHandlerClass):
        """Set up an initially empty mapping between a user's nickname
        and the file-like object used to send data to that user."""
        socketserver.ThreadingTCPServer.__init__(self, server_address,
                                                 RequestHandlerClass)
        self.users = {}

class RequestHandler(socketserver.StreamRequestHandler):
    """Handles the life cycle of a user's connection to the chat
    server: connecting, chatting, running server commands, and
    disconnecting."""

    NICKNAME = re.compile('^[A-Za-z0-9_-]+$') #Regex for a valid nickname

    def handle(self):
        """Handles a connection: gets the user's nickname, then
        processes input from the user until they quit or drop the
        connection."""
        self.nickname = None
        self.privateMessage('Who are you?')
        nickname = self._readline()
        done = False
        try:
            self.nickCommand(nickname)
            self.privateMessage('Hello %s, welcome to the Python Chat Server.'\
                                % d(nickname))
            self.broadcast('%s has joined the chat.' % d(nickname), False)
        except ClientError as error:
            self.privateMessage(error.args[0])        
            done = True
        except socket.error:
            done = True
##        print("\"%s\" has logged in."%d(self.nickname))
        write_p("\"%s\" has logged in.  \n"%d(self.nickname), 1)
        # print(dir(self.server))
        write_p("Connection from ip address %s, port %d"%(self.client_address), 1)
        #Now they're logged in; let them chat.
        while not done:
            try:
                done = self.processInput()
            except ClientError as error:
                self.privateMessage(str(error))
            except socket.error as e:
                done = True

    def finish(self):                        
        "Automatically called when handle() is done."
        if self.nickname:
            #The user successfully connected before disconnecting. 
            #Broadcast that they're quitting to everyone else.
            message = '%s has quit.' % d(self.nickname)
            if hasattr(self, 'partingWords'):
                message = '%s has quit: %s' % (d(self.nickname),
                                               self.partingWords)
            self.broadcast(message, False)

            #Remove the user from the list so we don't keep trying to
            #send them messages.
            if self.server.users.get(self.nickname):
                write_p("\"%s\" has quit.\n"%d(self.nickname),1)
                del(self.server.users[self.nickname])
        self.request.shutdown(2)
        self.request.close()

    def processInput(self):
        """Reads a line from the socket input and either runs it as a
        command, or broadcasts it as chat text."""
        done = False
        l = self._readline()
        command, arg = self._parseCommand(l)
        if command:
            write_p("\"%s\" has executed %s.\n"%(d(self.nickname), d(l)) ,1)
            done = command(arg)
        else:
            l = '<%s> %s\n' % (d(self.nickname), d(l))
            write_p("To all: %s"%l)
            self.broadcast(l)
        return done
    #Each server command is implemented as a method. The _parseCommand method, defined later, takes a line that looks like /nick and calls the corresponding method (in this case, nickCommand):
    #Below are implementations of the server commands.

    def nickCommand(self, nickname):
        """Attempts to change a user's nickname."""
        if not nickname:
            raise ClientError('No nickname provided.')
        if type(nickname)==str:
            nickname=b(nickname)
        if not self.NICKNAME.match(d(nickname)):
            raise ClientError ('Invalid nickname: "%s"' % d(nickname))
        if nickname == self.nickname:
            raise ClientError ('You are already known as "%s".' % d(nickname))
        if self.server.users.get(nickname, None):
            raise ClientError ('There\'s already a user named "%s" here.' % nickname)
        oldNickname = None
        if self.nickname:
            oldNickname = self.nickname
            del(self.server.users[self.nickname])
        self.server.users[nickname] = self.wfile
        self.nickname = nickname
        if oldNickname:
            self.broadcast('%s is now known as %s' % (d(oldNickname),
                                                      d(self.nickname)))
    def quitCommand(self, partingWords):
        """Tells the other users that this user has quit, then makes
        sure the handler will close this connection."""
        if partingWords:
            self.partingWords = partingWords
        #Returning True makes sure the user will be disconnected.
        return True
    def kickCommand(self, user):
        # print(self.nickname,user,[d(f) for f in self.server.users], sep=':')
        # print(dir(self))
        if d(self.nickname) == 'joshb':
            # print(len(self.server.users))
            # print([f.nickname for f in self.server.users])
            if b(user) in self.server.users:
                self.broadcast('~!kick%s'%user)
                write_p('~!kick%s'%user,1)
            else:
                self.privateMessage("Invalid username.")
        else:
            self.privateMessage("You do not have these permissions.")
    def mooseCommand(self, ignored):
        write_p("%s wants to know about The Moose"%d(self.nickname),1)
        self.privateMessage("""Moose added soon.""")
    def namesCommand(self, ignored):
        "Returns a list of the users in this chat room."
        user_list=join(', ',self.server.users.keys())
        self.privateMessage(user_list)
    def msgCommand(self,nickAndMsg):
        "Send a private message to another user"
        if type(nickAndMsg)==None or type(nickAndMsg)==type(None):
            self.privateMessage("No input given")
            return
        if len(nickAndMsg)==0:
            self.privateMessage("No input given")
            return
        if not ' ' in nickAndMsg:
            self.privateMessage("No message given, use a space ' ' to give one")
            return
        nick,msg=nickAndMsg.split(' ',1)
        if nick==self.nickname:
            self.privateMessage("What, send a message to yourself?")
            return
        user = self.server.users.get(b(nick))
##        print(user,nick,self.server,self.server.users)
        if not user:
            self.privateMessage("No such user: '%s'"%nick)
            return
        msg="[Private from %s] %s\r\n"%(d(self.nickname),msg)
        write_p(msg)
##        write_p("%s:%s"%(user,type(user)),1)
        user.write(b(msg))
        return
    # Below are helper methods.
    
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
            write_p("User %s tried to run '/_parse'."%d(self.nickname),1)
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
    sys.argv.append('127.0.0.1');sys.argv.append('27272')
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
        PythonChatServer((hostname, port), RequestHandler).serve_forever()
    except (KeyboardInterrupt, EOFError):
        print("Stopped Server")
        write_p("Stopped Server at %s\n"%time.asctime())
        sys.exit(0)