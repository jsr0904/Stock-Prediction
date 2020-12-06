from bs4 import BeautifulSoup
import requests as rq
import re
import openpyxl
import json

identity = []#�ߺ� ���Ÿ� ���� ����

def clean_text(text):#������ normalization
    cleaned_text = re.sub('[a-zA-Z]', '', text)
    cleaned_text = re.sub('["\~\?\>\)\%\]\��\,\��\?\+\:\\/\@\(\[\��\��\"\?\��\��\?\��\-]',
                          '', cleaned_text)
    return cleaned_text

# =======================================
# -- CRAWLING function
# =======================================
def crawling(sdate,edate,query,category,price,stock):
    url = 'http://search.chosun.com/search/news.search'
    f = open('crawling.txt', 'a')
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
                if result not in identity: #�ߺ����� �ʴ� headline�� ��츸 �Է�
                    identity.append(result)
                    f.write(result+'\t'+str(price)+'\t'+str(stock)+'\n')
    f.close()
# =======================================
# -- MAIN function
# =======================================
querys = ["������","�� ��", "�� ����","�� �̻���","�� ȸ��","�� ����","�� ����","�� ��������"]
wb = openpyxl.load_workbook('./stock.xlsx')
excel = wb['Sheet1']

for row in excel:
    sdate = row[0].value
    edate = row[1].value
    if row[2].value >= 0:
        price = 1
    else:
        price = 0
    stock = row[3].value
    for query in querys:
        crawling(sdate,edate,query,"��ġ",price,stock)
