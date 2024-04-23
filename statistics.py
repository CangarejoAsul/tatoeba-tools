# aspell -d en dump master | aspell -l en expand > eng.txt

from janome.tokenizer import Tokenizer
from jieba import cut
from konlpy.tag import Kkma
from os import makedirs
from os.path import isdir
from random import randint, shuffle
from re import findall, I, search, sub
from regex import findall as find
from unicodedata import normalize

minimum = 0
minimumasian = 0

def cleanupforhashing(text):
  text = normalize("NFKC", text)
  # text = sub(r"""\s+""", "", text)
  # text = sub(r"""[\u2010-\u2015\u2212]+""", "-", text)
  # text = sub(r"""[<>‹›«»'"\u2018-\u201F]+""", "'", text)
  text = cleanupforsorting(text)
  return text

def cleanupforsorting(word):
  word = word.lower()
  word = sub(r"[\Wˈˌǃ]", "", word)
  word = sub(r"[àáâãäāåă]", "a", word)
  word = sub(r"[æ]", "ae", word)
  word = sub(r"[çćĉčℂ]", "c", word)
  word = sub(r"[đḍď]", "d", word)
  word = sub(r"[èéêẽëēěė]", "e", word)
  word = sub(r"[ﬁ]", "fi", word)
  word = sub(r"[ﬂ]", "fl", word)
  word = sub(r"[ĝ]", "g", word)
  word = sub(r"[ḥĥ]", "h", word)
  word = sub(r"[ìíîĩïī]", "i", word)
  word = sub(r"[ĵ]", "j", word)
  word = sub(r"[łľĺ]", "l", word)
  word = sub(r"[ñńň]", "n", word)
  word = sub(r"[òóôõöōø]", "o", word)
  word = sub(r"[œ]", "oe", word)
  word = sub(r"[ℚ]", "q", word)
  word = sub(r"[řṛŕℝ]", "r", word)
  word = sub(r"[ŝšşșṣ]", "s", word)
  word = sub(r"[ß]", "ss", word)
  word = sub(r"[ţṭť]", "t", word)
  word = sub(r"[ùúûũüūŭ]", "u", word)
  word = sub(r"[𝑥]", "x", word)
  word = sub(r"[ý]", "y", word)
  word = sub(r"[žż]", "z", word)
  return word

def cleanupforsplitting(text):
  text = sub(r"[\u00AD\u200B-\u200E\uFEFF]", "", text)
  text = sub(r"[\u2010-\u2013\u2212]", "-", text)
  text = sub(r"[\u2018\u2019\u2032]", "'", text)
  text = sub(r"\.{2,}", "…", text)
  text = sub(r"-{2,}", "—", text)
  return text

def loadlanguageset():
  print("Loading language set...")
  read = open("temporary/languages.txt", "r", encoding = "utf-8")
  languages = []
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    languages.append(fields[0])
  read.close()
  return languages

