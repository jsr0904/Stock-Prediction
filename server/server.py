from konlpy.tag import Mecab
import json
import os
import nltk
import numpy as np
from tensorflow.python.keras import models
import datetime
from bs4 import BeautifulSoup
import requests as rq
import os
import re

#changing rate of Stock
rate = 0.01
#HOST, Port Number
HOST = ''
PORT = 5006

identity = []#중복 제거를 위한 변
def clean_text(text):#데이터 normalization
    cleaned_text = re.sub('[a-zA-Z]', '', text)
    cleaned_text = re.sub('["\~\?\>\)\%\]\·\,\①\?\+\:\\/\@\(\[\④\×\"\?\②\∼\?\③\-]',
                          '', cleaned_text)
    return cleaned_text

# =======================================
# -- CRAWLING function
# =======================================
def crawling(sdate,edate,query,category):
    url = 'http://search.chosun.com/search/news.search'
    print(sdate)
    for i in range(1, 100000):
        params = {
            'query':query, #검색할 키워드
            'orderby':'news', #정렬 순서(최신순)
            'pageno':i,
            'categoryd2':category,#정치 분야만 선택
            'sdate':sdate, #시작날짜
            'edate':edate, #끝날짜
        }
        r = rq.get(url, params) #해당 url의 정보 요청
        soup = BeautifulSoup(r.content,'lxml')
        r.close()
        soup2 = soup.find('div',attrs={'class':'search_news_box'})
        #title = ''
        #result = ''
        if soup2 is None:
            break
        for item in soup2.find_all('dl'): #headline만 추출
            title = item.find('dt').get_text()
            result = clean_text(title)
            if result  is not '':
                if result not in identity:#중복되지 않는 headline인 경우만 입력
                    identity.append(result)
                    print(result)





#######  해당 파일에서는  ######
#학습, 테스트 데이터 태깅 및 저장#
#모델 학습 및 생성, 저장#
##############################

### Train data , Test Date ###
def read_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        # txt 파일의 헤더(id document label)는 제외하기
        data = data[0:]
    return data
data = read_data('news_stock.txt')

#학습 데이터
train_data = data

#태깅
mecab = Mecab()

def tokenize(doc):
    result = []
    for t in mecab.pos(doc):
        if "SH" in t[1] or "SL" in t[1]:
            result.append(t[0])
        elif t[0] in stop:
            continue
        elif "NNB" not in t[1] and "J"not in t[1]:
            if "IC" not in t[1] and "S"not in t[1]:
                if "E" not in t[1] and "X"not in t[1]:
                    result.append(t[0])
    return result

#float -> list형으로 변환
def change(rate):
    result = [rate]
    return result

print("====문장 분석====")
#태깅한 것을 저장 및 불러오기
if os.path.isfile('Prediction.json'):
    with open('Prediction.json',"r",encoding='utf-8') as f:
        train_docs = json.load(f)
else:
    train_docs = [(tokenize(row[0]),change(row[2]),row[1]) for row in train_data]
    with open('Prediction.json', 'w', encoding="utf-8") as make_file:
        json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")

tokens = [t for d in train_docs for t in d[0]]
text = nltk.Text(tokens, name='NMSC')

# 총 토큰 수 7819
selected = [f[0] for f in text.vocab().most_common(4000)]
print(len(selected))
selected_words = selected[:3999]
def term_frequency(doc):
    return [doc.count(word) for word in selected_words]

#input으로 변환
def dataSet(data):
    result = []
    for d in data:
        text = term_frequency(d[0])
        text.append(float(d[1][0]))
        result.append(text)
    return result


from keras.models import load_model
print("====모델저장====")
model = load_model("model")

def predict_pos_neg(content,stock_value):
    token = tokenize(content)
    tf = term_frequency(token)
    tf.append(stock_value)
    data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
    x_data = data.reshape(data.shape[0],4000,1)
    score = float(model.predict(x_data))

    if(score > 0.5):
        return "[{}]\n ▶ {:.2f}% 확률로 상승 예정\n".format(content, score * 100)
    else:
        return "[{}]\n ▶ {:.2f}% 확률로 하락 예정\n".format(content, (1 - score) * 100)

print("====모델실행====")
querys = ["북 핵", "북 도발","북 미사일","북 회담","북 제재","북 압박","북 비핵화"]
import socket
def run_server(port=PORT):
    host = HOST
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        while True:
            print("연결대기")
            conn, addr = s.accept()
            print("연결")
            flag = 0
            while True:
                result = ""
                data = conn.recv(1024)
                print(data.decode())
                string = str(data.decode()).strip()
                if (string == 'real'):
                    flag = 1
                    edate = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
                    sdate = (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime('%Y.%m.%d %H:%M:%S')
                    for query in querys:
                        crawling(sdate, edate, query, "정치")
                    for i in identity:
                        result = result + predict_pos_neg(i, rate)
                elif (string == 'exit'):
                    break
                else:
                    string, stock = string.split('/')
                    result = predict_pos_neg(string, float(stock))
                print(result)
                conn.sendall(result.encode("utf-8"))
                if(flag == 1): break
            conn.close()
run_server()

