#/usr/bin/python3

'''
Date:   2018. Jan. 22nd. Monday
Author: Seyoung Park

Purpose:
    1. SSH into Kosh.
    2. Check uptime of Paniikki machines via 'ssh bit uptime'
    3. Show bash command to launch a notebook. (No this script doesn't launch the notebook).

ATTENTION:
    The code works only when you have your RSA Key registered on the remote.

FIXME:
    Make code so works without RSA Key.
    Now I couldn't find a way to get stdout. Seems like I have to use a socket.
    For instance, the following gives some hint how I could use a socket:

"""
argv = (["ssh", "user@kosh.org.aalto.fi", "ssh bit"])

(s1, s2) = socket.socketpair()

def setup():
    # runs in the child process
    s2.close()
s1a, s1b = os.dup(s1.fileno()), os.dup(s1.fileno())
s1.close()
p = subprocess.Popen(argv, stdin=s1a, stdout=s1b, preexec_fn=setup,
                      close_fds=True)#, stderr=stderr)
# os.close(s1a)
# os.close(s1b)
(serverproc, serversock) = (p, s2)

expected = b'SSHUTTLE0001'
initstring = serversock.recv(len(expected))
initstring
"""

    The above won't work if you don't have a public key set up.
    You get:
        ssh_askpass: exec(/usr/X11R6/bin/ssh-askpass): No such file or directory
        Permission denied, please try again.

    Check sshuttle:
        https://github.com/apenwarr/sshuttle/blob/083293ea0dc2ebc77f282c2803720a2bb5f21a80/sshuttle/ssh.py#L124
        https://github.com/apenwarr/sshuttle/blob/083293ea0dc2ebc77f282c2803720a2bb5f21a80/sshuttle/client.py#L418
'''

import subprocess, tempfile
from subprocess import Popen, PIPE, STDOUT

'''
FIXME
Find better way to load code to remote. Check sshuttle:
https://github.com/apenwarr/sshuttle/blob/083293ea0dc2ebc77f282c2803720a2bb5f21a80/sshuttle/ssh.py#L91
'''

# Following are code to be pushed to remote(kosh)
CODE_PANIIKKI_UPTIME='''
#!/usr/bin/python3
from concurrent.futures import ThreadPoolExecutor
import subprocess


paniikki = [
    "befunge","bit","bogo","brainfuck","deadfish","emo","entropy","false","fractran","fugue","glass","haifu","headache","intercal","malbolge","numberwang","ook","piet","regexpl","remorse","rename","shakespeare","smith","smurf","spaghetti","thue","unlambda","wake","whenever","whitespace","zombie"
]

def get_luokka(nimi):
    try:
        return nimi, subprocess.check_output(["ssh", nimi, "uptime"], timeout=1, stderr=subprocess.STDOUT).decode("utf-8").rstrip("\\n")
    except subprocess.TimeoutExpired:
        return nimi, "computer doesn't answer"
    except subprocess.CalledProcessError as e:
        return nimi, "error: %s" % e.output.decode("utf-8").rstrip("\\n")

executor = ThreadPoolExecutor(max_workers=8)

luokka = paniikki

for nimi, tulos in executor.map(get_luokka, luokka):
    print("%s: %s" % (nimi, tulos))
'''

CODE_GET_PORT = '''
#!/usr/bin/python3
    
def is_open(ip,port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def get_available_socket(ip,port=12520):
    while is_open(ip,port):
        port += 1
    return port

print(get_available_socket("{user}@{node}.org.aalto.fi"))
'''



class Node:
    '''
    A Paniikki machine
    Example uptime_output:
        befunge:  10:35:49 up 9 days,  8:44,  0 users,  load average: 0.02, 0.01, 0.00
    '''

    def __init__(self, uptime_output):
        self.init_properties(uptime_output)

    def init_properties(self, output):
        # print(output)
        self.hostname = output.split(':')[0]
        self.uptime = ' '.join(output.split(' up ')[1].split(" user")[0].split(', ')[:-1])
        self.num_users = int(output.split(' user')[0].split()[-1])
        self.loads = output.split('average:')[-1]

    def __repr__(self):
        return repr(
            "{:<13}=> up {:<14} with{:>2} users.  LOAD:{:>15}".format(
                self.hostname, self.uptime, self.num_users, self.loads)
        )


