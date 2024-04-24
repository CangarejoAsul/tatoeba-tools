from pathlib import Path
from re import findall
from sqlite3 import connect
from tkinter import Button, END, Entry, Label, StringVar, Text, Tk

def search():
  sourcewords = findall(r"\w[\w',:.-]*\w|\w", sourcewordsentry.get().lower())
  sourcelanguages = findall(r"\w+", sourcelanguagesentry.get().lower())
  minlength = int(minlengthentry.get())
  maxlength = int(maxlengthentry.get())
  includedusers = findall(r"\w+", includedusersentry.get())
  excludedusers = findall(r"\w+", excludedusersentry.get())
  targetwords = findall(r"\w[\w',:.-]*\w|\w", targetwordsentry.get().lower())
  targetlanguages = findall(r"\w+", targetlanguagesentry.get().lower())

  arguments = []
  query = ("""
        SELECT DISTINCT
          sentences.id,
          sentences.language,
          sentences.sentence,
          sentences.user
        FROM sentences""")
  for i, sourceword in enumerate(sourcewords):
    query += ("""
        INNER JOIN words AS sourcewords""" + str(i) + """
        ON sentences.id = sourcewords""" + str(i) + """.id AND sourcewords""" + str(i) + """.word = ?""")
    arguments.append(sourceword)
  for i, targetlanguage in enumerate(targetlanguages):
    query += ("""
        INNER JOIN links AS links""" + str(i) + """
        ON sentences.id = links""" + str(i) + """.source
        INNER JOIN sentences AS sentences""" + str(i) + """
        ON links""" + str(i) + """.target = sentences""" + str(i) + """.id AND sentences""" + str(i) + """.language = ?""")
    arguments.append(targetlanguage)
    for j, targetword in enumerate(targetwords):
      query += ("""
        INNER JOIN words AS targetwords""" + str(i) + """x""" + str(j) + """
        ON sentences""" + str(i) + """.id = targetwords""" + str(i) + """x""" + str(j) + """.id AND targetwords""" + str(i) + """x""" + str(j) + """.word = ?""")
      arguments.append(targetword)
  if not targetlanguages and targetwords:
    query += ("""
        INNER JOIN links AS wordlinks
        ON sentences.id = wordlinks.source
        INNER JOIN sentences AS wordsentences
        ON wordlinks.target = wordsentences.id""")
    for i, targetword in enumerate(targetwords):
      query += ("""
        INNER JOIN words AS targetwords""" + str(i) + """
        ON wordsentences.id = targetwords""" + str(i) + """.id AND targetwords""" + str(i) + """.word = ?""")
      arguments.append(targetword)
  query += ("""
        WHERE length(sentences.sentence) >= ? AND length(sentences.sentence) < ?""")
  arguments.extend((minlength, maxlength))
  if sourcelanguages:
    query += (" AND (" + " OR ".join(["sentences.language = ?"] * len(sourcelanguages)) + ")")
    arguments.extend(sourcelanguages)
  if includedusers:
    query += (" AND (" + " OR ".join(["sentences.user = ?"] * len(includedusers)) + ")")
    arguments.extend(includedusers)
  if excludedusers:
    query += (" AND NOT (" + " OR ".join(["sentences.user = ?"] * len(excludedusers)) + ")")
    arguments.extend(excludedusers)
  query += ("""
        ORDER BY sentences.id DESC""")
  query += (""";""")
  print(query)

  cursor.execute(query, tuple(arguments))
  results = cursor.fetchall()
  resultstext.delete("1.0", END)
  if results:
    for i, row in enumerate(results):
      resultstext.insert(END, str(row[0]) + "\t" + row[1] + "\t" + row[2] + "\t" + row[3] + "\n")
  else:
    resultstext.insert(END, "There are no results.\n")

def close():
  cursor.close()
  connection.close()
  window.destroy()

if Path("data").is_file():
  connection = connect("data")
  cursor = connection.cursor()
else:
  connection = connect("data")
  cursor = connection.cursor()

  cursor.execute("CREATE TABLE sentences (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL, user text NOT NULL);")
  cursor.execute("CREATE INDEX sentences_language ON sentences (language);")
  cursor.execute("CREATE INDEX sentences_user ON sentences (user);")
  cursor.execute("CREATE TABLE words (id integer NOT NULL, word text NOT NULL);")
  cursor.execute("CREATE INDEX words_id ON words (id);")
  cursor.execute("CREATE INDEX words_word ON words (word);")

  language = {}
  file = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    language[int(fields[0])] = fields[1]
    cursor.execute("INSERT INTO sentences (id, language, sentence, user) VALUES (?, ?, ?, ?);", (fields[0], fields[1], fields[2], fields[3]))
    for word in set(findall(r"\w[\w',:.-]*\w|\w", fields[2].lower())):
      cursor.execute("INSERT INTO words (id, word) VALUES (?, ?);", (fields[0], word))
  file.close()
  connection.commit()

  cursor.execute("CREATE TABLE links (source integer NOT NULL, target integer NOT NULL);")
  cursor.execute("CREATE INDEX links_source ON links (source);")
  cursor.execute("CREATE INDEX links_target ON links (target);")

  file = open("links.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    if int(fields[0]) in language and int(fields[1]) in language:
      cursor.execute("INSERT INTO links (source, target) VALUES (?, ?);", (fields[0], fields[1]))
  file.close()
  connection.commit()

window = Tk()
window.title("Experimental Search")
window.protocol("WM_DELETE_WINDOW", close)
sourcewordslabel = Label(window, text = "Source words:")
sourcewordslabel.pack()
sourcewordsentry = Entry(window, textvariable = StringVar(window, value = "cat"))
sourcewordsentry.pack()
sourcelanguageslabel = Label(window, text = "Source languages:")
sourcelanguageslabel.pack()
sourcelanguagesentry = Entry(window, textvariable = StringVar(window, value = "eng"))
sourcelanguagesentry.pack()
minlengthlabel = Label(window, text = "Min length:")
minlengthlabel.pack()
minlengthentry = Entry(window, textvariable = StringVar(window, value = "0"))
minlengthentry.pack()
maxlengthlabel = Label(window, text = "Max length:")
maxlengthlabel.pack()
maxlengthentry = Entry(window, textvariable = StringVar(window, value = "10000"))
maxlengthentry.pack()
targetwordslabel = Label(window, text = "Target words:")
targetwordslabel.pack()
targetwordsentry = Entry(window)
targetwordsentry.pack()
includeduserslabel = Label(window, text = "Belonging to users:")
includeduserslabel.pack()
includedusersentry = Entry(window)
includedusersentry.pack()
excludeduserslabel = Label(window, text = "Not belonging to users:")
excludeduserslabel.pack()
excludedusersentry = Entry(window)
excludedusersentry.pack()
targetlanguageslabel = Label(window, text = "Target languages:")
targetlanguageslabel.pack()
targetlanguagesentry = Entry(window, textvariable = StringVar(window, value = "deu, ron"))
targetlanguagesentry.pack()
searchbutton = Button(window, text = "Search", command = search)
searchbutton.pack()
resultstext = Text(window)
resultstext.pack()
window.mainloop()
