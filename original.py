from re import findall
from sys import argv

print("Reading original...")
original = set()
for line in open(argv[1], "r", encoding = "utf-8"):
  split = findall("[^\t\n]+", line)
  if split[1] == "0":
    original.add(split[0])

print("Writing original...")
file = open(argv[3], "w", encoding = "utf-8")
for line in open(argv[2], "r", encoding = "utf-8"):
  split = findall("[^\t\n]+", line)
  if split[0] in original:
    print(line, end = "", file = file)

print("Done!")
