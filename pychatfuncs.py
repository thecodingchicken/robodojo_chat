#!/bin/bash python3
import os
import time

FILEN = os.path.join('logs', make_log_name(l))

def make_log_name(l):
    """you take in a list.  It contains the year, month, and day in that order.  It
returns a nicely formatted name"""
    f = "%s_%s-%s"%(l[0], l[1], l[2])
    return f

def write_text(text, filen):
    bar = open(filen,'a')
    bar.write(text)
    bar.close()
    del bar

def write_p(text, p=0, filen = FILEN):
    """write text to the file filen in global and if p == 1: print it"""
    if p == 1:print(text)
    write_text(text)

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

class ClientError(Exception):
    "An exception thrown because the client gave bad input to the server."
    pass