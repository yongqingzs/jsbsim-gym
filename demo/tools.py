import sys
import time

class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'w')  # 'a' to append ; 'w' to overwrite
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def log_write(self, message):
        self.log.write(message)

    def flush(self):
        pass
