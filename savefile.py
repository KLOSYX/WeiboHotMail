import time
import os


def chek_folder(class_name):
    now = time.strftime('%Y%m%d', time.localtime())
    path = f'./{class_name}/{now}'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def save_file(class_name, file_name, data):
    assert data is not None and file_name is not None, 'Data error'
    path = chek_folder(class_name)
    out_file = path + '\\' + file_name
    with open(out_file, 'a+', encoding='utf-8') as of:
        for item in data:
            for element in item[:-1]:
                of.write(element + ',')
            of.write(item[-1] + '\n')
