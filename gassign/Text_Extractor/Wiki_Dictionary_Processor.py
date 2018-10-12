import xml.etree.ElementTree as ET
import numpy as np


def cut_line(line):
    for i in range(len(line)):
        if line[len(line) - 1] == '\n':
            return str(line[0:len(line) - 1])

    return line


def bracket_processign(line):
    for i in range(len(line)):
        if line[i] == '(':
            return str(line[0:i])

    return line


def slice_processign(line):
    for i in range(len(line)):
        if line[len(line) - 1] == '과':
            return str(line[0:len(line) - 1])

    return line


def slice_processign2(line):
    for i in range(len(line)):
        if line[i] == ':':
            return str(line[i + 1:len(line)])

    return line


def trim(line):
    if len(line) > 0:
        if line[len(line) - 1] == ' ':
            return trim(str(line[0:len(line) - 1]))

    return line


def trim2(line):
    if len(line) > 0:
        if line[0] == ' ':
            return trim2(str(line[0:len(line) - 1]))

    return line


def check(line):
    if len(line) == 0:
        return False

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

"""bracket processing functions"""


WIKI_Words = []

for a in range(11):
    print('processing', a, 'file...')

    tree = ET.parse('wikisplit' + str(a))
    root = tree.getroot()

    for page in root:
        check_ok = True

        for tags in page:
            if tags.tag == 'title':
                title = tags.text
                if check(title):
                    WIKI_Words.append(trim2(trim(slice_processign2(slice_processign(bracket_processign(title))))))

words_array = np.zeros(shape=[len(WIKI_Words)], dtype='<U30')
for i in range(len(WIKI_Words)):
    words_array[i] = WIKI_Words[i]

words_array.sort()

result_file = open('Wiki_Dictionary', mode='w', encoding='utf8')

for i in range(len(WIKI_Words) - 1):
    if words_array[i] != words_array[i + 1]:
        result_file.write(words_array[i])
        result_file.write('\n')
result_file.write(words_array[len(WIKI_Words) - 1])
result_file.write('\n')
result_file.close()
