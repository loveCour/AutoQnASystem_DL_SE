# -*- coding: utf-8 -*-

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

    if a <= z[0] <= b:
        #print('!!')
        #print(c)
        #input()
        return True
    elif e <= z[0] <= f:
        return True
    else:
        c1 = 0
        c2 = 0

        for i in range(len(z)):
            if a <= z[i] <= b:
                c1 += 1
            if c <= z[i] <= d:
                c2 += 1

        if c1 > c2:
            return True

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
    result_ = Bracket_Processing6(result_, '<ref', '</ref>')
    result_ = Bracket_Processing(result_, '(', ')')
    # result_ = Bracket_Processing4_(result_, '[[', ']]')
    result_ = Bracket_Processing5(result_, '[[', '|', ']]')
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
    #result_ = result_.replace('.', '')
    result_ = result_.replace('[[', '')
    result_ = result_.replace(']]', '')
    result_ = result_.replace(',', '')
    result_ = result_.replace('\'\'', '')

    return result_

output_file = open('wiki_info', 'w', encoding='utf-8')

registered_words = []
register_text = []

title = ''

ind = 0

# 11개 split file
for a in range(1):
    print(a, 'processing...')

    tree = ET.parse('wikisplit' + str(a))
    root = tree.getroot()

    for page in root:
        check_ok = True

        for tags in page:
            if tags.tag == 'title':
                title = tags.text

                type_check_Token = '틀:'

                if len(title) > len(type_check_Token):
                    if title[0:len(type_check_Token)] == type_check_Token:
                        title = title[2:len(title) - 2]

            if tags.tag == 'revision' and check_ok is True:
                for text in tags:
                    if text.tag == 'text':
                        if not(text.text is None):
                            temp_text = text.text
                            a = temp_text.find('{{')
                            b = temp_text.find('\n}}')
                            if a != -1 and b != -1:
                                temp_text = temp_text[a:b + 3]

                            sentences = temp_text.split('\n')
                            result_str = ''

                            for i in range(len(sentences)):
                                if len(sentences[i]) > 1:
                                    if sentences[i][0] == '|':
                                        result_str += sentences[i] + '\n'

                            registered_words.append(title)
                            register_text.append(result_str)
                            if ind % 100 == 0:
                                print(title, ind)
                            ind += 1

registered_words = np.array(registered_words, dtype='<U30')
dictionary_index = registered_words.argsort()
registered_words.sort()

"""
i = 0
while True:
    print(register_text[i])
    i += 1
    input()
"""

new_words = []
new_paragraphs = []

new_words.append(registered_words[0])
new_paragraphs.append(register_text[dictionary_index[0]])
for i in range(1, len(register_text)):
    if registered_words[i - 1] == registered_words[i]:
        new_paragraphs[len(new_paragraphs) - 1] = new_paragraphs[len(new_paragraphs) - 1] + \
                                                  '\n' + register_text[dictionary_index[i]]
    else:
        new_words.append(registered_words[i])
        new_paragraphs.append(register_text[dictionary_index[i]])

for i in range(len(new_words)):
    info_line = new_paragraphs[i]
    info_line = info_line.replace(' = ', '=')
    info_line = info_line.replace('| ', '')
    info_line = info_line.replace('|', '')
    info_line = info_line.replace('[[', '')
    info_line = info_line.replace(']]', '')
    info_line = Bracket_Processing(info_line, '<', '>')
    info_line = Bracket_Processing(info_line, '(', ')')

    output_file.write(new_words[i])
    output_file.write('\n')
    output_file.write(info_line)
    output_file.write('\a')

    if i % 2000 == 0:
        print(i)

output_file.close()
