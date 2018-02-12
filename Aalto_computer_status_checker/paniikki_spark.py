#/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor
import subprocess

paniikki = [
    "befunge","bit","bogo","brainfuck","deadfish","emo","entropy","false","fractran","fugue","glass","haifu","headache","intercal","malbolge","numberwang","ook","piet","regexpl","remorse","rename","shakespeare","smith","smurf","spaghetti","thue","unlambda","wake","whenever","whitespace","zombie"
]

def get_luokka(nimi, i):
    try:
        return nimi, subprocess.check_output(["ssh", nimi, ""], timeout=1, stderr=subprocess.STDOUT).decode("utf-8").rstrip("\n")

    except subprocess.TimeoutExpired:
        return nimi, "computer doesn't answer"
    except subprocess.CalledProcessError as e:
        return nimi, "error: %s" % e.output.decode("utf-8").rstrip("\n")

executor = ThreadPoolExecutor(max_workers=8)

for nimi, tulos in executor.map(get_luokka, paniikki, range(len(paniikki))):
    print("%s: %s" % (nimi, tulos))
