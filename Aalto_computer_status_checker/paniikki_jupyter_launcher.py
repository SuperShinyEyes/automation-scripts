#/usr/bin/python3

import subprocess

CODE_PANIIKKI_UPTIME='''
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

for nimi, tulos in executor.map(get_luokka, paniikki):
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
    'befunge:  10:35:49 up 9 days,  8:44,  0 users,  load average: 0.02, 0.01, 0.00'
    '''

    def __init__(self, uptime_output):
        self.init_properties(uptime_output)

    #         self.hostname = hostname
    #         self.uptime = uptime
    #         self.num_users = num_users

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
    def __init__(self, uptime_outputs):
        self.nodes = [Node(u) for u in uptime_outputs]
        self.sort()

    def sort(self):
        # Sort by number of users
        self.nodes.sort(key=lambda n: n.num_users)
        # Now sort by loads
        nodes_by_num_user_dict = {}
        for n in self.nodes:
            nodes_by_num_user_dict.setdefault(n.num_users, [])
            nodes_by_num_user_dict[n.num_users].append(n)
        for k, v in nodes_by_num_user_dict.items():
            v.sort(
                key=lambda node:
                float(
                    node.loads.split(',')[0]
                )
            )
        # Flatten
        # https://stackoverflow.com/a/952952/3067013
        self.nodes = [
            n for nodes in nodes_by_num_user_dict.values()
            for n in nodes
        ]

    def __print__(self):
        title = "Paniikki Nodes Status"
        print('\n')
        print("=" * len(title))
        print(title)
        print("=" * len(title))
        for n in self.nodes:
            print(n)



class ComputerLabRemoteController:
    def __init__(self, username):
        self.username = username
        self.uptimes = None
        self.node = None
        self.port = None

    def check_lab_uptimes(self):
        with open('temp.py', 'w') as f:
            f.write(CODE_PANIIKKI_UPTIME)

        self.uptimes = subprocess.check_output(
            ["ssh kosh python3 < ./temp.py"],
            timeout=10,
            shell=True,  # FIXME: Remove this for security
            stderr=subprocess.STDOUT
        ).decode("utf-8").rstrip("\n").split('\n')

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

        subprocess.check_output(
            ["rm temp.py"],
            timeout=10,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode("utf-8").rstrip("\n")

        self.lab = ComputerLab(self.uptimes)
        self.lab.__print__()

    def print_command(self):
        command = '''ssh {user}@{node} -t -L {port}:localhost:{port} -o ProxyCommand='ssh {user}@kosh -W %h:%p'  "bash -l -c \'module load courses/CS-E4820 ; jupyter notebook --port={port} --no-browser\'"'''.format(
            user=self.username, node=self.node.hostname, port=self.port)
        print("\n")
        print("Copy/paste this line into your shell in order to start a Jupyter Notebook:\n>>>\n")
        print(command)
        print("\n")

    def get_port(self):
        node = self.lab.nodes[0]
        with open('temp.py', 'w') as f:
            f.write(CODE_GET_PORT.format(user=self.username, node='bit'))

        self.port = subprocess.check_output(
            ["ssh kosh python3 < ./temp.py"],
            timeout=10,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode("utf-8").rstrip("\n")

        subprocess.check_output(
            ["rm temp.py"],
            timeout=10,
            shell=True,
            stderr=subprocess.STDOUT
        ).decode("utf-8").rstrip("\n")

        # This is called from this function because of synchronousity
        self.print_command()

    def run(self):
        self.uptimes = self.check_lab_uptimes()
        self.node = self.lab.nodes[0]
        self.port = self.get_port()


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