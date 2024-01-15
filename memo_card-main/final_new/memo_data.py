from PyQt5.QtCore import QAbstractListModel, QModelIndex, Qt
from random import randint, shuffle

new_quest_templ = 'Нове запитання' # такий рядок буде встановлюватись за умовчанням для нових питань
new_answer_templ = 'Нова відповідь' # те ж для відповідей

text_wrong = 'Неправильно'
text_correct = 'Правильно'

class Question():
    ''' зберігає інформацію про одну відповідь'''
    def __init__(self, question=new_quest_templ, answer=new_answer_templ, 
                       wrong_answer1='', wrong_answer2='', wrong_answer3=''):
        self.question = question # запитання
        self.answer = answer # правильна відповідь
        self.wrong_answer1 = wrong_answer1 # 
        self.wrong_answer2 = wrong_answer2 # 
        self.wrong_answer3 = wrong_answer3 #
        self.is_active = True # продовжувати задавати це питання?
        self.attempts = 0 # скільки разів ставилося це питання
        self.correct = 0 # кількість вірних відповідей
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
        # конструктор отримує та запам'ятовує об'єкт з даними та віджети, що відповідають полям анкети
        self.frm_model = frm_model  # може отримати і None - нічого страшного не станеться,
                                    # але для методу show потрібно буде попередньо оновити дані методом change
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
        self.frm_model.question = self.question.text() # копіюємо дані з віджету в об'єкт
    def save_answer(self):
        '''зберігає текст правильної відповіді '''
        self.frm_model.answer = self.answer.text() # копіюємо дані з віджету в об'єкт
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
        # перевизначимо конструктор, щоб не викликати вручну set_connects (діти можуть викликати вручну)
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
            # відповідь вірна, запишемо і відобразимо в статистиці
            self.result.setText(text_correct) # напис "правильно", чи "неправильно"
            self.showed_answer.setText(self.frm_model.answer) # пишемо сам текст відповіді в відповідності. віджету
            self.frm_model.got_right() # оновити статистику, додавши одну правильну відповідь
        else:
            # відповідь невірна, запишемо і відобразимо у статистиці
            self.result.setText(text_wrong) # напис "правильно" або "неправильно"
            self.showed_answer.setText(self.frm_model.answer) # пишемо сам текст відповіді в відповідності. віджету
            self.frm_model.got_wrong() # оновити статистику, добавивши неправильну відповідь
            
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
            # інтерфейс хоче намалювати цей рядок, дамо йому текст питання для відображення

            form = self.form_list[index.row()]
            return form.question
    def insertRows(self, parent=QModelIndex()):
        ''' цей метод викликається, щоб вставити до списку об'єктів нові дані;
        генерується та вставляється одне порожнє питання.'''
        position = len(self.form_list) # ми вставляємо в кінець, це потрібно повідомити наступним рядком:
        self.beginInsertRows(parent, position, position) # вставка даних повинна бути після цієї вказівки і перед endInsertRows()
        self.form_list.append(Question()) # добавили нове запитання в список даних
        self.endInsertRows() # закінчили вставку (тепер можна продовжувати працювати з моделлю)
        QModelIndex()
        return True # повідомляємо, що все прошло хорошо
    def removeRows(self, position, parent=QModelIndex()):
        ''' стандартний метод видалення рядків - після видалення з моделі рядок автоматично видаляється з екрана'''
        self.beginRemoveRows(parent, position, position) # повідомляємо, що ми збираємося видаляти рядок - від position до position
            # (взагалі кажучи, стандарт методу removeRows пропонує прибирати кілька рядків, але ми напишемо один)
        self.form_list.pop(position) # видаляємо зі списку елемент із номером position
            # у правильній реалізації програми видаляти питання зі статистикою не можна, можна їх деактивувати,
            # але це помітно ускладнює модель (треба підтримувати список усіх питань для статистики.
            # та список активних для відображення у списку редагування)
        self.endRemoveRows() # закончили удаление (дальше библиотека сама обновляет список на экране)
        return True # все добре
            # (по доброму нам може прийти неіснуючий position,
            # правильніше було б писати try except і повертати True тільки в дійсно спрацював випадку)
    def random_question(self):
        ''' Видає випадкове запитання '''
        #тут варто перевіряти, що питання активне...
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