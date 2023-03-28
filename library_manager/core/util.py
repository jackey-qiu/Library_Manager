from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QMenu
import base64
import bcrypt

def encrypt_password(password, encode = 'utf-8'):
    password = password.encode(encode)
    salt = bcrypt.gensalt(10)
    return bcrypt.hashpw(password, salt)

def confirm_password(password,encrypted_password, encode = 'utf-8'):
    return bcrypt.checkpw(str(password).encode(encode), encrypted_password)

def error_pop_up(msg_text = 'error', window_title = ['Error','Information','Warning'][0]):
    msg = QMessageBox()
    if window_title == 'Error':
        msg.setIcon(QMessageBox.Critical)
    elif window_title == 'Warning':
        msg.setIcon(QMessageBox.Warning)
    else:
        msg.setIcon(QMessageBox.Information)

    msg.setText(msg_text)
    # msg.setInformativeText('More information')
    msg.setWindowTitle(window_title)
    msg.exec_()

def map_chinese_to_eng_key(str_ch):
    map_ = {'书名':'book_name',
            '作者':'author',
            '编号':'paper_id',
            '状态':'status',
            '类别':'class',
            }
    if str_ch in map_:
        return map_[str_ch]
    else:
        return 'UNKNOWN'

def image_to_64base_string(image_path):
    with open(image_path, "rb") as img_file:
         my_string = base64.b64encode(img_file.read())
    return my_string

def image_string_to_qimage(my_string, img_format = 'PNG'):
    QByteArr = QtCore.QByteArray.fromBase64(my_string)
    QImage = QtGui.QImage()
    QImage.loadFromData(QByteArr, img_format)
    return QImage

class PandasModel(QtCore.QAbstractTableModel):
    """
    Class to populate a table view with a pandas dataframe
    """
    def __init__(self, data, tableviewer, main_gui, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        self.tableviewer = tableviewer
        self.main_gui = main_gui

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role):
        if index.isValid():
            if role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole] and index.column()!=0:
                return str(self._data.iloc[index.row(), index.column()])
            #if role == QtCore.Qt.BackgroundRole and index.row()%2 == 0:
                # return QtGui.QColor('green')
                # return QtGui.QColor('DeepSkyBlue')
                #return QtGui.QColor('Blue')
            # if role == QtCore.Qt.BackgroundRole and index.row()%2 == 1:
            if role == QtCore.Qt.BackgroundRole:
                return QtGui.QColor('white')
                # return QtGui.QColor('aqua')
                # return QtGui.QColor('lightGreen')
            # if role == QtCore.Qt.ForegroundRole and index.row()%2 == 1:
            if role == QtCore.Qt.ForegroundRole:
                return QtGui.QColor('black')
            if role == QtCore.Qt.CheckStateRole and index.column()==0:
                if self._data.iloc[index.row(),index.column()]:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        return None

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            if value == QtCore.Qt.Checked:
                self._data.iloc[index.row(),index.column()] = True
            else:
                self._data.iloc[index.row(),index.column()] = False
        else:
            if str(value)!='':
                self._data.iloc[index.row(),index.column()] = str(value)
        # if self._data.columns.tolist()[index.column()] in ['select','archive_date','user_label','read_level']:
            # self.update_meta_info_paper(paper_id = self._data['paper_id'][index.row()])
        self.dataChanged.emit(index, index)
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()
        self.tableviewer.resizeColumnsToContents() 
        # self.tableviewer.horizontalHeader().setStretchLastSection(True)
        return True
    
    def update_view(self):
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def headerData(self, rowcol, orientation, role):
        map_chinese_words = {'select':'选择','paper_id':'编号','year':'年份','press':'出版社','archive_date':'入库时间','book_name':'书名','class':'类别','status':'状态','note':'备注'}
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            tag = self._data.columns[rowcol]         
            if tag in map_chinese_words:
                return map_chinese_words[tag]
            else:
                return tag
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[rowcol]         
        return None

    def flags(self, index):
        if not index.isValid():
           return QtCore.Qt.NoItemFlags
        else:
            if index.column()==0:
                return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)
            else:
                return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def sort(self, Ncol, order):
        """Sort table by given column number."""
        self.layoutAboutToBeChanged.emit()
        self._data = self._data.sort_values(self._data.columns.tolist()[Ncol],
                                        ascending=order == QtCore.Qt.AscendingOrder, ignore_index = True)
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()