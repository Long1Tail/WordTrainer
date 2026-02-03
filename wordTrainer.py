import random
import sqlite3
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QAbstractItemView

from UI.about import AboutForm
from UI.add_language import AddLangForm
from UI.add_word import AddWordForm
from UI.dictionary import DictForm
from UI.main_window import MainWindow
from UI.results import ResultForm
from UI.settings import SettingsForm
from UI.train import TrainingForm
from UI.train_settings import TrainingSettingsDialog

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


class WordTrainer(QWidget, MainWindow):  # Класс главного окна
    def __init__(self, app: QApplication):  # Конструктор
        super().__init__()
        self.setupUi(self)
        self.app = app
        self.con = sqlite3.connect('words.sqlite')
        self.test_settings_page = TestSettings(self, self.con)
        self.settings_page = SettingsWindow(self)
        self.dict_page = DictPage(self, self.con)
        self.test = Test(self, self.con)
        self.result_page = ResultPage(self, self.con)
        self.about_page = AboutWindow(self)
        self.add_word_page = AddWordWindow(self, self.con)
        self.add_lang_page = AddLangWindow(self, self.con)

        self.begin_trainin_btn.clicked.connect(self.begin)
        self.settings_btn.clicked.connect(self.settings)
        self.open_dictionary_btn.clicked.connect(self.open_dict)
        self.about_btn.clicked.connect(self.about)

        # Задание оформления
        with open('themes\\dark_theme.qss') as f:  # стилизвция
            self.app.setStyleSheet(f.read())
            f.close()

    def begin(self):  # запуск настроек теста
        self.hide()
        self.test_settings_page.show()

    def settings(self):  # открытие окна настроек
        self.settings_page.show()

    def open_dict(self):  # открытие словаря
        self.hide()
        self.dict_page.show()

    def about(self):  # вывод справки
        self.about_page.show()

    def change_theme(self, theme):  # смена оформления
        if theme == 'Светлая':
            with open('themes/light_theme.qss') as f:
                self.app.setStyleSheet(f.read())
                f.close()
        else:
            with open('themes/dark_theme.qss') as f:
                self.app.setStyleSheet(f.read())
                f.close()


class TestSettings(QWidget, TrainingSettingsDialog):  # окно настройки теста
    def __init__(self, parent: WordTrainer, connection):  # инициальзация
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.connection = connection
        self.cur = self.connection.cursor()
        self.request = 'SELECT * FROM langs'
        self.langs = self.cur.execute(self.request).fetchall()
        self.number = 0
        self.lang = ''

        for i in range(len(self.langs)):
            self.langs[i] = self.langs[i][0]  # перевод списка из формата [(x0, ), (x1, ), (x2, )...] в [x0, x1, x2]
            # для удобства

        for i in self.langs:
            self.choose_lang_box.addItem(i)

        self.start_btn.clicked.connect(self.start_test)
        self.back_btn.clicked.connect(self.back)

    def start_test(self):  # начало теста
        self.hide()
        self.parent.test.re_init(int(self.n_of_words_edit.text()), self.choose_lang_box.currentText())
        self.parent.test.show()

    def back(self):  # возврат в злавное меню
        self.parent.show()
        self.hide()


