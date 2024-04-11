from sqlite3 import connect
from re import findall
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
    SELECT *
    FROM sentences
    INNER JOIN words
    ON sentences.id = words.id AND words.word = ?""")
  list = [word[0]]
  for i, target in enumerate(targets):
    query += ("""
      INNER JOIN links AS links""" + str(i) + """
      ON sentences.id = links""" + str(i) + """.source
      INNER JOIN sentences AS sentences""" + str(i) + """
      ON links""" + str(i) + """.target = sentences""" + str(i) + """.id AND sentences""" + str(i) + """.language = ?""")
    list.append(target)
  query += ("""
    WHERE sentences.language = ?;""")
  list.append(source[0])

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

connection = connect("data.db")
cursor = connection.cursor()

try:
  cursor.execute("CREATE TABLE sentences (id integer PRIMARY KEY, language text NOT NULL, sentence text NOT NULL);")
  connection.commit()
except:
  pass
else:
  cursor.execute("CREATE TABLE words (id integer NOT NULL, word text NOT NULL);")
  connection.commit()

  file = open("sentences_detailed.csv", "r", encoding = "utf-8")
  for line in file:
    fields = findall(r"[^\t\n]+", line)
    cursor.execute("INSERT INTO sentences (id, language, sentence) VALUES (?, ?, ?);", (fields[0], fields[1], fields[2]))
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
