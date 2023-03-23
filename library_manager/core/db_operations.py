from .util import error_pop_up, PandasModel, map_chinese_to_eng_key
from ..widgets.dialogues import NewProject, QueryDialog, LendDialog, ReturnDialog, LoginDialog

from dotenv import load_dotenv
from pathlib import Path
import os, certifi, datetime
from pymongo import MongoClient
from PyQt5.QtWidgets import QMessageBox
from pathlib import Path
import PyQt5
import pandas as pd

def start_mongo_client_cloud(self):
    try:
        if not os.path.exists(str(Path(__file__).parent.parent/ "resources" / "private" / "atlas_password.dot")):
            error_pop_up('You should create a file named atlas_password under Library_Manager/resources/private folder, \
                            where you save the atlas url link for your MongoDB atlas cloud account. \
                            please use the format ATLAS_URL="URL LINK"')
        else:
            env = load_dotenv(str(Path(__file__).parent.parent/ "resources" / "private" / "atlas_password.dot"))
            if env:
                url = os.getenv('ATLAS_URL') 
                login_dialog(self, url)
                #self.mongo_client = MongoClient(url,tlsCAFile=certifi.where())
            else:
                url = ''
                print('something is wrong')
    except Exception as e:
        error_pop_up('Fail to start mongo client.'+'\n{}'.format(str(e)),'Error')

def extract_project_info(self):
    all = self.database.project_info.find()
    self.plainTextEdit_project_info.setPlainText('\n'.join([each['project_info'] for each in all]))

def load_project(self):
    self.database = self.mongo_client[self.comboBox_project_list.currentText()]
    extract_project_info(self)
    #self.update_paper_list_in_listwidget()
    init_pandas_model_from_db(self)
    update_paper_list_in_combobox(self)
    extract_paper_info(self)

def update_project_info(self):
    try:
        self.database.project_info.drop()
        self.database.project_info.insert_many([{'project_info':self.plainTextEdit_project_info.toPlainText()}])
        error_pop_up('Project information has been updated successfully!','Information')
    except Exception as e:
        error_pop_up('Failure to update Project information!','Error')

def new_project_dialog(self):
    dlg = NewProject(self)
    dlg.exec()

def lend_dialog(self):
    dlg = LendDialog(self)
    dlg.exec()

def login_dialog(self, url):
    dlg = LoginDialog(self, url)
    dlg.exec()

def return_dialog(self):
    dlg = ReturnDialog(self)
    dlg.exec()

def update_paper_list_in_combobox(self):
    papers = get_papers_in_a_list(self)
    self.comboBox_books.clear()
    self.comboBox_books.addItems(papers)

def get_papers_in_a_list(self):
    all_info = list(self.database.paper_info.find({},{'_id':0}))
    paper_id_list = [each['paper_id'] for each in all_info]
    return sorted(paper_id_list)

def init_pandas_model_from_db(self):
    data = {'select':[],'paper_id':[],'book_name':[],'year':[],'class':[],'press':[],'archive_date':[],'status':[],'note':[]}
    for each in self.database.paper_info.find():
        data['select'].append(each.get('select','True'))
        data['paper_id'].append(each['paper_id'])
        data['book_name'].append(each['book_name'])
        # data['title'].append(each['title'])
        data['year'].append(each['year'])
        data['class'].append(each['class'])
        data['press'].append(each.get('press','no input'))
        data['archive_date'].append(each.get('archive_date','2023-03-23'))
        data['status'].append(each.get('status','no input'))
        data['note'].append(each.get('note','no input'))
    data = pd.DataFrame(data)
    data['select'] = data['select'].astype(bool)
    self.pandas_model_paper_info = PandasModel(data = data, tableviewer = self.tableView_book_info, main_gui = self)
    self.tableView_book_info.setModel(self.pandas_model_paper_info)
    self.tableView_book_info.resizeColumnsToContents()
    self.tableView_book_info.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)

def update_project_info(self):
    try:
        self.database.project_info.drop()
        self.database.project_info.insert_many([{'project_info':self.plainTextEdit_project_info.toPlainText()}])
        error_pop_up('Project information has been updated successfully!','Information')
    except Exception as e:
        error_pop_up('Failure to update Project information!','Error')

def extract_paper_info(self):
    paper_id = self.comboBox_books.currentText()
    target = self.database.paper_info.find_one({'paper_id':paper_id})
    #set the pdf block to '' first
    paper_info = {'book_name':self.lineEdit_book_name.setText,
                    'author':self.lineEdit_author.setText,
                    'press':self.lineEdit_press.setText,
                    'year':self.lineEdit_year.setText,
                    'class':self.lineEdit_class.setText,
                    'paper_id':self.lineEdit_id.setText,
                    'status':self.lineEdit_status.setText,
                    'borrower':self.lineEdit_borrower.setText,
                    'lend_date':self.lineEdit_lend_date.setText,
                    'return_date':self.lineEdit_return_date.setText,
                    'note':self.lineEdit_note.setText,
                    'abstract':self.textEdit_abstract.setHtml,
                    }    
    for key, item in paper_info.items():
        if key in target:
            if key == 'abstract':
                format_ = '<p style="color:gold;margin-left:20px;">{}</p>'.format
                item(format_(target[key]))
            else:
                item(target[key])
        else:
            if key == 'graphical_abstract':
                pass
            else:
                item('')

