import requests
import json
import os

def morpAnalysisReq(question) :
    response = requests.get('http://127.0.0.1:9980?str=' + question)
    response.encoding=None
    return response.json()

def KeywordSelect(wordList) :
    selectedKeyword = []
    #print(wordList)
    for x in wordList :
        numberFound = False
        save = ''
        for y in x["morp_list"] :
            isKeyword = False
            morp = y["morp"]
            pos = y["pos"]
            if pos == "수관형사" :
                numberFound = True
                if save == '' :
                    save += morp
                else :
                    print("수관형사를 하는데 뭔가 이상하다")
            elif pos == "단위성의존명사" :
                if numberFound :
                    save += morp
                    selectedKeyword.append(save)
                    save = ''
                    numberFound = False
                else :
                    print("단위성의존명사를 하는데 뭔가 이상하다")
            elif pos == "형용사" :
                selectedKeyword.append(morp)
            else :
                tmp = pos[-2:]
                if tmp == '명사' :
                    selectedKeyword.append(morp)
                elif tmp == '동사' :
                    selectedKeyword.append(morp)
                elif tmp == '부사' :
                    selectedKeyword.append(morp)
    return selectedKeyword


wantRetry = True;
while wantRetry :
#질문 입력
    question = input("질문 : ")

#http통신
    analysisResult = morpAnalysisReq(question)

#질문에서 키워드 뽑아내기
    wordList = analysisResult["sentences"][0]["word_list"]
    selectedKeyword = KeywordSelect(wordList)
    
#검색엔진 실행
    queryString = ''
    for x in selectedKeyword :
        queryString += x + '|'
    queryString = queryString[:-1]
    print(queryString)
    os.system('iif_manager_main_test "'+queryString+ '"')
#다시할래요?
    again = input("다시하려면 y를 누르시오")
    if again != 'y' :
        wantRetry = False