def loadlanguagemap():
  print("Loading language map...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  language = {}
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    language[fields[0]] = fields[1]
  read.close()
  return language

def getwords(text):
  return findall(r"""(?:[\w#@-][\w#@'()/,:.-]*)?[\w#@-]""", cleanupforsplitting(text))

def getwordsinenglish(text):
  return findall(
    r"""[^\s—―…'‘"“<«\[{¿¡][^\s—―…]+[)][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|"""
    r"""[^\s—―…'‘"“<«(\[{¿¡][^\s—―…]*[(][^\s—―…]+[^\s—―…'’"”>»\]},:;.?!‽]|"""
    r"""(?:[^\s—―…'‘"“<«(\[{¿¡][^\s—―…]*)?(?:[^\W\d]\.){2,}(?![^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽])|"""
    r"""[^\s—―…'‘"“<«(\[{¿¡][^\s—―…]*[^\s—―…'’"”>»)\]},:;.?!‽]|"""
    r"""[^\s—―…'‘’"“”<>«»()\[\]{},:;.¿?¡!‽]""",
    cleanupforsplitting(text))

def getwordsinlanguage(janome, kkma, language, text):
  words = set()
  if language in ("cmn", "lzh", "wuu", "yue"):
    for token in cut(text):
      words.update(getwords(token))
  elif language in ("eng", "fra", "ita", "por", "spa"):
    words.update(getwordsinenglish(text))
  elif language == "jpn":
    for token in janome.tokenize(text):
      words.update(getwords(token))
  elif language == "kor":
    for token in kkma.morphs(text):
      words.update(getwords(token))
  else:
    words.update(getwords(text))
  return words

def loadspellchecker(language):
  try:
    file = open("dictionaries/" + language + ".txt", "r", encoding = "utf-8")
  except:
    return lambda word: True
  else:
    print("Loading spellchecker (" + language + ")...")
    dictionary = set()
    for line in file:
      dictionary.update(findall(r"\w+", line.lower()))
    file.close()
    return lambda word: all(fragment in dictionary for fragment in findall(r"\w+", word.lower()))

def writelanguageset():
  print("Reading language set...")
  frequency = {}
  sample = {}
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] not in frequency:
      frequency[fields[1]] = 0
      sample[fields[1]] = line
    if len(fields[2]) >= minimum or fields[1] in ("cmn", "jpn", "kor", "lzh", "wuu", "yue") and len(fields[2]) >= minimumasian:
      frequency[fields[1]] += 1
      if randint(1, frequency[fields[1]]) == 1:
        sample[fields[1]] = line
  read.close()
  
  print("Writing language set...")
  languages = list(frequency.keys())
  shuffle(languages)
  languages.sort(key = lambda language: frequency[language], reverse = True)
  if not isdir("temporary"): 
    makedirs("temporary")
  write = open("temporary/languages.txt", "w", encoding = "utf-8")
  for language in languages:
    print(language, frequency[language], sample[language], sep = "\t", end = "", file = write)
  write.close()

def partitionsentences():
  print("Partitioning sentences...")
  if not isdir("temporary/sentences"): 
    makedirs("temporary/sentences")
  write = {}
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] != "\\N":
      if fields[1] not in write:
        write[fields[1]] = open("temporary/sentences/" + fields[1] + ".txt", "w", encoding = "utf-8")
      print(line, end = "", file = write[fields[1]])
  read.close()
  for idiom in write:
    write[idiom].close()

