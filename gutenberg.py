from random import randint, shuffle
from os import scandir
from re import findall, I, search, sub

def cleanupforsplitting(text):
  text = sub(r"[\u00AD\u200B-\u200E\uFEFF]", "", text)
  text = sub(r"[\u2010-\u2013\u2212]", "-", text)
  text = sub(r"[\u2018\u2019\u2032]", "'", text)
  text = sub(r"\.{2,}", "…", text)
  text = sub(r"-{2,}", "—", text)
  text = text.replace("A\u0300", "À")
  text = text.replace("A\u0301", "Á")
  text = text.replace("A\u0302", "Â")
  text = text.replace("A\u0303", "Ã")
  text = text.replace("C\u0327", "Ç")
  text = text.replace("E\u0301", "É")
  text = text.replace("E\u0302", "Ê")
  text = text.replace("I\u0301", "Í")
  text = text.replace("O\u0301", "Ó")
  text = text.replace("O\u0302", "Ô")
  text = text.replace("O\u0303", "Õ")
  text = text.replace("U\u0301", "Ú")
  text = text.replace("a\u0300", "à")
  text = text.replace("a\u0301", "á")
  text = text.replace("a\u0302", "â")
  text = text.replace("a\u0303", "ã")
  text = text.replace("c\u0327", "ç")
  text = text.replace("e\u0301", "é")
  text = text.replace("e\u0302", "ê")
  text = text.replace("i\u0301", "í")
  text = text.replace("o\u0301", "ó")
  text = text.replace("o\u0302", "ô")
  text = text.replace("o\u0303", "õ")
  text = text.replace("u\u0301", "ú")
  text = text.replace("\ufb01", "fi")
  text = text.replace("\ufb02", "fl")
  return text

def getwords(text):
  return findall(
    r"""[^\s—―…'‘"“<«(\[{¿¡][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|"""
    r"""[^\s—―…'‘’"“”<>«»()\[\]{},:;.¿?¡!‽]""",
    cleanupforsplitting(text))

def isvalidword(word):
  return not search(r"[^a-z'-]", word, flags = I)

