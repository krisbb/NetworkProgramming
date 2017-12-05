import socket
import json
import base64

LENGTHOFMESSAGE = 512

class ClientSocket:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host
        self.port = port

    def close(self):
        self.sock.close()

    def ehlo(self, host):
        template = 'EHLO {}'.format(host)
        print('Sending -> {}'.format(template))
        self.send(template)

    def auth(self):
        template = 'AUTH LOGIN'
        print('Sending -> {}'.format(template))
        self.send(template)

    def mailFrom(self, sender):
        template = 'MAIL FROM:<{}>'.format(sender)
        print('Sending -> {}'.format(template))
        self.send(template)

    def rcptTo(self, recipient):
        template = 'RCPT TO:<{}>'.format(recipient)
        print('Sending -> {}'.format(template))
        self.send(template)

    def data(self):
        template = 'DATA'
        print('Sending -> {}'.format(template))
        self.send(template)

    def sendMail(self,mail):
        encodedMsg = str.encode(mail)
        howMuchWasSent = self.sock.send(encodedMsg + b'\r\n' + str.encode('.') + b'\r\n')
        # print(howMuchWasSent)
        if howMuchWasSent == 0:
            raise RuntimeError("socket connection broken")

    def quit(self):
        template = 'QUIT'
        print('Sending -> {}'.format(template))
        self.send(template)

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

FinalMail = 'From: {}\nTo: {}\nSubject: {}\n{}\n'

if __name__ == '__main__':
    json_config = {}

    with open('config.json') as file:
        json_config = json.load(file)

    login = json_config['credentials']['login']
    passwd = json_config['credentials']['password']
    login64 = base64.encodebytes(str.encode(login))
    passwd64 = base64.encodebytes(str.encode(passwd))
    host = json_config['address']['host']
    port = json_config['address']['port']

    clientSock = ClientSocket(host, port)
    list_output = ''
    new_list_output = ''
    try:
            clientSock.connect()
            print(clientSock.receive())
            clientSock.ehlo(host)
            print(clientSock.receive())
            clientSock.auth()
            print(clientSock.receive())
            clientSock.send(login64.decode()[:-1])
            print(clientSock.receive())
            clientSock.send(passwd64.decode()[:-1])
            print(clientSock.receive())
            clientSock.mailFrom(login)
            print(clientSock.receive())
            clientSock.rcptTo(login)
            print(clientSock.receive())
            clientSock.data()
            print(clientSock.receive())
            clientSock.sendMail(FinalMail.format(login, login, 'test', 'test'))
            print(clientSock.receive())
            clientSock.quit()
            print(clientSock.receive())
    except Exception as e:
        print(e.args)
    finally:
        clientSock.close()
