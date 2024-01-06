from re import findall
from sys import argv

languages = set()
for i in range(1, len(argv) - 2):
  languages.add(argv[i])

print("Writing sentences...")
file = open(argv[- 1], "w", encoding = "utf-8")
for line in open(argv[- 2], "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[1] in languages:
    print(line, end = "", file = file)

print("Done!")
