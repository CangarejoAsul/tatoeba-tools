from pathlib import Path
from re import findall
from sqlite3 import connect
from tkinter import Button, END, Entry, Label, StringVar, Text, Tk

def search():
  words = findall(r"\w[\w',:.-]*\w|\w", wordentry.get().lower())
  source = findall(r"\w+", sourcelanguageentry.get().lower())
  targets = findall(r"\w+", targetlanguagesentry.get().lower())
  if len(source) != 1:
    resultstext.delete("1.0", END)
    resultstext.insert(END, "Please choose exactly one source language.")
    return

  arguments = []
  query = ("""
      SELECT DISTINCT
        `sentences-""" + source[0] + """`.id,
        `sentences-""" + source[0] + """`.language,
        `sentences-""" + source[0] + """`.sentence
      FROM `sentences-""" + source[0] + """`""")
  for i, word in enumerate(words):
    query += ("""
      INNER JOIN `words-""" + source[0] + """` AS words""" + str(i) + """
      ON `sentences-""" + source[0] + """`.id = words""" + str(i) + """.id AND words""" + str(i) + """.word = ?""")
    arguments.append(word)
  for i, target in enumerate(targets):
    query += ("""
      INNER JOIN `links-""" + source[0] + """-""" + target + """` AS links""" + str(i) + """
      ON `sentences-""" + source[0] + """`.id = links""" + str(i) + """.source
      INNER JOIN `sentences-""" + target + """` AS sentences""" + str(i) + """
      ON links""" + str(i) + """.target = sentences""" + str(i) + """.id""")
  query += (""";""")

  cursor.execute(query, tuple(arguments))
  results = cursor.fetchall()
  resultstext.delete("1.0", END)
  if results:
    for i, row in enumerate(results):
      resultstext.insert(END, str(row[0]) + "\t" + row[1] + "\t" + row[2] + "\n")
  else:
    resultstext.insert(END, "There are no results.\n")

def close():
  cursor.close()
  connection.close()
  window.destroy()

if Path("data.db").is_file():
  connection = connect("data.db")
  cursor = connection.cursor()
else:
  connection = connect("data.db")
  cursor = connection.cursor()

  language = {}
  file = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    language[int(fields[0])] = fields[1]
    try:
      cursor.execute("CREATE TABLE `sentences-" + fields[1] + "` (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL);")
      cursor.execute("CREATE TABLE `words-" + fields[1] + "` (id integer NOT NULL, word text NOT NULL);")
    except:
      pass
    cursor.execute("INSERT INTO `sentences-" + fields[1] + "` (id, language, sentence) VALUES (?, ?, ?);", (fields[0], fields[1], fields[2]))
    for word in findall(r"\w[\w',:.-]*\w|\w", fields[2].lower()):
      cursor.execute("INSERT INTO `words-" + fields[1] + "` (id, word) VALUES (?, ?);", (fields[0], word))
  file.close()
  connection.commit()

  file = open("links.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    try:
      cursor.execute("CREATE TABLE `links-" + language[int(fields[0])] + "-" + language[int(fields[1])] + "` (source integer NOT NULL, target integer NOT NULL);")
    except:
      pass
    if int(fields[0]) in language and int(fields[1]) in language:
      cursor.execute("INSERT INTO `links-" + language[int(fields[0])] + "-" + language[int(fields[1])] + "` (source, target) VALUES (?, ?);", (fields[0], fields[1]))
  file.close()
  connection.commit()

  cursor.execute("CREATE TABLE version240413 (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL);")
  connection.commit()

try:
  cursor.execute("SELECT * FROM version240413;")
except:
  print("Please delete data.db.")
  quit()

window = Tk()
window.title("Search")
window.protocol("WM_DELETE_WINDOW", close)
wordlabel = Label(window, text = "Word:")
wordlabel.pack()
wordentry = Entry(window, textvariable = StringVar(window, value = "cat"))
wordentry.pack()
sourcelanguagelabel = Label(window, text = "Source language:")
sourcelanguagelabel.pack()
sourcelanguageentry = Entry(window, textvariable = StringVar(window, value = "eng"))
sourcelanguageentry.pack()
targetlanguageslabel = Label(window, text = "Target languages:")
targetlanguageslabel.pack()
targetlanguagesentry = Entry(window, textvariable = StringVar(window, value = "deu, ron"))
targetlanguagesentry.pack()
searchbutton = Button(window, text = "Search", command = search)
searchbutton.pack()
resultstext = Text(window)
resultstext.pack()
window.mainloop()
