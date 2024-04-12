from pathlib import Path
from re import findall
from sqlite3 import connect
from tkinter import Button, END, Entry, Label, StringVar, Text, Tk

def search():
  word = findall(r"\w+", wordentry.get().lower())
  source = findall(r"\w+", sourcelanguageentry.get().lower())
  targets = findall(r"\w[\w'-]*\w|\w", targetlanguagesentry.get().lower())
  if len(word) != 1 or len(source) != 1:
    resultstext.delete("1.0", END)
    resultstext.insert(END, "Please search for exactly one word in exactly one source language.")
    return

  query = ("""
      SELECT DISTINCT
        `sentences-""" + source[0] + """`.id,
        `sentences-""" + source[0] + """`.language,
        `sentences-""" + source[0] + """`.sentence
      FROM `sentences-""" + source[0] + """`
      INNER JOIN words
      ON `sentences-""" + source[0] + """`.id = words.id AND words.word = ?""")
  list = [word[0]]
  for i, target in enumerate(targets):
    query += ("""
      INNER JOIN links AS links""" + str(i) + """
      ON `sentences-""" + source[0] + """`.id = links""" + str(i) + """.source
      INNER JOIN `sentences-""" + target + """` AS sentences""" + str(i) + """
      ON links""" + str(i) + """.target = sentences""" + str(i) + """.id""")
  query += (""";""")

  cursor.execute(query, tuple(list))
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

if Path("data.db").isfile():
  connection = connect("data.db")
  cursor = connection.cursor()
else:
  connection = connect("data.db")
  cursor = connection.cursor()

  cursor.execute("CREATE TABLE words (id integer NOT NULL, word text NOT NULL);")
  connection.commit()

  file = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    try:
      cursor.execute("CREATE TABLE `sentences-" + fields[1] + "` (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL);")
    except:
      pass
    cursor.execute("INSERT INTO `sentences-" + fields[1] + "` (id, language, sentence) VALUES (?, ?, ?);", (fields[0], fields[1], fields[2]))
    for word in findall(r"\w[\w'-]*\w|\w", fields[2].lower()):
      cursor.execute("INSERT INTO words (id, word) VALUES (?, ?);", (fields[0], word))
  file.close()
  connection.commit()

  cursor.execute("CREATE TABLE links (source integer NOT NULL, target integer NOT NULL);")
  connection.commit()

  file = open("links.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    cursor.execute("INSERT INTO links (source, target) VALUES (?, ?);", (fields[0], fields[1]))
  file.close()
  connection.commit()

  cursor.execute("CREATE TABLE dummy (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL);")
  connection.commit()

try:
  cursor.execute("SELECT * FROM dummy;")
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
