import os, datetime
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from pathlib import Path
from pymongo import MongoClient
import certifi
from ..core.util import error_pop_up
ui_path = str(Path(__file__).parent.parent/ "ui")

class NewProject(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the dialog's GUI
        uic.loadUi(os.path.join(ui_path,"new_project_dialog.ui"), self)
        self.pushButton_ok.clicked.connect(lambda:self._creat_a_new_project( parent = parent,
                                                                            name_db = self.lineEdit_name.text(), 
                                                                            db_info = self.textEdit_introduction.toPlainText(),
                                                                            type_db ='paper'))
        self.pushButton_cancel.clicked.connect(lambda:self.close())

    def _creat_a_new_project(self,parent, name_db, db_info,type_db ='paper'):
        parent.database = parent.mongo_client[name_db]
        if type_db == 'paper':
            parent.database.project_info.insert_many([{'project_info':db_info}])
        parent.comboBox_project_list.clear()
        parent.comboBox_project_list.addItems(parent.mongo_client.list_database_names())
        parent.comboBox_project_list.setCurrentText(name_db)
        #extract project info
        all = parent.database.project_info.find()
        parent.plainTextEdit_project_info.setPlainText('\n'.join([each['project_info'] for each in all]))

class LendDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the dialog's GUI
        uic.loadUi(os.path.join(ui_path,"lend_book_dialogue.ui"), self)
        self.lineEdit_book_name.setText(parent.lineEdit_book_name.text())
        self.pushButton_lend.clicked.connect(lambda:self.lend(parent))

    def lend(self, parent):
        parent.lineEdit_borrower.setText(self.lineEdit_borrower.text())
        parent.lineEdit_status.setText('借出')
        parent.lineEdit_lend_date.setText(datetime.datetime.today().strftime('%Y-%m-%d'))
        parent.pushButton_update.click()
        parent.statusbar.clearMessage()
        parent.statusbar.showMessage('The book is lent to {} successfully:-)'.format(self.lineEdit_borrower.text()))
        self.close()

class LoginDialog(QDialog):
    def __init__(self, parent=None, url=''):
        super().__init__(parent)
        # Load the dialog's GUI
        uic.loadUi(os.path.join(ui_path,"login_dialogue.ui"), self)
        self.pushButton_login.clicked.connect(lambda:self.login(parent, url))

    def login(self, parent, url):
        url_complete = url.format(self.lineEdit_login_name.text(),self.lineEdit_password.text())
        try:
            client = MongoClient(url_complete,tlsCAFile=certifi.where())
            parent.mongo_client = client
            parent.comboBox_project_list.clear()
            parent.comboBox_project_list.addItems(parent.mongo_client.list_database_names())
            self.close()
        except:
            error_pop_up('login info is incorrect. Try again!')

class ReturnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the dialog's GUI
        uic.loadUi(os.path.join(ui_path,"return_book_dialogue.ui"), self)
        self.lineEdit_book_name.setText(parent.lineEdit_book_name.text())
        self.lineEdit_borrower.setText(parent.lineEdit_borrower.text())
        self.pushButton_return.clicked.connect(lambda:self.return_(parent))

    def return_(self, parent):
        #parent.lineEdit_borrower.setText(self.lineEdit_borrower.text())
        parent.lineEdit_status.setText('在馆')
        parent.lineEdit_return_date.setText(datetime.datetime.today().strftime('%Y-%m-%d'))
        parent.pushButton_update.click()
        parent.statusbar.clearMessage()
        parent.statusbar.showMessage('The book is returned by {} successfully:-)'.format(self.lineEdit_borrower.text()))
        self.close()

class QueryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # Load the dialog's GUI
        uic.loadUi(os.path.join(ui,"query_dialog.ui"), self)
        self.pushButton_clear.clicked.connect(self.clear_fields)
        self.pushButton_search.clicked.connect(self.search)
        self.pushButton_exit.clicked.connect(lambda:self.close())
    
    def clear_fields(self):
        self.lineEdit_title.setText('')
        self.lineEdit_abstract.setText('')
        self.lineEdit_author.setText('')
        self.lineEdit_journal.setText('')
        self.lineEdit_year.setText('')

    def search(self):
        self.parent.query_string_title = self.lineEdit_title.text()
        self.parent.query_string_abstract = self.lineEdit_abstract.text()
        self.parent.query_string_author = self.lineEdit_author.text()
        self.parent.query_string_journal = self.lineEdit_journal.text()
        self.parent.query_string_year = self.lineEdit_year.text()

        self.parent.query_opt_title = self.comboBox_title.currentText()
        self.parent.query_opt_abstract = self.comboBox_abstract.currentText()
        self.parent.query_opt_author = self.comboBox_author.currentText()
        self.parent.query_opt_journal = self.comboBox_journal.currentText()
        self.parent.query_opt_year = self.comboBox_year.currentText()

        self.parent.database.paper_info.drop_indexes()

        paper_ids = self.parent.query_info()
        text_box = []

        #self.textEdit_query_info.setText('\n'.join(self.parent.query_info()))
        for each in paper_ids:
            text_box.append(each)
            #extract paper info
            text_box.append('##paper_info##')
            target = self.parent.database.paper_info.find_one({'paper_id':each})
            keys = ['full_authors','journal','year','title','url','doi','abstract']
            for each_key in keys:
                text_box.append('{}:  {}'.format('  '+each_key,target[each_key]))
            text_box.append('\n')
        self.textEdit_query_info.setText('\n'.join(text_box))