def countwords():
  words = set()
  frequency = {}
  i = 0
  for file in scandir("gutenberg"):
    text = open(file.path, "r", encoding = "utf-8")
    try:
      string = text.read().lower()
    except:
      text.close()
      continue
    if len(sub(r"[^a-z]", "", string, flags = I)) / len(string) >= .5:
      for word in getwords(string):
        if isvalidword(word):
          words.add(word)
          if word not in frequency:
            frequency[word] = 0
          frequency[word] += 1
      # i += 1
      # if i >= 20 * 1000:
      #   print("?")
      #   break
    text.close()
  words = list(words)
  shuffle(words)
  words.sort(key = lambda word: frequency[word], reverse = True)

  translated = set()
  file = open("translations-eng-por.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if fields[2] != "0":
      translated.add(fields[0])
  file.close()

  file = open("frequency.txt", "w", encoding = "utf-8")
  for word in words:
    print(word, "+" if word in translated else "−", frequency[word], sep = "\t", file = file)
  file.close()

def findsentences():
  dictionary = set()
  file = open("eng.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    dictionary.add(fields[0].lower())
  file.close()

  translated = set()
  file = open("translations-eng-por.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if fields[2] != "0":
      translated.add(fields[0])
  file.close()

  frequency = {}
  untranslated = set()
  terms = []
  file = open("frequency.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if isvalidword(fields[0]) and fields[0] in dictionary and int(fields[2]) >= 100:
      frequency[fields[0]] = int(fields[2])
      if len(untranslated) < 1000 and fields[0] not in translated:
        untranslated.add(fields[0])
        terms.append(fields[0])
  file.close()

  sentences = {}
  for word in untranslated:
    sentences[word] = []
  for file in scandir("gutenberg"):
    text = open(file.path, "r", encoding = "utf-8")
    try:
      string = sub(r"\s+", " ", text.read())
    except:
      text.close()
      continue
    if len(sub(r"[^a-z]", "", string, flags = I)) / len(string) >= .5:
      for sentence in findall(r""".+?(?<!\bDr)(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bSt)(?<!\b[A-Z])[.?!]+\W* (?=\W*[A-Z0-9])""", string):
        if len(sentence) >= 100:
          for word in getwords(sentence.lower()):
            if word in untranslated:
              sentences[word].append((word, file.name, min(frequency[term] if term in frequency else 0 for term in getwords(sentence.lower()) if term != word), sentence))
              if len(sentences[word]) >= 500:
                shuffle(sentences[word])
                sentences[word].sort(key = lambda tuple: tuple[2], reverse = True)
                sentences[word] = sentences[word][: 20]
    text.close()

  file = open("sentences.txt", "w", encoding = "utf-8")
  for word in terms:
    shuffle(sentences[word])
    sentences[word].sort(key = lambda tuple: tuple[2], reverse = True)
    for sentence in sentences[word][: 20]:
      print(*sentence, sep = "\t", file = file)
  file.close()

def findsentences2():
  dictionary = set()
  fragments = set()
  file = open("eng.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    dictionary.add(fields[0].lower())
    fragments.update(findall(r"\w+", fields[0].lower()))
  file.close()

  translated = set()
  file = open("translations-eng-por.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if fields[2] != "0":
      translated.add(fields[0])
  file.close()

  untranslated = set()
  file = open("frequency.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if len(untranslated) < 1000 and isvalidword(fields[0]) and fields[0] in dictionary and fields[0] not in translated and int(fields[2]) >= 100:
      untranslated.add(fields[0])
  file.close()

  i = 0
  frequency = {}
  sentences = {}
  for file in scandir("gutenberg"):
    text = open(file.path, "r", encoding = "utf-8")
    try:
      string = sub(r"\s+", " ", text.read())
    except:
      text.close()
      continue
    if len(sub(r"[^a-z]", "", string, flags = I)) / len(string) >= .5:
      for sentence in findall(r""".+?(?<!\bDr)(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bSt)[.?!]+""", string, flags = I):
        if len(sentence) >= 100 and len(sentence) < 200 and all(fragment in fragments for fragment in findall(r"\w+", sentence.lower())):
          for word in getwords(sentence.lower()):
            if word in untranslated:
              if word not in frequency:
                frequency[word] = 0
              frequency[word] += 1
              if word not in sentences:
                sentences[word] = [("", "", "") for _ in range(20)]
              for i in range(20):
                if randint(1, frequency[word]) == 1:
                  sentences[word][i] = (word, file.name, sentence)
    text.close()

  file = open("sentences2.txt", "w", encoding = "utf-8")
  words = list(sentences.keys())
  shuffle(words)
  for word in words:
    if word in sentences:
      shuffle(sentences[word])
      for sentence in sentences[word]:
        print(*sentence, sep = "\t", file = file)
  file.close()

def findsentences3():
  dictionary = set()
  fragments = set()
  file = open("eng.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    dictionary.add(fields[0].lower())
    fragments.update(findall(r"\w+", fields[0].lower()))
  file.close()

  translated = set()
  file = open("translations-eng-por.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if fields[2] != "0":
      translated.add(fields[0])
  file.close()

  untranslated = set()
  file = open("frequency.txt", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if isvalidword(fields[0]) and fields[0] in dictionary and fields[0] not in translated and int(fields[2]) >= 100:
      untranslated.add(fields[0])
  file.close()

  i = 0
  frequency = {}
  sentences = {}
  for file in scandir("gutenberg"):
    text = open(file.path, "r", encoding = "utf-8")
    try:
      string = sub(r"\s+", " ", text.read())
    except:
      text.close()
      continue
    if len(sub(r"[^a-z]", "", string, flags = I)) / len(string) >= .5:
      for sentence in findall(r""".+?(?<!\bDr)(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bSt)[.?!]+""", string, flags = I):
        if len(sentence) >= 100 and len(sentence) < 200:
          for word in getwords(sentence.lower()):
            if word in untranslated:
              if word not in frequency:
                frequency[word] = 0
              frequency[word] += 1
              if randint(1, frequency[word]) == 1:
                sentences[word] = (word, file.name, sentence)
    text.close()

  file = open("sentences3.txt", "w", encoding = "utf-8")
  words = list(sentences)
  shuffle(words)
  for word in words:
    print(*sentences[word], sep = "\t", file = file)
  file.close()

countwords()
findsentences()
# findsentences2()
# findsentences3()
