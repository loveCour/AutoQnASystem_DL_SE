# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from Bracket_Process_Function import *

""" Test가 필요할 때 """
if False:
    for i in range(11):
        print(i)

        tree = ET.parse('wikisplit' + str(i))
        root = tree.getroot()

        for page in root:
            title = ''

            for tags in page:
                if tags.tag == 'title':
                    title = tags.text

                if tags.tag == 'revision':
                    for text in tags:
                        if text.tag == 'text':

                            if title == '덩샤오핑':
                                print(text.text)
                                input()

"""
인명 인식을 위한 토큰 요소

2. | 원래 이름
3. | 출생일
4. | 출생지
5. | 국적
6. | 직업
7. | 소속
8. | 배우자
9. | 종교
10. | 학력
11. | 부모
"""

"""
지명 인식을 위한 토큰 요소

1. |인구
2. |지도
3. |면적
4. |세대
5. |총인구
6. |인구밀도
7. |행정구역

"""

"""
동/식물명 인식을 위한 토큰 요소

1. |계: 식물계
2. |계: 동물계

"""


def check_hangeul(z):
    a = '가'
    b = '힣'
    c = 'A'
    d = 'z'
    e = '1'
    f = '0'

    if a <= z <= b:
        #print('!!')
        #print(c)
        #input()
        return True
    elif e <= z <= f:
        return True
    else:
        #print('@@')
        #print(c)
        #input()
        return False


def check(line):
    for i in range(len(line)):
        #print(line[i])

        if line[i] == ':' and len(line) > 2:
            if line[i - 2] == '파' and line[i - 1] == '일':
                return False

        if line[i] == ':' and len(line) > 1:
            if line[i - 1] == '틀':
                return False

        if line[i] == ':' and len(line) > 4:
            if line[i - 4] == '위' and line[i - 3] == '키' and line[i - 2] == '백' and line[i - 1] == '과':
                return False

        if line[i] == ':' and len(line) > 2:
            if line[i - 2] == '분' and line[i - 1] == '류':
                return False

    return True

def preprocess(result_):
    result_ = Bracket_Processing(result_, '(', ')')
    #result_ = Bracket_Processing4_(result_, '[[', ']]')
    result_ = Bracket_Processing5(result_, '[[', '|', ']]')
    result_ = Bracket_Processing6(result_, '<ref>', '</ref>')
    result_ = Bracket_Processing_file(result_, '[[파일:', '[[', ']]')
    result_ = Bracket_Processing(result_, '<', '>')

    result_ = result_.replace('-', ' ')
    result_ = result_.replace('\'\'\'', '')
    result_ = result_.replace('”', '')
    result_ = result_.replace('“', '')
    result_ = result_.replace('《', '')
    result_ = result_.replace('》', '')
    result_ = result_.replace(' ( ', '(')
    result_ = result_.replace(' \" ', '')
    result_ = result_.replace('\"', '')
    result_ = result_.replace('[[', '')
    result_ = result_.replace(']]', '')
    result_ = result_.replace(',', '')
    result_ = result_.replace('\'\'', '')
    result_ = result_.replace('<', '')
    result_ = result_.replace('>', '')
    result_ = result_.replace('〈', '')
    result_ = result_.replace('〉', '')

    result_ = result_.strip()

    return result_

data = pd.read_excel("C:\\Users\\Administrator\\Desktop\\qadataset\\exobrain\\"\
                    "엑소브레인 말뭉치V3.0\\엑소브레인 QA Datasets\\ETRI QA Datasets\\"\
                    "단문질문 QA dataset(위키피디아, 기본태깅, 1,776개).xlsx")

title_list = []
answer_list = []
answer_ground_list = []
question_list = []

for i in range(len(data['위키피디아 제목']) - 1):
    title_list.append(data['위키피디아 제목'][i])

    answer = preprocess(str(data['정답 근거1(문장)'][i]))
    answer = answer.split('.')[0]
    #print(answer)
    #print('---')
    #input()
    answer = answer.strip()
    answer_ground_list.append(answer)

    answer_list.append(str(data['정답'][i]))

    que = str(data['질문'][i]).replace('?', '')
    question_list.append(que)

title = ''
refined_text = ''
refined_text_list = []

Wiki_Index = -1
Wiki_answer = 0
Wiki_question = 0
Wiki_answer_ground = 0

start_end_indeX_file = open('start_end_index_file', 'w', encoding='utf-8')
label_file = open('label_file', 'w', encoding='utf-8')
question_file = open('question_file', 'w', encoding='utf-8')
sentence_file = open('sentence_file', 'w', encoding='utf-8')

labels = []
paragraph = []
questions = []
start_index = []
end_index = []

acc_index = 0

# 11개 split file
for a in range(11):
    print(a, 'processing...')

    tree = ET.parse('wikisplit' + str(a))
    root = tree.getroot()

    for page in root:
        check_ok = True

        for tags in page:
            if tags.tag == 'title':
                title = tags.text

                Wiki_Index = -1
                for t in range(len(title_list)):
                    if title_list[t] == title:
                        Wiki_Index = t
                        Wiki_answer = answer_list[t]
                        Wiki_question = question_list[t]
                        Wiki_answer_ground = answer_ground_list[t]

                        # print('index::', title_list[t], title)

            #body text processing
            if Wiki_Index != -1:
                if tags.tag == 'revision' and check_ok is True:
                    for text in tags:
                        if text.tag == 'text':
                            #print(text.text)

                            sentences = text.text
                            sentences = str(sentences).replace('.', '\n')
                            sentences = text.text.split('\n')

                            for s in range(len(sentences)):
                                result = sentences[s]
                                result = preprocess(result)
                                sentences[s] = result

                            #####################
                            #refine text
                            #####################
                            if Wiki_Index != -1:
                                # print(title)
                                # print('-------')
                                # print(refined_text)

                                ground = Wiki_answer_ground
                                answer_index = refined_text.find(ground)

                                is_have_anser = False
                                for s in sentences:
                                    if str(s).find(Wiki_answer_ground) != -1:
                                        is_have_anser = True

                                #ok case
                                if is_have_anser is True:
                                    print(Wiki_answer, '------')

                                    length_of_paragraph = 0

                                    for s in sentences:
                                        if check_Sentence(s) is True:
                                            length_of_paragraph += 1

                                            paragraph.append(str(s))
                                            questions.append(str(Wiki_question))
                                            if str(s).find(Wiki_answer_ground) != -1:
                                                labels.append(1)
                                            else:
                                                labels.append(0)

                                    start_index.append(int(acc_index))
                                    acc_index += length_of_paragraph
                                    end_index.append(int(acc_index))

                                # print(answer_index, ground)
                                # input()
                                refined_text = ''

for s in range(len(paragraph)):
    sentence_file.write(paragraph[s])
    sentence_file.write('\n')

    question_file.write(questions[s])
    question_file.write('\n')

    label_file.write(str(labels[s]))
    label_file.write('\n')

for s in range(len(start_index)):
    start_end_indeX_file.write(str(start_index[s]) + '#' + str(end_index[s]))
    start_end_indeX_file.write('\n')

sentence_file.close()
question_file.close()
label_file.close()
start_end_indeX_file.close()