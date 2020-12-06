import mecab
import json
import os
import nltk
import numpy as np
import tensorflow.python.keras
from tensorflow.python.keras import models
from tensorflow.python.keras import layers
from tensorflow.python.keras import optimizers
from tensorflow.python.keras import losses
from tensorflow.python.keras import metrics
from matplotlib import font_manager, rc

#######  해당 파일에서는  ######
#학습, 테스트 데이터 태깅 및 저장#
#모델 학습 및 생성, 저장#
##############################

### Train data , Test Date ###
def read_data(filename):
    with open(filename, 'r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        # txt 파일의 헤더(id document label)는 제외하기
        data = data[0:]
    return data

data = read_data('crawling.txt')


part1 = round(len(data)*0.3*0.8)
train_data1 = data[:part1]
part2 = part1 + round(len(data)*0.3*0.1)
validation_data1 = data[part1:part2]
part3 = part2 + round(len(data)*0.3*0.1)
test_data1 = data[part2:part3]
part4 = part3 + round(len(data)*0.3*0.8)
train_data2 = data[part3:part4]
part5 = part4 + round(len(data)*0.3*0.1)
validation_data2 = data[part4:part5]
part6 = part5 + round(len(data)*0.3*0.1)
test_data2 = data[part5:part6]
part7 = part6+round(len(data)*0.4*0.8)
train_data3 = data[part6:part7]
part8 = part7+round(len(data)*0.4*0.1)
validation_data3 = data[part7:part8]
test_data3 = data[part8:]
#학습 데이터
train_data = train_data1+train_data2+train_data3
#테스트 데이터
validation_data= validation_data1+validation_data2+validation_data3
#평가 데이터
test_data = test_data1+test_data2+test_data3

#테스트 파일 분리
f = open("test.txt",'w')
for row in test_data:
    f.write(row[0]+'\t'+row[1]+'\t'+row[2]+'\n')
f.close()

mecab = mecab.MeCab()

news = []
frequency =[]
pos = []
neg = []

def count(content, rate):
    if content not in news:
        news.append(content)
        frequency.append(1)
        if rate == 1:
            pos.append(1)
            neg.append(0)
        else:
            pos.append(0)
            neg.append(1)
    else:
        num = news.index(content)
        frequency[num] += 1
        if rate == 1:
            pos[num] += 1
        else:
            neg[num] += 1

def tokenization(doc,rate):
    for t in mecab.pos(doc):
        if "SH" in t[1] or "SL" in t[1]:
            count(t[0],rate)
        elif "NNB" not in t[1] and "J"not in t[1]:
            if "IC" not in t[1] and "S"not in t[1]:
                if "E" not in t[1] and "X"not in t[1]:
                        count(t[0],rate)
for row in train_data:
    tokenization(row[0],int(row[1]))


def tokenize(doc):
    result = []
    for t in mecab.pos(doc):
        if "SH" in t[1] or "SL" in t[1]:
            result.append(t[0])
        #elif t[0] in stop:
        #    continue
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
if os.path.isfile('train_doc.json'):
    with open('train_doc.json',"r",encoding='utf-8') as f:
        train_docs = json.load(f)
    with open('validation_doc.json',"r",encoding='utf-8') as f:
        validation_docs = json.load(f)
    with open('test_doc.json',"r",encoding='utf-8') as f:
        test_docs = json.load(f)
else:
    train_docs = [(tokenize(row[0]),change(row[2]),row[1]) for row in train_data]
    validation_docs= [(tokenize(row[0]),change(row[2]),row[1]) for row in validation_data]
    test_docs = [(tokenize(row[0]),change(row[2]),row[1]) for row in test_data]

    # JSON 파일로 저장
    with open('train_doc.json', 'w', encoding="utf-8") as make_file:
        json.dump(train_docs, make_file, ensure_ascii=False, indent="\t")
    with open('validation_doc.json', 'w', encoding="utf-8") as make_file:
        json.dump(validation_docs, make_file, ensure_ascii=False, indent="\t")
    with open('test_doc.json', 'w', encoding="utf-8") as make_file:
        json.dump(test_docs, make_file, ensure_ascii=False, indent="\t")

tokens = [t for d in train_docs for t in d[0]]
text = nltk.Text(tokens, name='NMSC')

# 총 토큰 수
selected_words = [f[0] for f in text.vocab().most_common(10000)]
selected = []

words = []
senti = []
for row in news:
    if row in selected_words:
        x = news.index(row)
        words.append(row)
        val = (pos[x]-neg[x])/frequency[x]
        senti.append(val)
        if val <= -0.3 or val >= 0.3 and frequency[x] >=3:
            selected.append(row)

def term_frequency(doc):
    return [doc.count(word) for word in selected]

#input으로 변환
def dataSet(data):
    result = []
    for d in data:
        text = term_frequency(d[0])
        text.append(float(d[1][0]))
        result.append(text)
    return result


print("====데이터 준비====")


print(len(selected))

#학습 및 테스트할 데이터 전처리
train_x = dataSet(train_docs)
test_x = dataSet(test_docs)
validation_x = dataSet(validation_docs)
train_y = [c[2][0] for c in train_docs]
test_y = [c[2][0] for c in test_docs]
validation_y =[c[2][0] for c in validation_docs]
x_train = np.asarray(train_x).astype('float32')
x_test = np.asarray(test_x).astype('float32')
x_validation = np.asarray(validation_x).astype('float32')
y_train = np.asarray(train_y).astype('float32')
y_test = np.asarray(test_y).astype('float32')
y_validation = np.asarray(validation_y).astype('float32')

x_train_t = x_train.reshape(x_train.shape[0],2957,1)
x_test_t = x_test.reshape(x_test.shape[0],2957,1)
x_validation_t = x_validation.reshape(x_validation.shape[0],2957,1)


#########MODEL#############
print("====모델생성====")
#모델 구성
model = models.Sequential()
model.add(layers.GRU(64, input_shape=(2957,1), activation='relu',return_sequences=True,dropout=0.8))
model.add(layers.GRU(64,activation='tanh',return_sequences=True))
model.add(layers.GRU(64,activation='tanh',return_sequences=True))
model.add(layers.Flatten())
model.add(layers.Dense(1, activation='sigmoid'))#relu성능 최하 쓰지말자 output에
model.compile(optimizer=optimizers.Adam(lr=0.002),
#모델 학급과정 설정
             loss=losses.binary_crossentropy,
             metrics=['accuracy'])
#학습 batch_size/2 => epochs/2

model.fit(x_train_t, y_train, epochs=50, batch_size=256,validation_data=(x_validation_t,y_validation),verbose=2)
#평가
loss, acc = model.evaluate(x_test_t, y_test,verbose=2)
print("Test loss:",loss)
print("Test accurary:",acc)
from keras.models import load_model
print("====모델저장====")
model.save('model')
