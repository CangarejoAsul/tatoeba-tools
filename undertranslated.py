from random import randint, shuffle
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
  text = sub(r"[\u00AD\u200B-\u200E\uFEFF]", "", text)
  text = sub(r"[\u2010-\u2013\u2212]", "-", text)
  text = sub(r"[\u2018\u2019\u2032]", "'", text)
  text = sub(r"\.{2,}", "…", text)
  text = sub(r"-{2,}", "—", text)
  return text

def getwords(text):
  return findall(
    r"""[^\s—―…'‘"“<«\[{][^\s—―…]+[)][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|"""
    r"""[^\s—―…'‘"“<«(\[{][^\s—―…]*[(][^\s—―…]+[^\s—―…'’"”>»\]},:;.?!‽]|"""
    r"""(?:[^\s—―…'‘"“<«(\[{][^\s—―…]*)?(?:[^\W\d]\.){2,}(?![^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽])|"""
    r"""[^\s—―…'‘"“<«(\[{][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|"""
    r"""[^\s—―…'‘’"“”<>«»()\[\]{},:;.?!‽]""",
    cleanupforsplitting(text))
  return findall(r"""[^\s—―…'‘"“<«(\[{][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|[^\s—―…'‘’"“”<>«»()\[\]{},:;.?!‽]""", cleanupforsplitting(text))
  return findall(r"(?:[\w#@-][\w#@'()/,:.-]*)?[\w#@-]", cleanupforsplitting(text))

read = open("translations-" + source + "-" + target + ".txt", "r", encoding = "utf-8")
translations = {}
for line in read:
  fields = findall(r"[^\t\n]+", line)
  translations[fields[0]] = int(fields[2])
read.close()

file = open("text.txt", "r", encoding = "utf-8")
text = sub(r"\s+", " ", file.read())
file.close()

words = set()
frequency = {}
sample = {}
for sentence in findall(r".+?(?<!\bMr)[.?!]\W* (?=\W*[A-Z])", text):
  for word in getwords(sentence.lower()):
    if word not in translations or translations[word] < threshold:
      words.add(word)
      if word not in frequency:
        frequency[word] = 0
      frequency[word] += 1
      if randint(1, frequency[word]) == 1:
        sample[word] = sentence
words = list(words)
shuffle(words)

write = open("words.txt", "w", encoding = "utf-8")
for word in words:
  print(word, frequency[word], sample[word], sep = "\t", file = write)
write.close()
