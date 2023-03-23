import sys, os
from PyQt5 import uic
from pathlib import Path
import click, glob
from PyQt5.QtWidgets import QMainWindow,QApplication
sys.path.append(str(Path(__file__).parent.parent.parent))
import library_manager.core.db_operations as db

class MyMainWindow(QMainWindow):
    def __init__(self, parent = None):
        super(MyMainWindow, self).__init__(parent)

    def init_gui(self, ui):
        #ui is a *.ui file from qt designer
        uic.loadUi(ui, self)
        self.widget_terminal.update_name_space('main_gui',self)
        self.actionDatabaseCloud.triggered.connect(lambda:db.start_mongo_client_cloud(self))
        self.pushButton_load.clicked.connect(lambda:db.load_project(self))
        self.pushButton_new_project.clicked.connect(lambda:db.new_project_dialog(self))
        self.pushButton_update_project_info.clicked.connect(lambda:db.update_project_info(self))
        self.pushButton_lend.clicked.connect(lambda:db.lend_dialog(self))
        self.pushButton_return.clicked.connect(lambda:db.return_dialog(self))
        self.pushButton_new.clicked.connect(lambda:db.add_paper_info(self))
        self.pushButton_update.clicked.connect(lambda:db.update_paper_info(self))
        self.pushButton_remove.clicked.connect(lambda:db.delete_one_paper(self))
        self.pushButton_search.clicked.connect(lambda:db.query_by_field(self,self.comboBox_search_field.currentText(),self.lineEdit_search_item.text()))
        self.comboBox_books.activated.connect(lambda:db.extract_paper_info(self))

@click.command()
@click.option('--ui', default='library_manager.ui',help="main gui ui file generated from Qt Desinger, possible ui files are :")
@click.option('--ss', default ='Takezo.qss', help='style sheet file *.qss, possible qss files include: ')
@click.option('--tm', default = 'False', help='show terminal widget (--tm True) or not (--tm False)')
def main(ui, ss, tm):
    ui_file = str(Path(__file__).parent.parent/ "ui" / ui)
    QApplication.setStyle("fusion")
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.init_gui(ui_file)
    if tm=='False':
        myWin.widget_terminal.hide()
        myWin.label_3.hide()
    elif tm=='True':
        pass
    myWin.setWindowTitle('图书管理系统')
    style_sheet_path = str(Path(__file__).parent.parent/ "resources" / "stylesheets" / ss)
    File = open(style_sheet_path,'r')
    with File:
        qss = File.read()
        app.setStyleSheet(qss)    
    myWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    