import os
import textract

def correct_files_names(path):
    listdir = os.listdir(path)

    for file in listdir:
        if '.doc' in file or '.docx' in file:
            path_file = os.path.join(path, file)
            try:
                text = textract.process(path_file)
                text = text.decode('utf-8').strip()
                text = text[:2500]
            except:
                continue

            name_fos = text[text.find('«', text.find('«') + 1) + 1:text.find('»', text.find('»') + 1)]
            name_fos = name_fos.replace('\n', '')
            name_fos = name_fos.replace('\t', '')

            success = False
            number = 1
            while not success:
                if '.docx' in file:
                    new_name = name_fos + ' ' + str(number) + '.docx'
                else:
                    new_name = name_fos + ' ' + str(number) + '.doc'
                path_new_name_file = os.path.join(path, new_name)

                try:
                    if number > 1000:
                        success = True

                    os.rename(path_file, path_new_name_file)
                    number = 1
                    success = True
                    print('Файл успешно переименован: ', new_name)
                except:
                    number += 1