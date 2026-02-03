import sqlite3

con = sqlite3.connect('words.sqlite')
cur = con.cursor()
request = ''
with open('words.txt', 'r') as file:
    file = file.read()
    words = list(map(lambda x: x.split, file.split('\n')))
    for i in words:
        request = f'INSERT INTO words(russian_word, {i[0]} Values("{i[1]}", "{i[2]}"'
    con.cursor()
    con.close()
