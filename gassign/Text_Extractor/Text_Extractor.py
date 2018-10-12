# -*- coding: utf-8 -*-

from functions import *
import xml.etree.ElementTree as ET
import numpy as np


def Bracket_Processing(string, start, end):
    result = ''

    is_bracket = False

    for i in range(len(string)):
        if string[i] == start:
            is_bracket = True
        elif string[i] == end:
            is_bracket = False
        elif is_bracket == False:
            result += string[i]

    return result
#< >


def Bracket_Processing2(string, start, end):
    result = ''

    is_bracket = False

    for i in range(len(string)):
        if string[i] == start:
            is_bracket = True
        elif string[i] == end:
            is_bracket = False
            result += string[i]
        elif is_bracket == False:
            result += string[i]

    return result


def Bracket_Processing3(string, start, end):
    result = ''

    is_bracket = False

    for i in range(len(string)):
        if i + 1 < len(string):
            if string[i] == start[0] and string[i + 1] == start[1]:
                is_bracket = True
            elif string[i] == end:
                is_bracket = False
                result += string[i]
            elif is_bracket == False:
                result += string[i]
        else:
            if string[i] == end:
                is_bracket = False
                result += string[i]
            elif is_bracket == False:
                result += string[i]
    return result


def Bracket_Processing4(string, start, end):
    result = ''

    bracket_count = 0
    is_bracket = False

    #print(len(string))

    for i in range(len(string)):
        if i + 1 < len(string) and i > 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                bracket_count += 1
            elif string[i - 1] == end[0] and string[i] == end[1]:
                bracket_count -= 1
            elif bracket_count == 0:
                result += string[i]
        elif i == 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                bracket_count += 1
        else:
            if bracket_count == 0:
                result += string[i]
        #print(string[i])
        #print(bracket_count)

    return result


def Bracket_Processing4_(string, start, end):
    result = ''

    bracket_count = 0

    for i in range(len(string)):
        if i + 1 < len(string) and i > 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                if bracket_count == 0:
                    result += string[i]

                bracket_count += 1
            elif string[i - 1] == end[0] and string[i] == end[1]:
                bracket_count -= 1

                if bracket_count == 0:
                    result += string[i - 1]
            elif bracket_count <= 1:
                result += string[i]
        elif i == 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                bracket_count += 1
        else:
            if bracket_count <= 1:
                result += string[i]
        #print(string[i])
        #print(bracket_count)

    return result
# [[  ]]


def Bracket_Processing5(string, start, end, end2):
    result = ''

    bracket_count = 0
    is_bracket = False
    is_bracket_end = False

    #print(len(string))

    for i in range(len(string)):
        if i + 1 < len(string) and i > 0:
            if is_bracket is True and is_bracket_end is True:
                if string[i - 2] == end2[0] and string[i - 1] == end2[1]:
                    is_bracket = False
                    is_bracket_end = False
                else:
                    if string[i] != start[0] and string[i] != end2[0]:
                        result += string[i]
            elif string[i] == start[0] and string[i + 1] == start[1]:
                temp_index = i
                token_exist = False
                while temp_index < len(string) - 2:
                    if string[temp_index] == end[0]:
                        token_exist = True
                    if string[temp_index] == end2[0] and string[temp_index + 1] == end2[1]:
                        if token_exist is True:
                            is_bracket = True
                            is_bracket_end = False
                            temp_index += len(string)
                        else:
                            temp_index += len(string)
                    else:
                        temp_index += 1
            elif string[i] == end[0]:
                is_bracket_end = True
        elif i == 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                temp_index = i
                token_exist = False
                while temp_index < len(string) - 2:
                    if string[temp_index] == end[0]:
                        token_exist = True
                    if string[temp_index] == end2[0] and string[temp_index + 1] == end2[1]:
                        if token_exist is True:
                            is_bracket = True
                            is_bracket_end = False
                            temp_index += len(string)
                        else:
                            temp_index += len(string)
                    else:
                        temp_index += 1

        if is_bracket is False and is_bracket_end is False:
            result += string[i]

        #print(string[i])
        #print(bracket_count)

    return result
#[[, | 경우를 처리함


def Bracket_Processing6(string, start, end):
    result = ''

    is_bracket = False

    #print(len(string))
    if len(start) > len(end):
        length = len(start)
    else:
        length = len(end)

    for i in range(len(string)):

        if i + length < len(string) and i >= 0:
            is_start = True
            is_end = True

            for j in range(len(start)):
                if string[i + j] != start[j]:
                    is_start = False

            for j in range(len(end)):
                if string[i - (len(end) - 1 - j)] != end[j]:
                    is_end = False

            if is_start is True:
                is_bracket = True
            elif is_end is True:
                is_bracket = False
            elif is_bracket is False:
                result += string[i]
        elif i == 0:
            if string[i] == start[0] and string[i + 1] == start[1]:
                is_bracket = True
        else:
            if is_bracket is False:
                result += string[i]
        #print(string[i])
        #print(bracket_count)

    return result
#<ref> <ref/>