class Test(QWidget, TrainingForm):  # окно тесста
    def __init__(self, parent, connection):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.lang = ''
        self.words = []
        self.connection = connection
        self.cur = self.connection.cursor()
        self.request = ''

        self.answer_btn.clicked.connect(self.next)
        self.finish_btn.clicked.connect(self.stop)

    def re_init(self, n, lang):  # перезапуск теста
        self.request = f'SELECT russian_word, {lang} FROM words'
        self.words = self.cur.execute(self.request).fetchall()
        random.shuffle(self.words)
        self.words = self.words[:n]
        self.word_edit.setText(self.words[0][0])

    def next(self):  # вывод следующего слова и сохранение ответа на текущее слово и, в случае завершение теста, его
        # очистка и открытие окна результатов

        self.request = f'INSERT INTO current_test(word, correct_translation, your_translation) ' \
                    f'VALUES ("{self.words[0][0]}", "{self.words[0][1]}", "{self.word_in_edit.text()}")'

        self.cur.execute(self.request)
        self.word_in_edit.setText('')
        if len(self.words) > 1:
            self.words = self.words[1:]
            self.word_edit.setText(self.words[0][0])
        else:
            self.words = []
            self.connection.commit()
            self.hide()
            self.parent.result_page.show()
            self.parent.result_page.re_init()

    def stop(self):  # остановка теста
        self.words = []
        self.connection.commit()
        self.hide()
        self.parent.result_page.show()
        self.parent.result_page.re_init()


class ResultPage(QWidget, ResultForm):  # окно результатов
    def __init__(self, parent: WordTrainer, connection):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.connection = connection
        self.answers = []
        self.request = ''
        self.cur = self.connection.cursor()

        self.again_button.clicked.connect(self.again)
        self.change_settings_again_button.clicked.connect(self.change_settings)
        self.main_menu_button.clicked.connect(self.back)

        self.result_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def re_init(self):  # перезапуск окна
        self.request = "SELECT * FROM current_test"
        self.answers = self.cur.execute(self.request).fetchall()

        self.result_view.setRowCount(len(self.answers))
        self.result_view.setColumnCount(4)

        for i in range(len(self.answers)):
            self.result_view.setItem(i, 0, QTableWidgetItem(self.answers[i][0]))
            self.result_view.setItem(i, 1, QTableWidgetItem(self.answers[i][1]))
            self.result_view.setItem(i, 2, QTableWidgetItem(self.answers[i][2]))
            if self.answers[i][1] == self.answers[i][2]:
                self.result_view.setItem(i, 3, QTableWidgetItem('+'))
            else:
                self.result_view.setItem(i, 3, QTableWidgetItem('-'))

        self.request = "DELETE FROM current_test"
        self.cur.execute(self.request)
        self.connection.commit()

        self.num_result.setText(
            f'{len(list(filter(lambda x: x[1] == x[2], self.answers)))} правильно из {len(self.answers)}')

    def again(self):  # повторный запуск с текущими настройками
        self.parent.test_settings_page.start_test()
        self.hide()

    def change_settings(self):  # запуск с изменением настроек
        self.hide()
        self.parent.test_settings_page.show()

    def back(self):  # возврат в главное меню
        self.hide()
        self.parent.show()


class SettingsWindow(QWidget, SettingsForm):  # окно настроек
    def __init__(self, parent: WordTrainer):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        self.save_button.clicked.connect(self.save)
        self.cansel_button.clicked.connect(self.back)

    def save(self):  # применение настроек
        self.parent.change_theme(self.buttonGroup.checkedButton().text())

    def back(self):  # переход в главное меню
        self.hide()
        self.parent.show()