class ComputerLab:
    '''
    Paniikki computer lab.
    Sort the nodes by its number of users and load average.
    '''
    def __init__(self, uptime_outputs):
        self.nodes = [Node(u) for u in uptime_outputs]
        self.sort()

    def sort(self):
        # Sort by number of users
        self.nodes.sort(key=lambda n: (
            n.num_users,
            float(n.loads.split(',')[0]),
            float(n.loads.split(',')[1]),
            float(n.loads.split(',')[2])
        ))

    def __print__(self):
        title = "Paniikki Nodes Status"
        print('\n')
        print("=" * len(title))
        print(title)
        print("=" * len(title))
        for n in self.nodes:
            print(n)



class ComputerLabRemoteController:
    '''
    The brain. Does SSH and remote code loading.
    '''
    def __init__(self, username):
        self.username = username
        self.uptimes = None
        self.node = None
        self.port = None

    def run_code_on_remote(self, code_as_str, remote="kosh"):
        p = Popen(['ssh', 'kosh', 'python3'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        grep_stdout = p.communicate(input=code_as_str.encode())[0]
        return grep_stdout.decode().rstrip("\n")

    def check_modules(self):
        code = ''' '''

    def check_lab_uptimes(self):
        self.uptimes = self.run_code_on_remote(CODE_PANIIKKI_UPTIME).split('\n')

        def contains_bad_output(output):
            bad_ouput_samples = [
                "Permission denied",
                "computer doesn't answer"
            ]
            for b in bad_ouput_samples:
                if b in output:
                    return True
                # print(b)
            else:
                return False

        self.uptimes = [u for u in self.uptimes if not contains_bad_output(u)]

        self.lab = ComputerLab(self.uptimes)
        self.lab.__print__()

    def print_command(self):
        command = '''ssh {user}@{node} -t -L {port}:localhost:{port} -o ProxyCommand='ssh {user}@kosh -W %h:%p'  "bash -l -c \'module load courses/CS-E4820-advanced-probabilistic-methods; jupyter notebook --port={port} --no-browser\'"'''.format(
            user=self.username, node=self.node.hostname, port=self.port)
        print("\n")
        print("Copy/paste this line into your shell in order to start a Jupyter Notebook:\n>>>\n")
        print(command)
        print("\n")

    def check_port_sanity(self, port):
        assert port.isdigit()
        assert int(port) > 1024
        assert int(port) < 64000

        self.port = port

    def get_port(self):
        node = self.lab.nodes[0]

        port = self.run_code_on_remote(
            CODE_GET_PORT.format(
                user=self.username,
                node=node
            )
        )

        self.check_port_sanity(port)

        # This is called from this function because of synchronousity
        self.print_command()

    def run(self):
        self.uptimes = self.check_lab_uptimes()
        self.node = self.lab.nodes[0]
        self.get_port()


def main():
    logo = r'''
   _         _ _            ___  __        _____  _____ 
  /_\   __ _| | |_ ___     / __\/ _\       \_   \/__   \
 //_\\ / _` | | __/ _ \   / /   \ \ _____   / /\/  / /\/
/  _  \ (_| | | || (_) | / /___ _\ \_____/\/ /_   / /   
\_/ \_/\__,_|_|\__\___/  \____/ \__/     \____/   \/
'''
    print(logo)

    username = input(
        "Hi! Welcome to Aalto CS-IT's Paniikki computer lab Jupyter Notebook controller. Do you want to launch one? Type in your Aalto username :D\n    e.g. tillip1\n>>> ")
    print("Thanks! Hold on a sec. This will take a few secs.")
    c = ComputerLabRemoteController(username)
    c.run()


if __name__ == "__main__":
    main()

