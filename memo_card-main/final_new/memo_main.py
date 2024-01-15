from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget

from memo_app import app
from memo_data import *
from memo_main_layout import *
from memo_card_layout import *
from memo_edit_layout import txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2, txt_Wrong3

######################################              Константы:              #############################################
main_width, main_height = 1000, 450 # начальные размеры главного окна
card_width, card_height = 600, 500 # начальные размеры окна "карточка"
time_unit = 1000    # столько длится одна единица времени из тех, на которые нужно засыпать 
                    # (в рабочей версии программы увеличить в 60 раз!)

######################################          Глобальные переменные:      #############################################
questions_listmodel = QuestionListModel() # список вопросов
frm_edit = QuestionEdit(0, txt_Question, txt_Answer, txt_Wrong1, txt_Wrong2, txt_Wrong3) # запоминаем, что в форме редактирования вопроса с чем связано
radio_list = [rbtn_1, rbtn_2, rbtn_3, rbtn_4] # список виджетов, который надо перемешивать (для случайного размещения ответов)
frm_card = 0 # здесь будет связываться вопрос с формой теста
timer = QTimer() # таймер для возможности "уснуть" на время и проснуться
win_card = QWidget() # окно карточки
win_main = QWidget() # окно редактирования вопросов, основное в программе

######################################             Тестовые данные:         #############################################
def testlist():
    
    frm = Question('Яблуко', 'apple', 'application', 'pinapple', 'apply')
    questions_listmodel.form_list.append(frm)
    frm = Question('Дім', 'house', 'horse', 'hurry', 'hour')
    questions_listmodel.form_list.append(frm)
    frm = Question('Миша', 'mouse', 'mouth', 'muse', 'museum')
    questions_listmodel.form_list.append(frm)
    frm = Question('Число', 'number', 'digit', 'amount', 'summary')
    questions_listmodel.form_list.append(frm)

######################################     Функции для проведения теста:    #############################################

def set_card():
    ''' задає, як виглядає вікно карточки'''
    win_card.resize(card_width, card_height)
    win_card.move(300, 300)
    win_card.setWindowTitle('Memory Card')
    win_card.setLayout(layout_card)

def sleep_card():
    ''' карточка ховається на деякий час, вказанний в таймері'''
    win_card.hide()
    timer.setInterval(time_unit * box_Minutes.value() )
    timer.start()

def show_card():
    ''' показує вікно (по таймеру), таймер зупиняється'''
    win_card.show()
    timer.stop()

def show_random():
    ''' показати випадкове питання '''
    global frm_card # как бы свойство окна - текущая форма с данными карточки
    # получаем случайные данные, и случайно же распределяем варианты ответов по радиокнопкам:
    frm_card = random_AnswerCheck(questions_listmodel, lb_Question, radio_list, lb_Correct, lb_Result)
    # мы будем запускать функцию, когда окно уже есть. Так что показываем:
    frm_card.show() # загрузить нужные данные в соответствующие виджеты 
    show_question() # показать на форме панель вопросовq

def click_OK():
    ''' перевіряє запитаня чи завантажує нове питання '''
    if btn_OK.text() != 'наступне питання':
        frm_card.check()
        show_result()
    else:
        # надпись на кнопке равна 'Следующий', вот и создаем следующий случайный вопрос:
        show_random()

def back_to_menu():
    ''' повернення з тесту до вікно редактора '''
    win_card.hide()
    win_main.showNormal()

######################################     Функции для редактирования вопросов:    ######################################
def set_main():
    ''' задає, як виглядає основне вікно'''
    win_main.resize(main_width, main_height)
    win_main.move(100, 100)
    win_main.setWindowTitle('Список запитань')
    win_main.setLayout(layout_main)

def edit_question(index):
    ''' завантажує у форму редагування питання та відповіді, що відповідають переданому рядку '''
    #  index - это объект класса QModelIndex, см. нужные методы ниже 
    if index.isValid():
        i = index.row()
        frm = questions_listmodel.form_list[i]
        frm_edit.change(frm)
        frm_edit.show()

def add_form():
    ''' додає нове запитання та пропонує його змінити '''
    questions_listmodel.insertRows() # Новый вопрос появился в данных и автоматически в списке на экране
    last = questions_listmodel.rowCount(0) - 1   # Новый вопрос - последний в списке. Найдем его позицию. 
                                                # В rowCount передаём 0, чтобы соответствовать требованиям функции:
                                                # этот параметр все равно не используется, но 
                                                # нужен по стандарту библиотеки (метод с параметром index вызывается при отрисовке списка)    
    index = questions_listmodel.index(last) # получаем объект класса QModelIndex, который соответствует последнему элементу в данных 
    list_questions.setCurrentIndex(index) # делаем соответствующую строку списка на экране текущей
    edit_question(index)    # этот вопрос надо подгрузить в форму редактирования
                            # клика мышкой у нас тут нет, вызовем нужную функцию из программы
    txt_Question.setFocus(Qt.TabFocusReason) # переводим фокус на поле редактирования вопроса, чтобы сразу убирались "болванки"
                                             # Qt.TabFocusReason переводит фокус так, как если бы была нажата клавиша "tab" 
                                             # это удобно тем, что выделяет "болванку", её легко сразу убрать 

def del_form():
    ''' видаляє запитання та перемикає фокус '''
    questions_listmodel.removeRows(list_questions.currentIndex().row())
    edit_question(list_questions.currentIndex())

def start_test():
    ''' на початку тесту форма зв'язується з випадковим питанням і показується'''
    show_random()
    win_card.show()
    win_main.showMinimized()

######################################      Установка нужных соединений:    #############################################
def connects():
    list_questions.setModel(questions_listmodel) # связать список на экране со списком вопросов
    list_questions.clicked.connect(edit_question) # при нажатии на элемент списка будет открываться для редактирования нужный вопрос
    btn_add.clicked.connect(add_form) # соединили нажатие кнопки "новый вопрос" с функцией добавления
    btn_delete.clicked.connect(del_form) # соединили нажатие кнопки "удалить вопрос" с функцией удаления
    btn_start.clicked.connect(start_test) # нажатие кнопки "начать тест" 
    btn_OK.clicked.connect(click_OK) # нажатие кнопки "OK" на форме теста
    btn_Menu.clicked.connect(back_to_menu) # нажатие кнопки "Меню" для возврата из формы теста в редактор вопросов
    timer.timeout.connect(show_card) # показываем форму теста по истечении таймера
    btn_Sleep.clicked.connect(sleep_card) # нажатие кнопки "спать" у карточки-теста

######################################            Запуск программы:         #############################################
# Основной алгоритм иногда оформляют в функцию, которая запускается, только если код выполняется из этого файла,
# а не при подключении как модуль. Детям это совершенно не нужно.
testlist()
set_card()
set_main()
connects()
win_main.show()
app.exec_()