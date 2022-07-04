from flask import Flask, request
from flask_api import status
import mariadb
import json
from dotenv import load_dotenv
import os
import hashlib
from googletrans import Translator

application = Flask(__name__)

@application.route('/')
def index():
    return 'Simple Game Wannabe'

@application.route('/get_bls_record', methods=['GET', 'POST'])
def get_bls_record():
    if request.method == 'POST':
        result = json.dumps(get_record(100))
    else:
        result = {"result_code": "999", "message": "Request method is not POST."}
    
    return result, status.HTTP_200_OK

@application.route('/set_bls_record', methods=['GET', 'POST'])
def set_bls_record():
    if request.method == 'POST':
        if request.is_json:
            params = request.get_json()
            score = params['score']
            nickname = params['nickname']
            key = params['key']
            mix = (str(score) + nickname).replace(".",get_env('USERNAME'))
            compare = hashlib.sha256(mix.encode()).hexdigest()
            if key == compare:
                dupl = False
                for record in get_record(100):
                    if record["nickname"] == nickname and record["score"] == score:
                        dupl = True
                if dupl:
                    result = {"result_code": "300", "message": "Duplicate records with the same name cannot be entered."}
                else:
                    set_record(nickname, score)
                    result = {"result_code": "000"}
            else:
                result = {"result_code": "200", "message": "The key is not valid."}
        else:
            result = {"result_code": "100", "message": "Request format is not JSON."}

    else:
        result = {"result_code": "999", "message": "Request method is not POST."}
    
    return result, status.HTTP_200_OK

@application.route('/trans_lang', methods=['GET', 'POST'])
def trans_lang():
    try:
        if request.method == 'POST':
            params = request.get_json()
            source = params.get('source')
            target = params.get('target')
            q = params.get('q')
            if q is not None:
                result = json.dumps(translate(q, source, target))
            else:
                result = {}
        else:
            result = {"result_code": "999", "message": "Request method is not POST."}
    except Exception as e:
        result = e.with_traceback()
    
    return result, status.HTTP_200_OK

def translate(text_list, src, dest):
    translator = Translator()
    result  = {
        "data": {
            "translations": []
        }
    }
    for text in text_list:
        translated = {'translatedText':translator.translate(text, src=src, dest=dest).text}
        result['data']['translations'].append(translated)
    return result

def get_env(name):
    return os.environ.get(name)

def connect_db():
    try:
        return mariadb.connect(
            user=get_env('USERNAME'),
            password=get_env('PASSWORD'),
            host=get_env('HOST'),
            port=int(get_env('PORT')),
            database=get_env('DB')
        )
    except mariadb.Error as e:
        print(e)

def get_record(limit):
    try:
        conn = connect_db()
        sql = 'SELECT id, nickname, score FROM bls_record ORDER BY score DESC LIMIT 0, ' + str(limit)
        result = []
        cur = conn.cursor()
        cur.execute(sql)
        for data in cur:
            result.append({
                'id': str(data[0]),
                'nickname': data[1],
                'score': str(data[2])
                })
        conn.close()
        return result
    except mariadb.Error as e:
        print(e)

def set_record(nickname, score):
    try:
        conn = connect_db()
        sql = 'INSERT INTO bls_record(nickname, score) VALUES(?, ?)'
        cur = conn.cursor()
        cur.execute(sql, (nickname, score))
        conn.commit()
        conn.close()
    except mariadb.Error as e:
        print(e)

if __name__ == "app":
    load_dotenv()
    conn = connect_db()

if __name__ == "__main__":
    application.run(host="localhost", port="5000")
