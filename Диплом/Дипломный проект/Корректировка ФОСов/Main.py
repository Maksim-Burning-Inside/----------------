import pathlib
from pathlib import Path
from ConvertToDOCX import convert_to_docx
from DeleteWrongFOS import delete_wrong_file
from NamesCorrects import correct_files_names

path = Path(pathlib.Path.cwd(), 'ФОСы')
path_type = Path(pathlib.Path.cwd(), 'ФОСы', '*.doc')

delete_wrong_file(path)
convert_to_docx(path_type)
correct_files_names(path)