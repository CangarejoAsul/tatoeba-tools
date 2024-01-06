from os import makedirs
from os.path import isdir
from re import findall
from unicodedata import normalize

languages = set([
  "eng",
  "rus",
  "ita",
  "tur",
  "epo",
  "ber",
  "kab",
  "deu",
  "fra",
  "por",
  "spa",
  "hun",
  # "jpn",
  "heb",
  "ukr",
  "nld",
  "fin",
  "pol",
  "lit",
  "mkd",
  "mar",
  # "cmn",
  "ces",
  "dan",
  "tok",
  "swe",
  "srp",
  "lat",
  "ara",
  "ell",
  "ron",
  "ina",
  "pes",
  "bul",
  "tlh",
  "swc",
  "tgl",
  "vie",
  "hau",
  "lfn",
  "nds",
  "ind",
  "slk",
  "nob",
  "jbo",
  "hin",
  "tat",
  "nnb",
  "isl",
  "bel",
  "ckb",
  "yid",
  "kor",
  "ido",
  "kmr",
])

print("Reading distinct...")
distinct = {}
total = {}
for line in open("sentences_detailed.csv", "r", encoding = "utf-8"):
  split = findall(r"[^\t\n]+", line)
  if split[1] in languages:
    if split[1] not in distinct:
      distinct[split[1]] = {}
    if split[3] not in distinct[split[1]]:
      distinct[split[1]][split[3]] = set()
    distinct[split[1]][split[3]].update(findall(r"\w+", normalize("NFKC", split[2]).lower()))
    if split[1] not in total:
      total[split[1]] = {}
    if split[3] not in total[split[1]]:
      total[split[1]][split[3]] = 0
    total[split[1]][split[3]] += len(findall(r"\w+", normalize("NFKC", split[2]).lower()))
for language in distinct:
  for user in distinct[language]:
    distinct[language][user] = (len(distinct[language][user]), total[language][user], float(len(distinct[language][user])) / total[language][user])
  distinct[language] = list(distinct[language].items())
  distinct[language].sort(key = lambda tuple: tuple[1][0], reverse = True)

print("Writing distinct...")
if not isdir("distinct"): 
  makedirs("distinct")
for language in distinct:
  file = open("distinct/distinct_" + language + ".txt", "w", encoding = "utf-8")
  for user, (unique, total, ratio) in distinct[language]:
    print(user, unique, total, ratio, sep = "\t", file = file)
