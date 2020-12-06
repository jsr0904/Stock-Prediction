# 뉴스/SNS 데이터 분석 및 딥러닝을 이용한 주가예측

## 필요성 및 설계
* 시간적 흐름의 영향을 받으며 외부의 변수에 영향을 받는 비 선형적인 특징을 갖는 주가 데이터와 비 선형적인 모델 학습에 적합한 딥 러닝을 통해 모델 생성
* 대북 관련 뉴스를 이용해 감성사전을 구축하였고 딥러닝 알고리즘인 MLP, GRU을 이용해 주가 예측을 실시 하였음
* 감성사전은 BOW에 이용할 단어 선정에 사용하였고 Parameter값을 변경하면서 최적의 모델을 찾음

# 뉴스 데이터
* 대북 관련 기업 중 “철도, 시멘트, 금강산, DMZ, 아스콘“에 속하는 기업들을 이용
* 검색한 날짜: 2011.18~2019.03.04 기간 중에서 선택한 기업들의 평균 변화율이 1%이상 또는 -1%이하의 변화를 보인 날짜가 3일 이상인 기간과 4%이상 또는 -4%이하의 변화율이 발생한 날짜로 검색
* 조선일보에서 정치 분야에서만 뉴스 수집
* 수집된 5549개의 시계열 데이터를 30%, 30%, 40%로 구간을 나눔
* 구간별 80%는 train data, 10%는 validation data, 10%는 test data로 이용
* 정확도 향상을 위해 input에 주가 데이터 추가(전날의 총지수 변화율)

# 감성 사전
* 조선일보 사이트에서  대북 관련 뉴스 제목 Crawling
* Re module을 통해 특수기호 등의 데이터 전처리
* 한국어 분석기 중 Mecab을 이용해서 단어로 분해
* 단어 별 빈도수 측정 및 상승, 하락한 날의 뉴스에서 나온 횟수 측정
* 측정된 값으로 감성사전 구축 후 score값이 0.3이상이거나 0.3이하고 빈도수가 3회 이상인 단어로 BOW 구축

# MLP ( Multiple Layer Perceptron )
* 가장 기본적인 Deep Learning 알고리즘
* Input layer 와 output layer 사이에 하나 이상의 hidden layer 가 존재하는 신경망
* 뉴스 제목을 입력 할 시 상승할 것인지 하락할 것인지 판별
<img src= https://github.com/jsr0904/Stock-Prediction/blob/main/MLP%20Model.png >

# GRU 
* LSTM에서 Forget, input, output gate를 줄여 Reset, Update gate를 이용하는 알고리즘
  - Reset : 새로운 입력을 이전 메모리와 어떻게 합칠지
  - Update : 이전 메모리를 얼마나 기억할지
* Parameter 수가 LSTM보다 적어서 학습 시간이 더 짧고 적은 데이터로도 학습이 가능
* 출력에 비선형 계산식이 필요가 없음
* 뉴스 제목을 입력 할 시 상승할 것인지 하락할 것인지 판별
<img src= https://github.com/jsr0904/Stock-Prediction/blob/main/GRU%20Model.png >

# 예측 결과
* 성능 지표는 Accuracy와 F1 score 이용
  - Accuracy : 예측 값과 실제 값이  일치될 확률
  - F1 score : 정밀성(Positive로 예측한 내용 중에 실제 Positive의 비율)과 재현율(실제 Positive 중 Positive로 예측한 비율)의 평균

      ||accuracy|precision|precision|F1_Score|
      |----|--------|---------|---------|--------|
      |MLP|0.72|0.52|0.48|0.5|
      |GRU|0.8|0.47|0.57|0.52|