class DictPage(QWidget, DictForm):  # страница словаря
    def __init__(self, parent, connection):
        super().__init__()
        self.setupUi(self)
        self.parent: WordTrainer = parent
        self.connection = connection
        self.cur = self.connection.cursor()
        self.request = 'SELECT * FROM langs'
        self.langs = []

        self.dict_view.setColumnCount(2)
        self.dict_view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for i in self.cur.execute(self.request):
            self.dictionary_language_choose.addItem(i[0])

        self.request = f"SELECT russian_word, {self.dictionary_language_choose.currentText()} from words"

        self.words = self.cur.execute(self.request).fetchall()
        self.dict_view.setRowCount(len(self.words))

        for i in range(len(self.words)):
            self.dict_view.setItem(i, 0, QTableWidgetItem(self.words[i][0]))
            self.dict_view.setItem(i, 1, QTableWidgetItem(self.words[i][1]))

        self.land_add_button.clicked.connect(self.show_add_lang_form)
        self.word_add_button.clicked.connect(self.show_add_word_form)
        self.back_to_main_menu_button.clicked.connect(self.back)
        self.dictionary_language_choose.currentTextChanged.connect(self.change)

    def show_add_lang_form(self):  # вызов окна добавления языка
        self.parent.add_lang_page.show()

    def show_add_word_form(self):  # вызов окна добавления слова
        self.parent.add_word_page.show()

    def back(self):  # переход в главное меню
        self.hide()
        self.parent.show()

    def change(self):  # смена языка
        self.request = f"SELECT russian_word, {self.dictionary_language_choose.currentText()} FROM words"

        self.words = self.cur.execute(self.request).fetchall()

        self.dict_view.setRowCount(len(self.words))
        for i in range(len(self.words)):
            self.dict_view.setItem(i, 0, QTableWidgetItem(self.words[i][0]))
            self.dict_view.setItem(i, 1, QTableWidgetItem(self.words[i][1]))

    def re_init(self):
        self.request = ('SELECT * FROM langs')
        print(self.request)
        self.dict_view.setColumnCount(2)
        self.dict_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dictionary_language_choose.clear()

        self.langs = self.cur.execute(self.request).fetchall()
        for i in self.cur.execute(self.request):
            self.dictionary_language_choose.addItem(i[0])

        self.request = f"SELECT russian_word, {self.dictionary_language_choose.currentText()} from words"
        print(self.request)
        self.words = self.cur.execute(self.request).fetchall()
        self.dict_view.setRowCount(len(self.words))


        for i in range(len(self.words)):
            self.dict_view.setItem(i, 0, QTableWidgetItem(self.words[i][0]))
            self.dict_view.setItem(i, 1, QTableWidgetItem(self.words[i][1]))


class AboutWindow(QWidget, AboutForm):  # вызов справки
    def __init__(self, parent: WordTrainer):
        super().__init__()
        self.setupUi(self)
        self.parent = parent

        self.back_btn.clicked.connect(self.back)

    def back(self):  # закрытие справки
        self.parent.show()
        self.hide()


class AddLangWindow(QWidget, AddLangForm):  # окно добавления языка
    def __init__(self, parent, connection):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.connection = connection
        self.cur = self.connection.cursor()
        self.request = ''

        self.add_btn.clicked.connect(self.add)
        self.cansel_btn.clicked.connect(self.back)

    def add(self):  # сохранение языка в памяти
        self.request = f"INSERT INTO langs VALUES('{self.add_lang_edit.text()}')"
        self.cur.execute(self.request)
        print(1)
        self.request = f"ALTER TABLE words ADD {self.add_lang_edit.text()} TEXT"
        self.cur.execute(self.request)
        print(1)

        self.connection.commit()
        self.parent.dict_page.change()
        self.add_lang_edit.setText('')

        self.parent.dict_page.re_init()
        self.hide()

    def back(self):  # закрытие окна
        self.hide()


class AddWordWindow(QWidget, AddWordForm):  # окно добавления слова в язык
    def __init__(self, parent, connection):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.connection = connection
        self.cur = self.connection.cursor()
        self.request = "SELECT * FROM langs"

        for i in self.cur.execute(self.request):
            self.lang_choose.addItem(i[0])

        self.add_button.clicked.connect(self.add)
        self.cansel_button.clicked.connect(self.back)

    def add(self):  # сохранение слова
        self.request = f'INSERT INTO words(russian_word, {self.lang_choose.currentText()}) ' \
                    f'VALUES("{self.add_translation_edit.text()}", "{self.add_word_edit.text()}")'

        self.cur.execute(self.request)

        self.connection.commit()
        self.parent.dict_page.change()
        self.hide()
        self.add_translation_edit.setText('')
        self.add_word_edit.setText('')

    def back(self):  # закрытие окна
        self.hide()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    sys.excepthook = except_hook
    word_trainer = WordTrainer(app)
    word_trainer.show()

    sys.exit(app.exec())
