from bs4 import BeautifulSoup
import requests as rq
import re
import openpyxl
import json

identity = []#중복 제거를 위한 변수

def clean_text(text):#데이터 normalization
    cleaned_text = re.sub('[a-zA-Z]', '', text)
    cleaned_text = re.sub('["\~\?\>\)\%\]\·\,\①\?\+\:\\/\@\(\[\④\×\"\?\②\∼\?\③\-]',
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
                if result not in identity: #중복되지 않는 headline인 경우만 입력
                    identity.append(result)
                    f.write(result+'\t'+str(price)+'\t'+str(stock)+'\n')
    f.close()
# =======================================
# -- MAIN function
# =======================================
querys = ["김정은","북 핵", "북 도발","북 미사일","북 회담","북 제재","북 통일","북 개성공단"]
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
        crawling(sdate,edate,query,"정치",price,stock)
