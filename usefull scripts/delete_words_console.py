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

print('Чтобы выйти, введите "exit".')
print('Чтобы удалить перевод слова, введите его и языки, перевод на который хотите удалить.')
print('Если хотите удалить весь ряд, просто введите слово на русском')

for i in sys.stdin:
    if i:
        if i == 'exit':
            break

        elif len(i.split()) == 1:
            i = i.rstrip()
            word = i
            question = input(f'Вы уверены, что хотите удалить слово {word} и все его переводы?\ny - да\n n - нет')
            if question == 'y':
                request = f'DELETE from words where russian_word = "{word}"'
                cursor.execute(request)
            elif question == 'n':
                continue
            else:
                print('Неверный ввод. Введите запрос заново')
        else:
            word = i.split()[0]
            language = i.split()[1:]
            question = input(f'Вы уверены, что хотите удалить переводы слова {word} на введённые вами языки?\ny - да, '
                             f'n - нет"')
            if question == 'y':
                for j in language:
                    request = f'UPDATE words SET {language} = NULL where russian_word = {word} and language = {j}'
connection.commit()
