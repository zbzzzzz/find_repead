'''pass'''
import os
import shutil
import hashlib
import sqlite3
import time
import pyautogui
import datetime
import configparser

def fastmd5(file_path,split_piece=256,get_front_bytes=8):
    """
    快速计算一个用于区分文件的md5（非全文件计算，是将文件分成s段后，取每段前d字节，合并后计算md5，以加快计算速度）

    Args:
        file_path: 文件路径
        split_piece: 分割块数
        get_front_bytes: 每块取前多少字节
    """
    size = os.path.getsize(file_path) # 取文件大小
    block = size//split_piece # 每块大小 
    h = hashlib.md5()
    # 计算md5
    if size < split_piece*get_front_bytes: 
        # 小于能分割提取大小的直接计算整个文件md5
        with open(file_path, 'rb') as f:
            h.update(f.read())
    else:
        # 否则分割计算
        with open(file_path, 'rb') as f:
            index = 0
            for i in range(split_piece):
                f.seek(index)
                h.update(f.read(get_front_bytes))
                index+=block
    return h.hexdigest()

def get_time():
    ''''''
    now = datetime.datetime.now()  #获取当前时间
    return f'{now.strftime("%Y-%m-%d")} {now.hour}:{now.minute}:{now.second}'


# # 计算每张图像的md5值
# def compute_md5(image_path):
#     '''pass'''
#     img = open(image_path, 'rb')
#     md5 = hashlib.md5(img.read())
#     img.close()
#     md5_values = md5.hexdigest()
#     return md5_values
def save_md5():
    ''''''
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '..','qb.ini'))
    download_path = config['config']['download_path']
    path_list = download_path + '_done'
    # path_list = input('input path:')
    duplicate_path = os.path.join(os.path.dirname(download_path), 'Duplicate')
    os.makedirs(duplicate_path, exist_ok=True)
    connect, cursor = init_db_table()
    move_img_names = []
    # print('running...')
    for fold_path in path_list:
        for root, directories, files in os.walk(fold_path):
            for image_name in files:
                if image_name.endswith('.!qB') or image_name.endswith('.bc!'):
                    image_path = os.path.join(root, image_name)
                    if image_name in move_img_names:
                        new_path = os.path.join(duplicate_path, str(time.time()) + '_' + image_name)
                    else:
                        new_path = os.path.join(duplicate_path, image_name)
                        move_img_names.append(image_name)
                    shutil.move(image_path, new_path)
                else:
                    print(f'{image_name}  {get_time()}')
                    # if image_name.upper().endswith(('.MP4', '.FLV')):
                    image_path = os.path.join(root, image_name)
                    md5 = fastmd5(image_path)
                    cursor.execute(f"SELECT md5 FROM vedio WHERE md5='{md5}';")
                    md5_result = cursor.fetchone()
                    if md5_result:
                        if image_name in move_img_names:
                            new_path = os.path.join(duplicate_path, str(time.time()) + '_' + image_name)
                        else:
                            new_path = os.path.join(duplicate_path, image_name)
                            move_img_names.append(image_name)
                        shutil.move(image_path, new_path)
                        # shutil.copy(image_path, new_path)
                        # with open(r'E:\duplicate\underage\repeat.txt', 'a') as repeat_file:
                        #     cursor.execute(f"SELECT name FROM vedio WHERE md5='{md5}';")
                        #     same_file_name = cursor.fetchone()
                        #     repeat_file.write(f'origin_path:{image_path}\nnew_path:{new_path}\nsame_file_name:{same_file_name}\n\n')
                    else:
                        try:    
                            cursor.execute("INSERT INTO vedio (md5, name) VALUES (?, ?);",(md5, image_name))
                        except Exception as err:
                            print(f'md5:{md5}\nimage_name:{image_name}\nerr:{err}') 
                            pyautogui.alert(f'save_md5 Err!')


    connect.commit()
    connect.close()
    # connect.close()
    # connect.close()

def init_db_table():
    '''pass'''
    db_path = os.path.join(os.path.dirname(__file__), 'save_md5.db')
    if os.path.exists(db_path):
        old_db_path = os.path.join(os.path.dirname(__file__), 'old_db', f'{time.time()}_save_md5.db')
        shutil.copy(db_path, old_db_path)
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()
    cursor.execute('''SELECT tbl_name FROM sqlite_master WHERE type = 'table'; ''')
    values = cursor.fetchall()
    tables = []
    for value in values:
        tables.append(value[0])
    if not tables:
        cursor.execute(f"CREATE TABLE vedio (id integer PRIMARY KEY, md5 text, name text);")
        print(f'create table vedio.')
    return connect, cursor

def main():
    '''pass'''
    now_time = time.time()
    # image_dir = r'C:\depository\code\DIY\spider\bili\新建文件夹 (2)'
    save_md5()
    print(f'used time is {time.time() - now_time} s')
    pyautogui.alert(f'save_md5 is done!')
if __name__ == "__main__":
    main()
