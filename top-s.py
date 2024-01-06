from sys import argv
from re import findall

print("Reading queries...")
queries = {}
for line in open(argv[5], encoding = "utf-8", errors = "backslashreplace"):
  split = findall(r"[^\,\n]+", line)
  if len(split) >= 3 and split[1] == argv[1]:
    for word in findall(r"\w+", split[2].lower()):
      if len(word) <= 20:
        if word not in queries:
          queries[word] = 0
        queries[word] += 1

print("Reading languages...")
source = set()
target = set()
for line in open(argv[3], encoding = "utf-8", errors = "backslashreplace"):
  split = findall(r"[^\t\n]+", line)
  if split[1] == argv[1]:
    source.add(int(split[0]))
  if split[1] == argv[2]:
    target.add(int(split[0]))

print("Reading links...")
links = set()
for line in open(argv[4], encoding = "utf-8", errors = "backslashreplace"):
  split = findall(r"[^\t\n]+", line)
  if int(split[0]) in source and int(split[1]) in target:
    links.add(int(split[0]))

print("Reading sentences...")
translations = {}
for word in queries:
  translations[word] = 0
for line in open(argv[3], encoding = "utf-8", errors = "backslashreplace"):
  split = findall(r"[^\t\n]+", line)
  if int(split[0]) in links:
    words = set()
    for word in findall(r"\w+", split[2].lower()):
      if word in translations:
        words.add(word)
    for word in words:
      translations[word] += 1

print("Sorting queries...")
words = []
for word in queries:
  words.append((word, queries[word], translations[word]))
words.sort(key = lambda word: word[2], reverse = True)
words.sort(key = lambda word: word[1], reverse = True)

print("Writing queries...")
output = open(argv[6], "w", encoding = "utf-8")
for word in words:
  print(word[0], word[1], word[2], sep = "\t", file = output)

print("Done!")
