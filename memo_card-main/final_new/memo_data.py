from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
from random import randint, shuffle

new_quest_templ = 'Нове запитання' # такая строка будет устанавливаться по умолчанию для новых вопросов
new_answer_templ = 'Нова відповідь' # то же для ответов

text_wrong = 'Неправильно'
text_correct = 'Правильно'

class Question():
    ''' зберігає інформацію про одну відповідь'''
    def __init__(self, question=new_quest_templ, answer=new_answer_templ, 
                       wrong_answer1='', wrong_answer2='', wrong_answer3=''):
        self.question = question # вопрос
        self.answer = answer # правильный ответ
        self.wrong_answer1 = wrong_answer1 # считаем, что всегда пишется три неверных варианта
        self.wrong_answer2 = wrong_answer2 # 
        self.wrong_answer3 = wrong_answer3 #
        self.is_active = True # продолжать ли задавать этот вопрос?
        self.attempts = 0 # сколько раз этот вопрос задавался
        self.correct = 0 # количество верных ответов
    def got_right(self):
        ''' Заміняє статистику, отримав вірну відповідь'''
        self.attempts += 1
        self.correct += 1
    def got_wrong(self):
        ''' Заміняє статистику, отримав невірну відповідь'''
        self.attempts += 1

class QuestionView():
    ''' Зіставляє данні та віджети для відображення запитання'''
    def __init__(self, frm_model, question, answer, wrong_answer1, wrong_answer2, wrong_answer3):
        # конструктор получает и запоминает объект с данными и виджеты, соответствующие полям анкеты
        self.frm_model = frm_model  # может получить и None - ничего страшного не случится, 
                                    # но для метода show нужно будет предварительно обновить данные методом change
        self.question = question
        self.answer = answer
        self.wrong_answer1 = wrong_answer1
        self.wrong_answer2 = wrong_answer2
        self.wrong_answer3 = wrong_answer3  
    def change(self, frm_model):
        ''' обновлення данних, вже звязанних з інтерфейсом '''
        self.frm_model = frm_model
    def show(self):
        ''' виводить на экран всі дані з об'єкта '''
        self.question.setText(self.frm_model.question)
        self.answer.setText(self.frm_model.answer)
        self.wrong_answer1.setText(self.frm_model.wrong_answer1)
        self.wrong_answer2.setText(self.frm_model.wrong_answer2)
        self.wrong_answer3.setText(self.frm_model.wrong_answer3)

class QuestionEdit(QuestionView):
    ''' використовуюється, якщо потрібно редагувати форму: встановлює обробники подій, котрі зберігають текст  '''
    def save_question(self):
        ''' зберігає текст запитання '''
        self.frm_model.question = self.question.text() # копируем данные из виджета в объект
    def save_answer(self):
        '''зберігає текст правильної відповіді '''
        self.frm_model.answer = self.answer.text() # копируем данные из виджета в объект
    def save_wrong(self):
        ''' зберігає всі неправильні відповіді 
        (якщо в наступній версії програми кількість неправильних відповідей стане змінною
        і вони будуть вводитись у списку, можна буде поміняти цей метод) '''
        self.frm_model.wrong_answer1 = self.wrong_answer1.text()
        self.frm_model.wrong_answer2 = self.wrong_answer2.text()
        self.frm_model.wrong_answer3 = self.wrong_answer3.text()
    def set_connects(self):
        ''' встановлює обробки подій у віджетах так, щоб зберігати дані '''
        self.question.editingFinished.connect(self.save_question)
        self.answer.editingFinished.connect(self.save_answer)
        self.wrong_answer1.editingFinished.connect(self.save_wrong) 
        self.wrong_answer2.editingFinished.connect(self.save_wrong)
        self.wrong_answer3.editingFinished.connect(self.save_wrong)
    def __init__(self, frm_model, question, answer, wrong_answer1, wrong_answer2, wrong_answer3):
        # переопределим конструктор, чтобы не вызывать вручную set_connects (дети могут вызывать вручную)
        super().__init__(frm_model, question, answer, wrong_answer1, wrong_answer2, wrong_answer3)
        self.set_connects()

