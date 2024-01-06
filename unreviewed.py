from re import findall
from sys import argv

print("Reading reviews...")
reviewed = set()
for line in open(argv[1], "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  reviewed.add(split[1])

print("Filtering unreviewed...")
file = open(argv[3], "w", encoding = "utf-8")
for line in open(argv[2], "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[0] not in reviewed:
    print(line, end = "", file = file)

print("Done!")
