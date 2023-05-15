import os
import textract

def delete_wrong_file(path):
    listdir = os.listdir(path)
    wrong_files = 0
    incorrect_files = 0

    for file in listdir:
        if '.doc' in file or '.docx' in file:
            path_file = os.path.join(path, file)
            try:
                text = textract.process(path_file)
                text = text.decode('utf-8').strip()
                text = text.lower()
                if text.find('блок d') >= 0:
                    continue
                else:
                    incorrect_files += 1
                    print('Удалён не ФОС', file)
                    os.remove(path_file)
            except:
                wrong_files += 1
                print('Удалён повреждённый файл', file)
                os.remove(path_file)

    print('Повреждённых файлов:', wrong_files)
    print('Не ФОС-файлов:', incorrect_files)