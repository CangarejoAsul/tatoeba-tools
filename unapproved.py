from os import makedirs
from os.path import isdir
from re import findall

print("Reading reviews...")
unapproved = set()
for line in open("users_sentences.csv", "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[2] == "-1":
    unapproved.add(split[1])

print("Writing unapproved...")
file = {}
for line in open("sentences_detailed.csv", "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[0] in unapproved and split[1] != "\\N":
    if not isdir("unapproved"): 
      makedirs("unapproved")
    if split[1] not in file:
      file[split[1]] = open("unapproved/unapproved-" + split[1] + ".txt", "w", encoding = "utf-8")
    print(line, end = "", file = file[split[1]])
