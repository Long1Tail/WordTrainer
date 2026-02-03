import sqlite3
import sys

name = "words.sqlite"
connection = sqlite3.connect(name)
cursor = connection.cursor()
request = ''
word = ''
translation = ''
language = ''
question = ''

print('Чтобы выйти, введите "exit"')
for i in sys.stdin:
    if i != 'exit':
        i = i.rstrip()
        word, translation, language = i.split()
        question = input(f'Вы уверены, что хотите добавить в колонку "{language}" слово "{word}" с переводом '
                         f'"{translation}"?\ny - да\n n - нет')
        if question == 'y':
            request = f'INSERT INTO words(russian_word, {language} Values("{word}", "{translation}"'
            cursor.execute(request)
        else:
            continue
    else:
        break
connection.commit()