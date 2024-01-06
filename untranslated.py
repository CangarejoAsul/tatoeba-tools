# argv[1]: language code
# argv[2]: links file
# argv[3]: sentences file
# argv[4]: sentences file

from re import findall
from sys import argv

print("Reading languages...")
language = {}
for line in open(argv[3], "r", encoding="utf-8"):
  split = findall("[^\t\n]+", line)
  language[split[0]] = split[1]

print("Reading links...")
translated = set()
for line in open(argv[2], "r", encoding="utf-8"):
  split = findall("[^\t\n]+", line)
  if split[1] in language and language[split[1]] == argv[1]:
    translated.add(split[0])

print("Writing sentences...")
file = open(argv[4], "w", encoding="utf-8")
for line in open(argv[3], "r", encoding="utf-8"):
  split = findall("[^\t\n]+", line)
  if split[0] not in translated:
    print(line, end = "", file = file)

print("Done!")