def Bracket_Processing_file(string, start, start2, end):
    result = ''

    is_bracket = False
    bracket_count = 0

    # print(len(string))
    if len(start) > len(end):
        length = len(start)
    else:
        length = len(end)

    for i in range(len(string)):
        if i + length < len(string) and i >= 0:
            is_start = True
            is_start2 = True
            is_end = True

            for j in range(len(start)):
                if string[i + j] != start[j]:
                    is_start = False

            for j in range(len(start2)):
                if string[i + j] != start2[j]:
                    is_start2 = False

            for j in range(len(end)):
                if string[i - (len(end) - 1 - j)] != end[j]:
                    is_end = False

            if is_start is True:
                is_bracket = True
                bracket_count += 1

            if is_start2 is True:
                bracket_count += 1

            if is_end is True:
                bracket_count -= 1
                if bracket_count == 0:
                    is_bracket = False

        if is_bracket is False:
            result += string[i]

            # print(string[i])
            # print(bracket_count)

    return result
#remove file tag

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

#output_file = open('output_corpus', 'w', encoding='utf-8')
output_file2 = open('wiki_corpus', 'w', encoding='utf-8')

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

            if tags.tag == 'revision' and check_ok is True:
                for text in tags:
                    if text.tag == 'text':
                        try:
                            remove_dic = ['=', '*', '{{', '}}', '[[분류:', '*']

                            #print('----------------------')
                            #print(text.text)

                            sentences = text.text.split('\n')
                            for s in range(len(sentences)):
                                result = sentences[s]
                                result = preprocess(result)
                                sentences[s] = result

                            result_str = ''
                            for s in range(len(sentences)):
                                result_str += sentences[s] + '\n'
                            #print('@@@@@@@@@@@@@@@@@@@@@@@@@')
                            #print(result_str)
                            #input()
                            #[[, |



                            result_str = Bracket_Processing4(result_str, '{{', '}}')
                            result_str = Bracket_Processing(result_str, '「', '」')
                            result_str = Bracket_Processing3(result_str, ' (', ')')
                            result_str = Bracket_Processing(result_str, '(', ')')
                            result_str = Bracket_Processing(result_str, '<', '>')
                            result_str = Bracket_Processing(result_str, '[', ']')
                            result_str = Bracket_Processing2(result_str, '|', ' ')

                            sen = str(text.text).split('\n')

                            #print(len(sen))
                            for i in range(len(sen)):
                                if len(sen[i]) > 1:
                                    if sen[i][0] == '=':
                                        0
                                    elif sen[i][0] == '{':
                                        0
                                    elif sen[i][0] == '}':
                                        0
                                    elif sen[i][0] == '|':
                                        0
                                    elif sen[i][0] == ' ':
                                        0
                                    elif sen[i][0] == '[':
                                        0
                                    elif sen[i][0] == '*':
                                        0
                                    elif sen[i][0] == '<':
                                        0
                                    elif sen[i][0] == ':':
                                        0
                                    elif sen[i][0] == '#':
                                        0
                                    elif sen[i][0] == '!':
                                        0
                                    elif sen[i][0] == ';':
                                        0
                                    else:
                                        if len(sen[i]) > 3:
                                            if sen[i][0] == '파' and sen[i][1] == '일' and sen[i][2] == ':':
                                                0
                                            elif sen[i][0] == 's' and sen[i][1] == 't' and sen[i][2] == 'y':
                                                0
                                            else:
                                                result_str += sen[i] + '\n'

                            result_str = result_str.replace('-', ' ')
                            result_str = result_str.replace('\'\'\'', '')
                            result_str = result_str.replace('”', '')
                            result_str = result_str.replace('“', '')
                            result_str = result_str.replace('《', '')
                            result_str = result_str.replace('》', '')
                            result_str = result_str.replace(' ( ', '(')
                            result_str = result_str.replace(' \" ', '')
                            result_str = result_str.replace('\"', '')
                            result_str = result_str.replace('.', '')
                            result_str = result_str.replace('[[', '')
                            result_str = result_str.replace(']]', '')
                            result_str = result_str.replace(',', '')
                            result_str = result_str.replace('\'\'', '')

                            result_str = Bracket_Processing4(result_str, '{{', '}}')
                            result_str = Bracket_Processing(result_str, '「', '」')
                            result_str = Bracket_Processing3(result_str, ' (', ')')
                            result_str = Bracket_Processing(result_str, '(', ')')
                            result_str = Bracket_Processing(result_str, '<', '>')
                            result_str = Bracket_Processing(result_str, '[', ']')
                            result_str = Bracket_Processing2(result_str, '|', ' ')

                            #print('----------------------------')
                            #print(text.text)
                            #print('----------------------------')
                            #print(result_str)
                            #input()
                            TK = result_str.split('\n')
                            output_file2.write(str(title) + '\n')
                            for k in range(len(TK)):
                                if TK[k] != '':
                                    if len(TK[k]) > 0:
                                        if check_hangeul(TK[k][0]) is True:
                                            output_file2.write(TK[k])
                                            output_file2.write('\n')
                                            #print("!!")
                                            #print(TK[k])
                                            #input()
                                        else:
                                            0
                                            #print("!!")
                                            #print(result_str)
                                            #input()
                            output_file2.write('\a')
                        except:
                            0
output_file2.close()
