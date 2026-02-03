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
    if i == 'exit':
        break
    else:
        i = i.rstrip()
        language = i
        question = input(f'Вы уверены, что хотите удалить язык "{language}"?\ny - да\n n - нет')
        if question == 'y':
            request = f'DELETE from langs where language="{language}"'
            cursor.execute(request)
            request = f'ALTER TABLE words DROP COLUMN {language}'
            cursor.execute()
        elif question == 'n':
            continue
        else:
            print('Неверный ввод. Запрос обнулён')
connection.commit()