def partitionlinks():
  print("Partitioning links...")

  languages = loadlanguageset()
  languageof = loadlanguagemap()

  print("Writing links...")
  read = open("links.csv", "r", encoding = "utf-8")
  if not isdir("temporary/links"): 
    makedirs("temporary/links")
  write = {}
  for language in languages:
    if language != "\\N":
      write[language] = open("temporary/links/" + language + ".txt", "w", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[0] in languageof and languageof[fields[0]] != "\\N":
      print(fields[0], fields[1], sep = "\t", file = write[languageof[fields[0]]])
  read.close()
  for language in languages:
    if language != "\\N":
      write[language].close()

def subpartitionlinks():
  print("Subpartitioning links...")

  languages = loadlanguageset()
  languageof = loadlanguagemap()

  for idiom in languages:
    if idiom != "\\N":
      print("Writing links (" + idiom + ")...")
      read = open("temporary/links/" + idiom + ".txt", "r", encoding = "utf-8")
      if not isdir("temporary/links/" + idiom): 
        makedirs("temporary/links/" + idiom)
      writes = {}
      for tongue in languages:
        if tongue != "\\N":
          writes[tongue] = open("temporary/links/" + idiom + "/" + tongue + ".txt", "w", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        if fields[1] in languageof and languageof[fields[1]] != "\\N":
          print(fields[0], fields[1], sep = "\t", file = writes[languageof[fields[1]]])
      read.close()
      for tongue in languages:
        if tongue != "\\N":
          writes[tongue].close()

def countcharacters():
  print("Counting characters...")

  languages = loadlanguageset()

  if not isdir("characters"):
    makedirs("characters")
  for language in languages:
    if language != "\\N":
      print("Reading characters (" + language + ")...")
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      characters = set()
      frequency = {}
      lines = {}
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        for character in set(fields[2]):
          characters.add(character)
          if character not in frequency:
            frequency[character] = 0
          frequency[character] += 1
          if randint(1, frequency[character]) == 1:
            lines[character] = line
      read.close()
      characters = list(characters)
      characters.sort()

      print("Writing characters (" + language + ")...")
      write = open("characters/characters-" + language + ".txt", "w", encoding = "utf-8")
      for character in characters:
        print(ord(character), hex(ord(character)), character, frequency[character], lines[character], sep = "\t", end = "", file = write)
      write.close()

def countwords():
  print("Counting frequency of words...")

  languages = loadlanguageset()

  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  if not isdir("words"):
    makedirs("words")
  for language in languages:
    if language != "\\N":
      spellchecks = loadspellchecker(language)

      print("Reading old words (" + language + ")...")
      words = set()
      oldsentences = {}
      identification = {}
      owner = {}
      try:
        read = open("words-old/words-" + language + ".txt", "r", encoding = "utf-8")
      except:
        pass
      else:
        for line in read:
          fields = findall(r"[^\t\n]+", line)
          if fields[2] != "0":
            words.add(fields[0])
            oldsentences[fields[0]] = int(fields[2])
            identification[fields[0]] = fields[4]
            owner[fields[0]] = fields[5]
        read.close()

      print("Reading words (" + language + ")...")
      newsentences = {}
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        sentence = getwordsinlanguage(janome, kkma, language, fields[2])
        for word in sentence:
          words.add(word)
          if word not in newsentences:
            newsentences[word] = 0
          newsentences[word] += 1
          if randint(1, newsentences[word]) == 1:
            identification[word] = fields[0]
            owner[word] = fields[3]
      read.close()

      for word in words:
        if word not in oldsentences:
          oldsentences[word] = 0
        if word not in newsentences:
          newsentences[word] = 0

      print("Writing words (" + language + ")...")
      words = list(words)
      words.sort()
      words.sort(key = lambda word: cleanupforsorting(word))
      write = open("words/words-" + language + ".txt", "w", encoding = "utf-8")
      for word in words:
        print(word, "+" + str(newsentences[word] - oldsentences[word]) if newsentences[word] >= oldsentences[word] else "−" + str(oldsentences[word] - newsentences[word]), newsentences[word], "+" if spellchecks(word) else "−", identification[word], owner[word], sep = "\t", file = write)
      write.close()

def counttranslations():
  print("Counting translations...")

  languages = loadlanguageset()

  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  for language in languages[: 50]:
    if language != "\\N":
      spellchecks = loadspellchecker(language)

      print("Reading links (" + language + ")...")
      linked = {}
      for idiom in languages[: 50]:
        if idiom != language and idiom != "\\N":
          read = open("temporary/links/" + language + "/" + idiom + ".txt", "r", encoding = "utf-8")
          linked[idiom] = set()
          for line in read:
            fields = findall(r"[^\t\n]+", line)
            linked[idiom].add(fields[0])
          read.close()

      print("Reading words (" + language + ")...")
      read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      words = set()
      sentences = {}
      translations = {}
      identification = {}
      owner = {}
      for idiom in languages[: 50]:
        translations[idiom] = {}
      for line in read:
        fields = findall(r"[^\t\n]+", line)
        sentence = getwordsinlanguage(janome, kkma, language, fields[2].lower())
        for word in sentence:
          words.add(word)
          if word not in sentences:
            sentences[word] = 0
          sentences[word] += 1
          if randint(1, sentences[word]) == 1:
            identification[word] = fields[0]
            owner[word] = fields[3]
          for idiom in languages[: 50]:
            if idiom != language and idiom != "\\N":
              if fields[0] in linked[idiom]:
                if word not in translations[idiom]:
                  translations[idiom][word] = 0
                translations[idiom][word] += 1
      read.close()
      words = list(words)
      words.sort()
      words.sort(key = lambda word: cleanupforsorting(word))

      print("Writing words (" + language + ")...")
      if not isdir("translations/" + language):
        makedirs("translations/" + language)
      for idiom in languages[: 50]:
        if idiom != language and idiom != "\\N":
          write = open("translations/" + language + "/translations-" + language + "-" + idiom + ".txt", "w", encoding = "utf-8")
          for word in words:
            print(word, sentences[word], translations[idiom][word] if word in translations[idiom] else 0, "+" if spellchecks(word) else "−", identification[word], owner[word], sep = "\t", file = write)
          write.close()

def counttranslationsuser(source, target, user):
  print("Counting translations...")
  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  spellchecks = loadspellchecker(source)

  print("Reading links (" + source + ")...")
  linked = {}
  read = open("temporary/links/" + source + "/" + target + ".txt", "r", encoding = "utf-8")
  linked[target] = set()
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    linked[target].add(fields[0])
  read.close()

  print("Reading words (" + source + ")...")
  read = open("temporary/sentences/" + source + ".txt", "r", encoding = "utf-8")
  words = set()
  sentences = {}
  translations = {}
  identification = {}
  owner = {}
  translations[target] = {}
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    sentence = getwordsinlanguage(janome, kkma, source, fields[2].lower())
    for word in sentence:
      words.add(word)
      if word not in sentences:
        sentences[word] = 0
      sentences[word] += 1
      if randint(1, sentences[word]) == 1:
        identification[word] = fields[0]
        owner[word] = fields[3]
      if fields[3] == user:
        if fields[0] in linked[target]:
          if word not in translations[target]:
            translations[target][word] = 0
          translations[target][word] += 1
  read.close()
  words = list(words)
  words.sort()
  words.sort(key = lambda word: cleanupforsorting(word))

  print("Writing words (" + source + ")...")
  if not isdir("translations-user/" + source):
    makedirs("translations-user/" + source)
  write = open("translations-user/" + source + "/translations-" + source + "-" + target + ".txt", "w", encoding = "utf-8")
  for word in words:
    print(word, sentences[word], translations[target][word] if word in translations[target] else 0, "+" if spellchecks(word) else "−", identification[word], owner[word], sep = "\t", file = write)
  write.close()

def selectsentences():
  print("Selecting sentences...")

  languages = loadlanguageset()

  janome = Tokenizer(wakati = True)
  kkma = Kkma()
  if not isdir("sentences"): 
    makedirs("sentences")
  for language in languages:
    if language != "\\N":
      spellchecks = loadspellchecker(language)

      translations = {}
      for tongue in languages:
        if tongue != "\\N" and tongue != language:
          print("Counting translations (" + language + "-" + tongue + ")...")
          file = open("temporary/links/" + language + "/" + tongue + ".txt", "r", encoding = "utf-8")
          for line in file:
            fields = findall(r"[^\t\n]+", line)
            if fields[0] not in translations:
              translations[fields[0]] = set()
            translations[fields[0]].add(tongue)
          file.close()
      for id in translations:
        translations[id] = len(translations[id])

      print("Reading words (" + language + ")...")
      dictionary = {}
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        if len(fields[2]) >= minimum or fields[1] in ("cmn", "jpn", "kor", "lzh", "wuu", "yue") and len(fields[2]) >= minimumasian:
          sentence = getwordsinlanguage(janome, kkma, language, fields[2].lower())
          for word in sentence:
            if word not in dictionary:
              dictionary[word] = []
            dictionary[word].append(fields[0])
      file.close()
      for word in dictionary:
        shuffle(dictionary[word])
        dictionary[word].sort(key = lambda id: translations[id] if id in translations else 0, reverse = True)

      print("Selecting IDs (" + language + ")...")
      ids = set()
      for word in dictionary:
        if not search(r"\d", word) and spellchecks(word):
          ids.update(dictionary[word][: 10])

      print("Reading sentences (" + language + ")...")
      sentences = []
      file = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
      for line in file:
        fields = findall(r"[^\t\n]+", line)
        if fields[0] in ids:
          sentences.append(line)
      file.close()
      shuffle(sentences)

      print("Writing sentences (" + language + ")...")
      file = open("sentences/sentences-" + language + ".txt", "w", encoding = "utf-8")
      for sentence in sentences:
        print(sentence, end = "", file = file)

def breaksrulesofidenticalwrappingmarks(name, mark, text):
  messages = []
  if findall(r"""\w""" + mark + r"""\w""", text):
    messages.append(name + ": preceeded and succeeded by letter or digit")
  if findall(r"""(\s|^)""" + mark + r"""(\s|$)""", text):
    messages.append(name + ": preceeded and succeeded by space")
  if findall(r"""^([^""" + mark + r"""]*""" + mark + r"""[^""" + mark + r"""]*""" + mark + r""")*[^""" + mark + r"""]*""" + mark + r"""[^""" + mark + r"""]*$""", text):
    messages.append(name + ": odd number")
  return messages

def breaksrulesofsymmetricwrappingmarks(name, opening, closing, text):
  messages = []
  if findall(r"""\w""" + opening, text):
    messages.append(name + ": opening mark preceeded by letter or digit")
  if findall(opening + r"""\s""", text):
    messages.append(name + ": opening mark succeeded by space")
  if findall(r"""\s""" + closing, text):
    messages.append(name + ": closing mark preceeded by space")
  if findall(closing + r"""\w""", text):
    messages.append(name + ": closing mark succeeded by letter or digit")
  if findall(opening + r"""[^""" + opening + closing + r"""]*$""", text):
    messages.append(name + ": unclosed opening mark")
  if findall(r"""^[^""" + opening + closing + r"""]*""" + closing, text):
    messages.append(name + ": unopened closing mark")
  if findall(opening + r"""[^""" + opening + closing + r"""]*""" + opening, text):
    messages.append(name + ": unbalanced opening marks")
  if findall(closing + r"""[^""" + opening + closing + r"""]*""" + closing, text):
    messages.append(name + ": unbalanced closing marks")
  return messages

def breaksrulesoffinnishguillemets(text):
  messages = breaksrulesofidenticalwrappingmarks("Guillemets", r"»", text)
  if findall(r"""«""", text):
    messages.append("Guillemets: left-pointing not used")
  return messages

def breaksrulesoffrenchguillemets(text):
  messages = []
  if findall(r"""\w«""", text):
    messages.append("Guillemets: opening mark preceeded by letter or digit")
  if findall(r"""«\S""", text):
    messages.append("Guillemets: opening mark not succeeded by space")
  if findall(r"""\S»""", text):
    messages.append("Guillemets: closing mark not preceeded by space")
  if findall(r"""»\w""", text):
    messages.append("Guillemets: closing mark succeeded by letter or digit")
  if findall(r"""«[^«»]*$""", text):
    messages.append("Guillemets: unclosed opening mark")
  if findall(r"""^[^«»]*»""", text):
    messages.append("Guillemets: unopened closing mark")
  if findall(r"""«[^«»]*«""", text):
    messages.append("Guillemets: unbalanced opening marks")
  if findall(r"""»[^«»]*»""", text):
    messages.append("Guillemets: unbalanced closing marks")
  return messages

def breaksrulesofenglishquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("English quotation marks", r"“", r"”", text)
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def breaksrulesoffinnishquotationmarks(text):
  messages = breaksrulesofidenticalwrappingmarks("Finnish quotation marks", r"”", text)
  if findall(r"""“""", text):
    messages.append("Left quotation mark: not used")
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def breaksrulesofgermanquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("German quotation marks", r"„", r"“", text)
  if findall(r"""”""", text):
    messages.append("Right quotation mark: not used")
  if findall(r"""["]""", text):
    messages.append("Straight quotation marks: not used")
  return messages

def breaksrulesofpolishquotationmarks(text):
  messages = breaksrulesofsymmetricwrappingmarks("Polish quotation marks", r"„", r"”", text)
  if findall(r"""“""", text):
    messages.append("Left quotation mark: not used")
  if findall(r"""["]""", text):
    messages.append("Straight quotation marks: not used")
  return messages

def breaksrulesofstraightquotationmarks(text):
  messages = breaksrulesofidenticalwrappingmarks("Straight quotation marks", "\"", text)
  if findall(r"""„""", text):
    messages.append("Low quotation mark: not used")
  return messages

def analyzepunctuation():
  print("Analyzing punctuation...")
  if not isdir("problematic"):
    makedirs("problematic")
  for language in ("ber", "cat", "ces", "dan", "deu", "eng", "epo", "est", "fin", "fra", "gle", "glg", "hun", "isl", "ita", "kab", "kor", "lat", "lit", "lvs", "nld", "nob", "pol", "por", "ron", "slk", "spa", "swe", "tgl", "tok", "tur", "vie"):
    print("Writing sentences (" + language + ")...")
    read = open("temporary/sentences/" + language + ".txt", "r", encoding = "utf-8")
    write = open("problematic/problematic-" + language + ".txt", "w", encoding = "utf-8")
    for line in read:
      fields = findall(r"[^\t\n]+", line)

      for message in breaksrulesofsymmetricwrappingmarks("Braces", r"\{", r"\}", fields[2]):
        print(message, line, sep = "\t", end = "", file = write)

      for message in breaksrulesofsymmetricwrappingmarks("Brackets", r"\[", r"\]", fields[2]):
        print(message, line, sep = "\t", end = "", file = write)

      if language in ("nld",) and find(r"""^((?!\.\.\.)(?!…)\W)*\p{Ll}(?<!'s\b)(?<!'t\b)""", fields[2]):
        print("Capitalization", line, sep = "\t", end = "", file = write)
      if language not in ("nld", "tok") and find(r"""^((?!\.\.\.)(?!…)\W)*\p{Ll}""", fields[2]):
        print("Capitalization", line, sep = "\t", end = "", file = write)

      if language in ("por",) and findall(r"""ç[ei]""", fields[2], flags = I):
        print("Cedilla: followed by e or i", line, sep = "\t", end = "", file = write)
      if language in ("ron",) and findall(r"""[şţ]""", fields[2], flags = I):
        print("Cedilla: possible homoglyph", line, sep = "\t", end = "", file = write)

      if findall(r"""\D:\d""", fields[2], flags = I):
        print("Colon: not preceeded by digit", line, sep = "\t", end = "", file = write)
      if language in ("ber", "fra", "kab") and findall(r"""[^\s\d]:""", fields[2], flags = I):
        print("Colon: preceeded by letter or punctuation", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s:""", fields[2], flags = I):
        print("Colon: preceeded by space", line, sep = "\t", end = "", file = write)
      if language in ("fin", "swe") and findall(r""":[^\w\s]""", fields[2], flags = I):
        print("Colon: succeeded by punctuation", line, sep = "\t", end = "", file = write)
      if language not in ("fin", "swe") and findall(r""":[^\d\s]""", fields[2], flags = I):
        print("Colon: succeeded by letter or punctuation", line, sep = "\t", end = "", file = write)
      if language in ("ber", "fra", "kab") and findall(r"""\d:\D""", fields[2], flags = I):
        print("Colon: not succeeded by digit", line, sep = "\t", end = "", file = write)

      if findall(r"""\s,""", fields[2], flags = I):
        print("Comma: preceeded by space", line, sep = "\t", end = "", file = write)
      if findall(r"""\D,\d""", fields[2], flags = I):
        print("Comma: not preceeded by digit", line, sep = "\t", end = "", file = write)
      if findall(r""",[^\W\d]""", fields[2], flags = I):
        print("Comma: succeeded by letter", line, sep = "\t", end = "", file = write)

      if findall(r"""[a-z][\u0430-\u044F]|[\u0430-\u044F][a-z]""", fields[2], flags = I):
        print("Cyrillic characters: possible homoglyphs", line, sep = "\t", end = "", file = write)

      if language in ("por",) and findall(r"""ü""", fields[2], flags = I):
        print("Dieresis: not used", line, sep = "\t", end = "", file = write)

      if findall(r"""\u2033""", fields[2], flags = I):
        print("Double prime: possible homoglyph", line, sep = "\t", end = "", file = write)

      if findall(r"""([^.]|^)\.\.([^.]|$)""", fields[2], flags = I):
        print("Ellipsis: too short", line, sep = "\t", end = "", file = write)

      # if findall(r"""--|(\s|^)-(\s|$)""", fields[2], flags = I):
      #   print("Em dash: homoglyph", line, sep = "\t", end = "", file = write)

      # if findall(r"""\d-\d""", fields[2], flags = I):
      #   print("En dash or figure dash: possible homoglyph", line, sep = "\t", end = "", file = write)

      if language in ("ber", "fra", "kab") and findall(r"""\w[!]""", fields[2], flags = I):
        print("Exclamation mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s[!]""", fields[2], flags = I):
        print("Exclamation mark: preceeded by space", line, sep = "\t", end = "", file = write)
      if findall(r"""[!]\w""", fields[2], flags = I):
        print("Exclamation mark: succeeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""\w[¡]""", fields[2], flags = I):
        print("Inverted exclamation mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""[¡]\s""", fields[2], flags = I):
        print("Inverted exclamation mark: succeeded by space", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""^[^¡!]*[!]""", fields[2], flags = I):
        print("Exclamation mark: unopened exclamation mark", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""[¡][^¡!]*$""", fields[2], flags = I):
        print("Exclamation mark: unclosed exclamation mark", line, sep = "\t", end = "", file = write)
      if language not in ("spa",) and findall(r"""[¡]""", fields[2], flags = I):
        print("Inverted exclamation mark: not used", line, sep = "\t", end = "", file = write)

      if language == "kor" and findall(r"""\w[^.…?!‽？~]*$""", fields[2], flags = I):
        print("Final punctuation", line, sep = "\t", end = "", file = write)
      if language != "kor" and findall(r"""\w[^.…?!‽]*$""", fields[2], flags = I):
        print("Final punctuation", line, sep = "\t", end = "", file = write)

      if findall(r"""[a-z][α-ω]|[α-ω][a-z]""", fields[2], flags = I):
        print("Greek characters: possible homoglyphs", line, sep = "\t", end = "", file = write)

      if language in ("fin", "swe"):
        for message in breaksrulesoffinnishguillemets(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("ber", "fra", "kab", "vie"):
        for message in breaksrulesoffrenchguillemets(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("ces", "dan", "deu", "hun", "pol", "slk"):
        for message in breaksrulesofsymmetricwrappingmarks("Guillemets", r"»", r"«", fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("cat", "epo", "est", "glg", "ita", "nob", "por", "ron", "spa", "tur"):
        for message in breaksrulesofsymmetricwrappingmarks("Guillemets", r"«", r"»", fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("eng", "gle", "isl", "kor", "lat", "lit", "lvs", "nld", "tok") and findall(r"""[«»]""", fields[2], flags = I):
        print("Guillemets: not used", line, sep = "\t", end = "", file = write)

      if findall(r"""\u05C1|\u05C2""", fields[2], flags = I):
        print("Hebrew dot", line, sep = "\t", end = "", file = write)

      if findall(r"""\u200E""", fields[2], flags = I):
        print("Left-to-right mark", line, sep = "\t", end = "", file = write)

      if findall(r"""x\d|\dx|\d\s*x\s*\d""", fields[2], flags = I):
        print("Multiplication sign: possible homoglyph", line, sep = "\t", end = "", file = write)

      if language not in ("glg", "ita", "por", "spa") and findall(r"""º""", fields[2], flags = I):
        print("Ordinal indicator: possible homoglyph", line, sep = "\t", end = "", file = write)

      for message in breaksrulesofsymmetricwrappingmarks("Parentheses", r"\(", r"\)", fields[2]):
        print(message, line, sep = "\t", end = "", file = write)

      if language == "eng" and findall(r"""\s[.](?![\d.])""", fields[2], flags = I):
        print("Period: preceeded by space", line, sep = "\t", end = "", file = write)
      if language != "eng" and findall(r"""\s[.](?![.])""", fields[2], flags = I):
        print("Period: preceeded by space", line, sep = "\t", end = "", file = write)
      if language != "eng" and findall(r"""\D[.]\d""", fields[2], flags = I):
        print("Period: not preceeded by digit", line, sep = "\t", end = "", file = write)

      if findall(r"""\u2032""", fields[2], flags = I):
        print("Prime: possible homoglyph", line, sep = "\t", end = "", file = write)

      if language in ("ber", "fra", "kab") and findall(r"""\w[?]""", fields[2], flags = I):
        print("Question mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s[?]""", fields[2], flags = I):
        print("Question mark: preceeded by space", line, sep = "\t", end = "", file = write)
      if findall(r"""[?]\w""", fields[2], flags = I):
        print("Question mark: succeeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""\w[¿]""", fields[2], flags = I):
        print("Inverted question mark: preceeded by letter or digit", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""[¿]\s""", fields[2], flags = I):
        print("Inverted question mark: succeeded by space", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""^[^¿?]*[?]""", fields[2], flags = I):
        print("Question mark: unopened question mark", line, sep = "\t", end = "", file = write)
      if language in ("spa",) and findall(r"""[¿][^¿?]*$""", fields[2], flags = I):
        print("Question mark: unclosed question mark", line, sep = "\t", end = "", file = write)
      if language not in ("spa",) and findall(r"""[¿]""", fields[2], flags = I):
        print("Inverted question mark: not used", line, sep = "\t", end = "", file = write)

      if language in ("ber", "cat", "dan", "eng", "epo", "fra", "gle", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
        for message in breaksrulesofenglishquotationmarks(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("fin", "swe"):
        for message in breaksrulesoffinnishquotationmarks(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("hun", "pol", "ron"):
        for message in breaksrulesofpolishquotationmarks(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("ces", "deu", "est", "isl", "lit", "slk"):
        for message in breaksrulesofgermanquotationmarks(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if language in ("ber", "cat", "dan", "eng", "epo", "fra", "glg", "ita", "kab", "kor", "lat", "lvs", "nld", "nob", "por", "spa", "tok", "tur", "vie"):
        for message in breaksrulesofstraightquotationmarks(fields[2]):
          print(message, line, sep = "\t", end = "", file = write)
      if findall(r""",,|''""", fields[2], flags = I):
        print("Quotation marks: homoglyphs", line, sep = "\t", end = "", file = write)
      if findall(r"""[‘’“”].*['"]|['"].*[‘’“”]""", fields[2], flags = I):
        print("Quotation marks: mixed curly and straight", line, sep = "\t", end = "", file = write)

      if language in ("ber", "fra", "kab") and findall(r"""\S;""", fields[2], flags = I):
        print("Semicolon: not preceeded by space", line, sep = "\t", end = "", file = write)
      if language not in ("ber", "fra", "kab") and findall(r"""\s;""", fields[2], flags = I):
        print("Semicolon: preceeded by space", line, sep = "\t", end = "", file = write)
      if findall(r""";\w""", fields[2], flags = I):
        print("Semicolon: succeeded by letter or digit", line, sep = "\t", end = "", file = write)

      if findall(r"""\u200B""", fields[2], flags = I):
        print("Zero-width space", line, sep = "\t", end = "", file = write)
    read.close()
    write.close()

def findsimilar():
  print("Writing similar...")
  read = open("sentences_detailed.csv", "r", encoding = "utf-8")
  language = {}
  user = {}
  seen = {}
  if not isdir("similar"): 
    makedirs("similar")
  write = {}
  write["!"] = open("similar/similar.txt", "w", encoding = "utf-8")
  for line in read:
    fields = findall(r"[^\t\n]+", line)
    if fields[1] not in language:
      language[fields[1]] = fields[1]
    if fields[3] not in user:
      user[fields[3]] = fields[3]
    sentence = hash(cleanupforhashing(fields[2]))
    if sentence in seen:
      if seen[sentence][1] == fields[1]:
        if fields[1] not in write:
          write[fields[1]] = open("similar/similar-" + fields[1] + ".txt", "w", encoding = "utf-8")
        print(str(seen[sentence][0]), seen[sentence][2], fields[0], fields[3], sep = "\t", file = write[fields[1]])
      else:
        print(str(seen[sentence][0]), seen[sentence][1], seen[sentence][2], fields[0], fields[1], fields[3], sep = "\t", file = write["!"])
    else:
      seen[sentence] = (int(fields[0]), language[fields[1]], user[fields[3]])
  read.close()
  for tongue in write:
    write[tongue].close()

writelanguageset()
print("")
partitionsentences()
print("")
partitionlinks()
print("")
subpartitionlinks()
print("")
countcharacters()
print("")
countwords()
print("")
counttranslations()
print("")
counttranslationsuser("eng", "por", "Cangarejo")
print("")
selectsentences()
print("")
analyzepunctuation()
print("")
findsimilar()
