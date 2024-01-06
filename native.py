from re import findall
from sys import argv

print("Reading languages...")
languages = {}
for line in open(argv[1], "r", encoding = "utf-8"):
  split = findall("[^\t\n]+", line)
  if len(split) >= 3 and split[1] == "5":
    if split[2] not in languages:
      languages[split[2]] = set()
    languages[split[2]].add(split[0])

print("Writing sentences...")
file = open(argv[3], "w", encoding = "utf-8")
for line in open(argv[2], "r", encoding = "utf-8"):
  split = findall("[^\t\n]+", line)
  if split[3] in languages and split[1] in languages[split[3]]:
    print(line, end = "", file = file)

print("Done!")