def delete_one_paper(self):
    paper_id = self.comboBox_books.currentText()
    reply = QMessageBox.question(self, 'Message', 'Are you sure to delete this paper?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
    if reply == QMessageBox.Yes:
        try:
            for collection in self.database.list_collection_names():
                self.database[collection].delete_many({'paper_id':paper_id})
            self.statusbar.clearMessage()
            self.statusbar.showMessage('The book is deleted from DB successfully:-)')
            # self.update_paper_list_in_listwidget()
            update_paper_list_in_combobox(self)
            init_pandas_model_from_db(self)
            extract_paper_info(self)
        except:
            error_pop_up('Fail to delete the paper info!','Error')

def update_paper_info(self):
    paper_id = self.comboBox_books.currentText()
    original = self.database.paper_info.find_one({'paper_id':paper_id})
    paper_info_new = {'book_name':self.lineEdit_book_name.text(),
                    'author':self.lineEdit_author.text(),
                    'press':self.lineEdit_press.text(),
                    'year':self.lineEdit_year.text(),
                    'class':self.lineEdit_class.text(),
                    'paper_id':paper_id,
                    'status':self.lineEdit_status.text(),
                    'borrower':self.lineEdit_borrower.text(),
                    'lend_date':self.lineEdit_lend_date.text(),
                    'return_date':self.lineEdit_return_date.text(),
                    'note':self.lineEdit_note.text(),
                    'abstract':self.textEdit_abstract.toPlainText().replace('\n',' '),
                    }    
    paper_info_new['select'] = original['select']
    paper_info_new['archive_date'] = original['archive_date']
    try:        
        reply = QMessageBox.question(self, 'Message', 'Would you like to update your database with new input?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.database.paper_info.replace_one(original,paper_info_new)
            #self.update_paper_list_in_listwidget()
            init_pandas_model_from_db(self)
        self.statusbar.clearMessage()
        self.statusbar.showMessage('Update the paper info successfully:-)')
    except Exception as e:
        error_pop_up('Fail to update the paper info :-(\n{}'.format(str(e)),'Error')     

#create a new paper record in database
def add_paper_info(self, parser = None):
    paper_info = {'book_name':self.lineEdit_book_name.text(),
                    'author':self.lineEdit_author.text(),
                    'press':self.lineEdit_press.text(),
                    'year':self.lineEdit_year.text(),
                    'class':self.lineEdit_class.text(),
                    'paper_id':self.lineEdit_id.text(),
                    'status':self.lineEdit_status.text(),
                    'borrower':self.lineEdit_borrower.text(),
                    'lend_date':self.lineEdit_lend_date.text(),
                    'return_date':self.lineEdit_return_date.text(),
                    'note':self.lineEdit_note.text(),
                    'abstract':self.textEdit_abstract.toPlainText().replace('\n',' '),
                    }
    if parser!=None:
        paper_info = parser
    papers = get_papers_in_a_list(self)
    if paper_info['paper_id'] in papers:
        error_pop_up('The paper id is already used. Please choose a different one.')
        return
    paper_info['select'] = False
    paper_info['archive_date'] = datetime.datetime.today().strftime('%Y-%m-%d')

    # if os.path.exists(self.lineEdit_pdf.text()):
        # self.file_worker.insertFile(filePath = self.lineEdit_pdf.text(),paper_id = paper_id_temp)
    try:
        self.database.paper_info.insert_one(paper_info)
        self.statusbar.clearMessage()
        self.statusbar.showMessage('Append the paper info sucessfully!')
        #self.update_paper_list_in_listwidget()
        init_pandas_model_from_db(self)
        update_paper_list_in_combobox(self)
        self.comboBox_books.setCurrentText(paper_info['paper_id'])
    except Exception as e:
        error_pop_up('Failure to append paper info!\n{}'.format(str(e)),'Error')              

def query_by_field(self, field, query_string):
    """[return the paper_ids according the query_string w.r.t the specified field]

    Args:
        field ([string]): in ['author','book_name','book_id','status','class']
        query_string ([string]): [the query string you want to perform, e.g. 1999 for field = 'year']

    Returns:
        [list]: [paper_id list]
    """
    field = map_chinese_to_eng_key(field)
    if field == 'UNKNOWN':
        error_pop_up('unknown field')
        return
    index_name = self.database.paper_info.create_index([(field,'text')])
    targets = self.database.paper_info.find({"$text": {"$search": "\"{}\"".format(query_string)}})
    #drop the index afterwards
    return_list = [each['paper_id'] for each in targets]
    self.database.paper_info.drop_index(index_name)
    # print(field, return_list)
    if len(return_list)!=0:
        self.comboBox_books.setCurrentText(return_list[0])
        extract_paper_info(self)
    else:
        error_pop_up('Nothing return')