#/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor
import subprocess

maari_a_luokat = [
    "albatrossi", "broileri", "dodo", "drontti", "emu", "fasaani",
     "flamingo", "iibis", "kakadu", "kalkkuna", "karakara", "kasuaari",
     "kiuru", "kiwi", "kolibri", "kondori", "kookaburra", "koskelo",
     "kuukkeli", "lunni", "moa", "pelikaani", "pitohui", "pulu",
     "ruokki", "siira", "strutsi", "suula", "tavi", "tukaani", "undulaatti" 
]

maari_c_luokat = [
    "akaatti", "akvamariini", "ametisti", "baryytti", "berylli", "fluoriitti", "granaatti",
    "hypersteeni", "jade", "jaspis", "karneoli", "korundi", "kuukivi", "malakiitti", "meripihka",
    "opaali", "peridootti", "rubiini", "safiiri", "sitriini", "smaragdi", "spektroliitti",
    "spinelli", "timantti", "topaasi", "turkoosi", "turmaliini", "vuorikide", "zirkoni" 
]

def get_luokka(nimi):
    try:
        return nimi, subprocess.check_output(["ssh", nimi, "uptime"], timeout=1, stderr=subprocess.STDOUT).decode("utf-8").rstrip("\n")
        #return nimi, subprocess.check_output(["ssh", nimi, "perf", "--version"], timeout=2, stderr=subprocess.STDOUT).decode("utf-8").rstrip("\n")
    except subprocess.TimeoutExpired:
        return nimi, "computer doesn't answer"
    except subprocess.CalledProcessError as e:
        return nimi, "error: %s" % e.output.decode("utf-8").rstrip("\n")

luokat = maari_a_luokat+maari_c_luokat
executor = ThreadPoolExecutor(max_workers=8)

for nimi, tulos in executor.map(get_luokka, luokat):
    print("%s: %s" % (nimi, tulos))