class AnswerCheck(QuestionView):
    ''' рахуючи, що питання анкети візуалізуються чек-боксами, перевіряє, чи правильна відповідь обрана.'''
    def __init__(self, frm_model, question, answer, wrong_answer1, wrong_answer2, wrong_answer3, showed_answer, result):
        ''' запам'ятовує всі властивості. showed_answer - це віджет, в якому записується правильна відповідь (показується пізніше)
        result - це віджет, в який буде записано txt_right або txt_wrong'''
        super().__init__(frm_model, question, answer, wrong_answer1, wrong_answer2, wrong_answer3)
        self.showed_answer = showed_answer
        self.result = result
    def check(self):
        ''' відповідь заноситься до статистики, але переключення у формі не відбувається:
        цей клас нічого не знає про панелі на формі '''
        if self.answer.isChecked():
            # ответ верный, запишем и отразим в статистике
            self.result.setText(text_correct) # надпись "верно" или "неверно"
            self.showed_answer.setText(self.frm_model.answer) # пишем сам текст ответа в соотв. виджете 
            self.frm_model.got_right() # обновить статистику, добавив один верный ответ
        else:
            # ответ неверный, запишем и отразим в статистике
            self.result.setText(text_wrong) # надпись "верно" или "неверно"
            self.showed_answer.setText(self.frm_model.answer) # пишем сам текст ответа в соотв. виджете 
            self.frm_model.got_wrong() # обновить статистику, добавив неверный ответ
            
class QuestionListModel(QAbstractListModel):
    ''' у даних знаходиться список об'єктів типу Question,
    а також список активних питань, щоб показувати його на екрані'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_list = []
    def rowCount(self, index):
        ''' кількість елементів для показу: обов'язковий метод для моделі, з якою буде пов'язаний віджет "список"'''
        return len(self.form_list)
    def data(self, index, role):
        ''' обов'язковий метод для моделі: які дані вона надає на запит від інтерфейсу'''
        if role == Qt.DisplayRole:
            # интерфейс хочет нарисовать эту строку, дадим ему текст вопроса для отображения
            form = self.form_list[index.row()]
            return form.question
    def insertRows(self, parent=QModelIndex()):
        ''' цей метод викликається, щоб вставити до списку об'єктів нові дані;
        генерується та вставляється одне порожнє питання.'''
        position = len(self.form_list) # мы вставляем в конец, это нужно сообщить следующей строкой:
        self.beginInsertRows(parent, position, position) # вставка данных должна быть после этого указания и перед endInsertRows()
        self.form_list.append(Question()) # добавили новый вопрос в список данных
        self.endInsertRows() # закончили вставку (теперь можно продолжать работать с моделью)
        QModelIndex()
        return True # сообщаем, что все прошло хорошо
    def removeRows(self, position, parent=QModelIndex()):
        ''' стандартний метод видалення рядків - після видалення з моделі рядок автоматично видаляється з екрана'''
        self.beginRemoveRows(parent, position, position) # сообщаем, что мы собираемся удалять строку - от position до position 
            # (вообще говоря, стандарт метода removeRows предлагает убирать несколько строк, но мы напишем одну)
        self.form_list.pop(position) # удаляем из списка элемент с номером position
            # в правильной реализации программы удалять вопросы со статистикой нельзя, можно их деактивировать, 
            # но это заметно усложняет модель (надо поддерживать список всех вопросов для статистики 
            # и список активных для отображения в списке редактирования)
        self.endRemoveRows() # закончили удаление (дальше библиотека сама обновляет список на экране)
        return True # все в порядке 
            # (по-хорошему нам может прийти несуществующий position,
            #  правильнее было бы писать try except и возвращать True только в действительно сработавшем случае)
    def random_question(self):
        ''' Видає випадкове запитання '''
        # тут стоит проверять, что вопрос активный...
        total = len(self.form_list)
        current = randint(0, total - 1)
        return self.form_list[current]

def random_AnswerCheck(list_model, w_question, widgets_list, w_showed_answer, w_result):
    '''повертає новий екземпляр класу AnswerCheck,
    з випадковим питанням та випадковим розкидом відповідей по віджетам'''
    frm = list_model.random_question()
    shuffle(widgets_list)
    frm_card = AnswerCheck(frm, w_question, widgets_list[0], widgets_list[1], widgets_list[2], widgets_list[3], w_showed_answer, w_result)
    return frm_card