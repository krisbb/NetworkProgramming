import socket
import json


LENGTHOFMESSAGE = 8192
helpString = 'You can use commands like - ls, cd <path>, up, tree, pwd, quit, help'

class ClientSocket:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = host
        self.port = port

    def close(self):
        self.sock.close()

    def user(self, user_name):
        template = 'USER {}'.format(user_name)
        print('Sending -> {}'.format(template))
        self.send(template)

    def passwd(self, password):
        template = 'PASS {}'.format(password)
        print('Sending -> {}'.format(template))
        self.send(template)

    def pasv(self, debug=0):
        template = 'PASV'
        if debug == 0:
            print('Sending -> {}'.format(template))
        self.send(template)

    def type(self, option):
        template = 'TYPE {}'.format(option)
        print('Sending -> {}'.format(template))
        self.send(template)

    def cwd(self, directory):
        template = 'CWD {}'.format(directory)
        print('Sending -> {}'.format(template))
        self.send(template)

    def cup(self):
        template = 'CDUP'
        print('Sending -> {}'.format(template))
        self.send(template)

    def pwd(self):
        template = 'PWD'
        print('Sending -> {}'.format(template))
        self.send(template)

    def list(self):
        return self.sendPassiveCmd('LIST')

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

    def parsePasvResp(self, resp):
        # print(resp)
        substring = resp[resp.find('(') + 1:resp.find(')')]
        numbers = substring.split(',')
        host = '{}.{}.{}.{}'.format(*numbers[0:-2])
        port = int(numbers[4])*256 + int(numbers[5])
        return host, port

    def sendPassiveCmd(self, cmd):
        self.pasv(1)
        host, port = self.parsePasvResp(self.receive())
        pasvSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pasvSock.connect((host, port))
        self.send(cmd)
        result = receiveFromSock(pasvSock)
        self.receive()
        pasvSock.close()
        self.receive()
        return result

    def getFtpTree(self, path='', depth=0):
        # get list of files in '/'

        result_string = ''
        if path != '':
            self.send('CWD {}'.format(path))
            resp = self.receive()
            if resp[0] != '2':
                return ''

        list = self.sendPassiveCmd('NLST').replace('\r', '').split('\n')
        for file in list:
            if depth != 0:
                result_string += depth * '\t' + '-'

            if file == '':
                result_string += '.'
            else:
                result_string += file + '\n'
                result_string += self.getFtpTree(path + '/' + file, depth+1) + '\n'

        return result_string


def receiveFromSock(sock):
    data = sock.recv(LENGTHOFMESSAGE)
    return data.decode()


if __name__ == '__main__':
    json_config = {}

    with open('config.json') as file:
        json_config = json.load(file)

    login = json_config['credentials']['login']
    passwd = json_config['credentials']['password']
    host = json_config['address']['host']
    port = json_config['address']['port']

    path_to_login = input('Please give path to login: ')

    clientSock = ClientSocket(host, port)
    clientSock.connect()
    print(clientSock.receive())
    clientSock.user(login)
    print(clientSock.receive())
    clientSock.passwd(passwd)
    print(clientSock.receive())

    if path_to_login != '':
        clientSock.cwd(path_to_login)
        print(clientSock.receive())

    print(helpString)
    try:
        while True:
            arg = ''
            cmd = input('Write msg: ')

            if cmd[:2] == 'cd':
                cmd, arg = cmd.split(' ')

            if cmd == 'up':
                clientSock.cup()
                print(clientSock.receive())
            elif cmd == 'cd':
                clientSock.cwd(arg)
                print(clientSock.receive())
            elif cmd == 'tree':
                print(clientSock.getFtpTree('/'))
            elif cmd == 'pwd':
                clientSock.pwd()
                print(clientSock.receive())
            elif cmd == 'ls':
                print(clientSock.list())
            elif cmd == 'help':
                print(helpString)
            elif cmd == 'quit':
                clientSock.quit()
                print(clientSock.receive())
                break

    except Exception as e:
        print(e.args)
    finally:
        clientSock.close()
