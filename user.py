from re import findall
from sys import argv

users = set()
for i in range(1, len(argv) - 2):
  users.add(argv[i])

print("Writing sentences...")
file = open(argv[- 1], "w", encoding = "utf-8")
for line in open(argv[- 2], "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[3] in users:
    print(line, end = "", file = file)

print("Done!")
