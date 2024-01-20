from random import shuffle
from re import findall, sub

source = "eng"
target = "por"
threshold = 1

def cleanupforsorting(word):
  word = word.lower()
  word = sub(r"\W", "", word)
  word = sub(r"[àáâãä]", "a", word)
  word = sub(r"[ç]", "c", word)
  word = sub(r"[èéêẽë]", "e", word)
  word = sub(r"[ìíîĩï]", "i", word)
  word = sub(r"[òóôõö]", "o", word)
  word = sub(r"[ùúûũü]", "u", word)
  return word

def cleanupforsplitting(text):
  text = sub(r"[\u00AD\u200B-\u200D\uFEFF]", "", text)
  text = sub(r"[\u2010-\u2013\u2212]", "-", text)
  text = sub(r"[\u2018\u2019]", "'", text)
  text = sub(r"\.{2,}", "…", text)
  text = sub(r"-{2,}", "—", text)
  return text

def getwords(text):
  return findall(
    r"""[(][^\s—―…]+[)][^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-]|"""
    r"""[\[][^\s—―…]+[\]][^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-]|"""
    r"""["][^\s—―…]+["][^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-]|"""
    r"""[*][^\s—―…]+[*][^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-]|"""
    r"""[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*[(][^\s—―…]+[)]|"""
    r"""[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*[\[][^\s—―…]+[\]]|"""
    r"""[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*["][^\s—―…]+["]|"""
    r"""(?<![\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-])[/][^\s—―…]+[/](?![\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-])|"""
    r"""(?<![/])[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*[.][^\s—―…]*[/](?![\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-])|"""
    r"""(?:[^\W\d]\.){2,}(?:[^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-])?|"""
    r"""(?:[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*)?(?:[^\W\d]\.){2,}|"""
    r"""[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-][^\s—―…]*[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹-]|"""
    r"""[\w#$%&@¢£¤¥§©®°¶‰€™₣₤₩₪₫₰₳₴₵₹]"""
  , cleanupforsplitting(text))

read = open("translations-" + source + "-" + target + ".txt", "r", encoding = "utf-8")
translations = {}
data = {}
for line in read:
  fields = findall(r"[^\t\n]+", line)
  translations[fields[0]] = int(fields[2])
  if fields[0] not in data:
    data[fields[0]] = [int(fields[1]), int(fields[2]), fields[3], fields[4], fields[5]]
  else:
    data[fields[0]][0] += int(fields[1])
    data[fields[0]][1] += int(fields[2])
read.close()

read = open("text.txt", "r", encoding = "utf-8")
words = set()
for line in read:
  for word in getwords(line.lower()):
    if word not in translations or translations[word] < threshold:
      words.add(word)
read.close()
words = list(words)
shuffle(words)

write = open("words.txt", "w", encoding = "utf-8")
for word in words:
  print(word, file = write)
write.close()

write = open("translations-" + source + "-" + target + "-clean.txt", "w", encoding = "utf-8")
for word in data:
  print(word, str(data[word][0]), str(data[word][1]), data[word][2], data[word][3], data[word][4], file = write)
write.close()
