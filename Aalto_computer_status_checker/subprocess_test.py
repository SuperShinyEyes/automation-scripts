import os
import subprocess

env = {'SSH_ASKPASS':os.path.realpath(__file__), 'DISPLAY':':9999'}

p = subprocess.Popen(['ssh', '-T', '-v', 'parks1@kosh.org.aalto.fi'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env=env,
    preexec_fn=os.setsid
)

print(p.stdout)