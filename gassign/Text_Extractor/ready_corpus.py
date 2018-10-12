import numpy as np


def check_time(string):
    if len(string) < 2:
        return False

    dics = ['년', '월', '일', '시', '분', '초']

    is_Dic = False

    if len(string) > 2:
        for dic in dics:
            if string[len(string) - 2] == dic:
                is_Dic = True

    if is_Dic is True:
        for i in range(len(string) - 2):
            if not ('0' <= string[i] <= '9'):
                return False

    if is_Dic is True:
        return True

    for dic in dics:
        if string[len(string) - 1] == dic:
            is_Dic = True

    if is_Dic is False:
        return False

    if is_Dic is True:
        for i in range(len(string) - 1):
            if not ('0' <= string[i] <= '9'):
                return False

    return True


def check_number(string):
    if len(string) < 1:
        return False

    for i in range(len(string)):
        if not ('0' <= string[i] <= '9'):
            return False
    return True

is_recovery = False

words_file = open('master_dictionary', 'r', encoding='utf-8')
words_order_file = open('master_dictionary_order', 'r', encoding='utf-8')

names_file = open('master_names', 'r', encoding='utf-8')
names_order_file = open('master_names_order', 'r', encoding='utf-8')

Dictionary = words_file.read().split('\n')
Dictionary_order = words_order_file.read().split('\n')

Names = names_file.read().split('\n')
Names_order = names_order_file.read().split('\n')

file_name = 'corpus_'

dataset_file = open(file_name, 'r', encoding='utf-8')

whole_text = dataset_file.read()
whole_text1 = whole_text.strip()
whole_text2 = whole_text.strip()

print(len(whole_text1))
print(len(whole_text2))

#original_input = open(file_name + '_', 'w', encoding='utf-8')
model_input = open(file_name + '_model', 'w', encoding='utf-8')
#symbol_input = open(file_name + '_symbol', 'w', encoding='utf-8')

#name: @#@
#time: ###
#number: #@#

if is_recovery is True:
    0
else:
    """
    for i in range(len(Names)):
        if i % 50 == 0:
            print('loop1...', i, '/', len(Names))

        index = len(Names) - 1 - i
        arg_index = int(Names_order[index])

        whole_text1 = whole_text1.replace(Names[arg_index], '@#@')
    """
    lines = whole_text1.split('\n')
    for k in range(len(lines)):
        if k % 1000 == 0:
            print('loop2...', k, '/', len(lines))

        TK = lines[k].split(' ')

        for j in range(len(TK)):
            if check_time(TK[j]) is True:
                TK[j] = '###'
            elif check_number(TK[j]) is True:
                TK[j] = '#@#'

        model_input.write(TK[0])
        for j in range(1, len(TK)):
            line = ' ' + TK[j]
            model_input.write(line)
        model_input.write('\n')

    """
    for i in range(len(Names)):
        if i % 1000 == 0:
            print('loop4...', i, '/', len(Names))

        index = len(Names) - 1 - i
        arg_index = int(Names_order[index])

        whole_text2 = whole_text2.replace(Names[arg_index], '@ ' + str(arg_index) + ' #')
    """
    #model_input.write(whole_text1)
    #symbol_input.write(whole_text2)

    model_input.close()
    #symbol_input.close()