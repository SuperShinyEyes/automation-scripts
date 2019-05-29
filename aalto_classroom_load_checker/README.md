# Aalto classroom computer load checker
Check system load in Paniikki and Maari from Kosh proxy server.

## How to use
```bash
# On your laptop
ssh username@kosh.aalto.fi

# Create your Kerberos ticket
kinit

# Fom Kosh
python3 check_paniikki_uptime.py

#   befunge:  17:05:34 up 91 days,  5:30,  1 user,  load average: 0.00, 0.00, 0.00
#   bit: computer doesn't answer
#   bogo:  17:05:34 up 35 days, 56 min,  2 users,  load average: 0.00, 0.00, 0.00
#   brainfuck:  17:05:34 up 45 days,  3:32,  4 users,  load average: 0.23, 0.23, 0.19
#   deadfish:  17:05:34 up 52 days,  3:49,  3 users,  load average: 0.00, 0.01, 0.00
#   emo:  17:05:34 up 34 days,  7:09,  0 users,  load average: 0.00, 0.00, 0.00
#   entropy:  17:05:34 up 16 days,  8:

ssh befunge

# Now you are in a Paniikki machine.
```
