import hashlib
import string
import os
import json
import random
import requests
import csv

from werkzeug.utils import secure_filename
from NationalEducationRadio.service import app
from flask import flash

SIMPLE_CHARS = string.ascii_letters + string.digits
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/../../static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_random_string(length = 24):
    """
    產生一組亂數字串
    :param length: 亂數字串長度，預設24
    :return: 亂數字串
    """
    ret_str = ''
    while length > 0:
        ret_str = ret_str.join(random.choice(SIMPLE_CHARS))
        length -= 1
    return ret_str


def password_encryption(password):
    """
    將密碼用sha256加密
    :param password: 密碼明碼
    :return: 雜湊後的密碼
    """
    return hashlib.sha256(password.encode('ascii')).hexdigest()


def allowed_file(filename):
    """
    過濾副檔名
    :param filename: 表單回傳的檔案物件
    :return: 布林值，副檔名是否合法
    """
    allow_extensions = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'csv', 'mp3']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allow_extensions


def image_upload(file):
    """
    上傳檔案
    :param file: 表單回傳的檔案物件
    :return: 布林值，成功與否
    """
    if file and allowed_file(file.filename):
        filename = get_random_string() + secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None


def delete_image(filename):
    """
    刪除檔案
    :param filename: 要刪除的檔案名稱
    :return: 布林值，成功與否
    """
    if allowed_file(filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filename):
            os.remove(filename)
        return True
    return None


def audio_upload(file):
    """
    上傳檔案
    :param file: 表單回傳的檔案物件
    :return: 布林值，成功與否
    """
    if file and allowed_file(file.filename):
        filename = get_random_string() + secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return None


def delete_audio(filename):
    """
    刪除檔案
    :param filename: 要刪除的檔案名稱
    :return: 布林值，成功與否
    """
    if allowed_file(filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(filename):
            os.remove(filename)
        return True
    return None


def required_to_flash(form):
    """
    將 wtf 產生的 required 改成 flash 方式送給templates
    :param form: 表單物件
    :return: 無
    """
    for name, messages in form.errors.items():
        for message in messages:
            flash(message)


def jqgrid_json(success, message=''):
    """
    回傳給jqgrid的json格式
    :param success: 布林值，是否成功
    :param message: 失敗時的訊息
    :return: json字串
    """
    src = {
        "success":  success,
        "message":  message
    }
    return json.dumps(src)

def parse_question_csv(file):
    if file and allowed_file(file.filename):
        filename = get_random_string() + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        csvfile = open(fullfilename, 'r')
        reader = csv.reader(csvfile)
        next(reader, None)
        questions = []
        i = 0
        for row in reader:
            questions.append({
                "id": i + 1,
                "content": row[2], 
                "type": "single",
                "start": row[0],
                "end": row[1],
                "answer": [4 * i + int(row[3])],
                "options": [
                    {
                        "id": 4 * i + 1, 
                        "label": row[4]
                    },
                    {
                        "id": 4 * i + 2, 
                        "label": row[5]
                    },
                    {
                        "id": 4 * i + 3, 
                        "label": row[6]
                    },
                    {
                        "id": 4 * i + 4, 
                        "label": row[7]
                    },
                ]
            })
            i += 1
        csvfile.close()
        os.remove(fullfilename)
        return json.dumps(questions)
    return None

def get_solr_data(audio_id):
    url = "http://140.124.183.5:8983/solr/EBCStation/select?indent=on&q=id:%d&wt=json&start=0&rows=105" % audio_id
    a = requests.get(url).json()
    if len(a['response']['docs']) == 1:
        return (True, ' , '.join(a['response']['docs'][0]['keywords'][0].split(",")), 
            a['response']['docs'][0]['summary'][0])
    return (False, None, None)



def article_filter(content):
    s = ""
    content = content.split("\n")
    for line in content:
        line = line.replace("\n", "").strip().split(" ")
        if line[3] != "<eps>" and line[3] != "<UNK>":
            s += line[3]

    pre = ["但", "甚至", "就是", "同時", "不過", "應該",
            "那", "所以", "而", "因為", "現在"]
    post = ["了", "的話", "解釋說"]
    for word in pre:
        s = s.replace(word, "，" + word)
    for word in post:
        s = s.replace(word, word + "，")
    for i in range(10):
        s = s.replace("，，", "，")

    return s
