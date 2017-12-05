import socket
import json
from time import sleep

LENGTHOFMESSAGE = 512


class ClientSocket:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host
        self.port = port

    def cmdUser(self, user_name):
        templateCmd = 'USER {}'.format(user_name)
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.receive())

    def cmdPass(self, password):
        templateCmd = 'PASS {}'.format(password)
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.receive())

    def cmdQuit(self):
        templateCmd = 'QUIT'
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.receive())

    def cmdStat(self):
        templateCmd = 'STAT'
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.receive())

    def cmdList(self, msg=''):
        if msg != '':
            msg = ' ' + msg
        templateCmd = 'LIST{}'.format(msg)
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        output = self.multiReceive()
        print(output)
        return output

    def cmdRetr(self, msg):
        templateCmd = 'RETR {}'.format(msg)
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.multiReceive())

    def cmdDele(self, msg):
        # no use in this client
        pass

    def cmdNoop(self):
        # no use in this client
        pass

    def cmdRset(self):
        templateCmd = 'RSET'
        print('Sending -> {}'.format(templateCmd))
        self.send(templateCmd)
        print(self.receive())

    def close(self):
        self.sock.close()

    def connect(self):
        self.sock.connect((host, port))
        self.sock.setblocking(True)

    def receive(self):
        data = self.sock.recv(LENGTHOFMESSAGE)
        return data.decode()

    def multiReceive(self):
        wholeString = ''

        while True:
            data = self.sock.recv(LENGTHOFMESSAGE)
            wholeString += data.decode()
            if '\r\n.\r\n' in data.decode():
                wholeString = wholeString[:len(wholeString)-3]
                break

        return wholeString

    def send(self, msg):
        encodedMsg = str.encode(msg)
        howMuchWasSent = self.sock.send(encodedMsg + b'\r\n')
        #print(howMuchWasSent)
        if howMuchWasSent == 0:
            raise RuntimeError("socket connection broken")

if __name__ == '__main__':
    json_config = {}

    with open('config.json') as file:
        json_config = json.load(file)

    login = json_config['credentials']['login']
    passwd = json_config['credentials']['password']
    host = json_config['address']['host']
    port = json_config['address']['port']

    clientSock = ClientSocket(host, port)
    list_output = ''
    new_list_output = ''
    try:
        # first connect and remember list output
        clientSock.connect()
        clientSock.cmdUser(login)
        clientSock.cmdPass(passwd)
        clientSock.cmdStat()
        list_output = clientSock.cmdList()
        clientSock.cmdQuit()

        while True:
            clientSock = ClientSocket(host, port)
            clientSock.connect()
            clientSock.cmdUser(login)
            clientSock.cmdPass(passwd)
            clientSock.cmdStat()
            new_list_output = clientSock.cmdList()
            if new_list_output not in list_output:
                clientSock.cmdRetr(1)
                clientSock.cmdQuit()
                break

            clientSock.cmdQuit()
            print('Sleep 10 seconds')
            sleep(10)
    except Exception as e:
        print(e.args)
    finally:
        clientSock.close()
