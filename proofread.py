from random import shuffle
from re import findall

users = (
  "Cabo",
  "carlosalberto",
  "DJ_Saidez",
  "maaster",
  "Nuel",
)

sentences = {}
for user in users:
  sentences[user] = []
for line in open("sentences_detailed.csv", "r", encoding = "utf-8"):
  fields = findall(r"[^\t\n]+", line)
  if fields[1] == "eng" and fields[3] in users:
    sentences[fields[3]].append(line)
for user in users:
  shuffle(sentences[user])

for user in users:
  reading = open("proofreading-" + user + ".txt", "w", encoding = "utf-8")
  for sentence in sentences[user]:
    print(sentence, end = "", file = reading)
