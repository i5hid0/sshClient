import sys, socket, libssh2



def connect(address, mode=0, info='', port=22):
    if mode == 0:
        print 'password'
    if mode == 1:
        print 'key'
    
    
    global cli
    cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cli.connect((address, int(port)))
    global session
    session = libssh2.Session()
    session.startup(cli)
    try:
        session.userauth_publickey_fromfile('ishido', '/home/ishido/.ssh/id_rsa.pub', '/home/ishido/.ssh/id_rsa')
    except (libssh2.Error):
        pass
    
    message = ''
    
    if session.authenticated is True:
        message = 1
        return message, session
    else:
        return message, session

def disconnect():
    cli.close()
    
def execCommand(command):
#    gr = Graphics().__init__()
    channel = session.channel()
    channel.execute(command)
    buff = ''
    
    while channel.read(2048):
#        print channel.read(1024)
        
#        print output(channel.read(1024))
#        buff += channel.read(2048)
#        gr.infoText.setText(buff)
        return channel.read(2048)

def output(*args):
    return args[0]

#disconnect()
