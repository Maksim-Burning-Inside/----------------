from glob import glob
import re
import os

import win32com.client as win32
from win32com.client import constants

def save_as_docx(path):
    word = win32.gencache.EnsureDispatch('Word.Application')
    doc = word.Documents.Open(path)
    doc.Activate()

    new_file_abs = os.path.abspath(path)
    new_file_abs = re.sub('.doc', '.docx', new_file_abs)

    word.ActiveDocument.SaveAs(
        new_file_abs, FileFormat=constants.wdFormatXMLDocument
    )
    doc.Close(False)

def convert_to_docx(path):
    paths = glob(str(path), recursive=True)
    for path in paths:
        save_as_docx(path)
        os.remove(path)
        print('Преобразова формат doc в docx')