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

identity = []#�ߺ� ���Ÿ� ���� ��
def clean_text(text):#������ normalization
    cleaned_text = re.sub('[a-zA-Z]', '', text)
    cleaned_text = re.sub('["\~\?\>\)\%\]\��\,\��\?\+\:\\/\@\(\[\��\��\"\?\��\��\?\��\-]',
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
            'query':query, #�˻��� Ű����
            'orderby':'news', #���� ����(�ֽż�)
            'pageno':i,
            'categoryd2':category,#��ġ �о߸� ����
            'sdate':sdate, #���۳�¥
            'edate':edate, #����¥
        }
        r = rq.get(url, params) #�ش� url�� ���� ��û
        soup = BeautifulSoup(r.content,'lxml')
        r.close()
        soup2 = soup.find('div',attrs={'class':'search_news_box'})
        #title = ''
        #result = ''
        if soup2 is None:
            break
        for item in soup2.find_all('dl'): #headline�� ����
            title = item.find('dt').get_text()
            result = clean_text(title)
            if result  is not '':
                if result not in identity:#�ߺ����� �ʴ� headline�� ��츸 �Է�
                    identity.append(result)
                    print(result)





#######  �ش� ���Ͽ�����  ######
#�н�, �׽�Ʈ ������ �±� �� ����#
#�� �н� �� ����, ����#
##############################

### Train data , Test Date ###
def read_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        # txt ������ ���(id document label)�� �����ϱ�
        data = data[0:]
    return data
data = read_data('news_stock.txt')

#�н� ������
train_data = data

#�±�
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

#float -> list������ ��ȯ
def change(rate):
    result = [rate]
    return result

print("====���� �м�====")
#�±��� ���� ���� �� �ҷ�����
if os.path.isfile('Prediction.json'):
    with open('Prediction.json',"r",encoding='utf-8') as f:
        train_docs = json.load(f)
else:
    train_docs = [(tokenize(row[0]),change(row[2]),row[1]) for row in train_data]
    with open('Prediction.json', 'w', encoding="utf-8") as make_file:
        json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")

tokens = [t for d in train_docs for t in d[0]]
text = nltk.Text(tokens, name='NMSC')

# �� ��ū �� 7819
selected = [f[0] for f in text.vocab().most_common(4000)]
print(len(selected))
selected_words = selected[:3999]
def term_frequency(doc):
    return [doc.count(word) for word in selected_words]

#input���� ��ȯ
def dataSet(data):
    result = []
    for d in data:
        text = term_frequency(d[0])
        text.append(float(d[1][0]))
        result.append(text)
    return result


from keras.models import load_model
print("====������====")
model = load_model("model")

def predict_pos_neg(content,stock_value):
    token = tokenize(content)
    tf = term_frequency(token)
    tf.append(stock_value)
    data = np.expand_dims(np.asarray(tf).astype('float32'), axis=0)
    x_data = data.reshape(data.shape[0],4000,1)
    score = float(model.predict(x_data))

    if(score > 0.5):
        return "[{}]\n �� {:.2f}% Ȯ���� ��� ����\n".format(content, score * 100)
    else:
        return "[{}]\n �� {:.2f}% Ȯ���� �϶� ����\n".format(content, (1 - score) * 100)

print("====�𵨽���====")
querys = ["�� ��", "�� ����","�� �̻���","�� ȸ��","�� ����","�� �й�","�� ����ȭ"]
import socket
def run_server(port=PORT):
    host = HOST
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        while True:
            print("������")
            conn, addr = s.accept()
            print("����")
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
                        crawling(sdate, edate, query, "��ġ")
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

