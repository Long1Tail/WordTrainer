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
        question = input(f'Вы уверены, что хотите добавить в язык "{language}"?\ny - да\n n - нет')
        if question == 'y':
            request = f'INSERT INTO langs VALUES("{language}")'
            cursor.execute(request)
            request = f'ALTER TABLE words ADD {language} TEXT'
            cursor.execute()
        elif question == 'n':
            continue
        else:
            print('Неверрный ввод. Запрос обнулён')
connection.commit()
