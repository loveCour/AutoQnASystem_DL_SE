import numpy as np

words_file = open('master_dictionary', 'r', encoding='utf-8')
words_order_file = open('master_dictionary_order', 'r', encoding='utf-8')

dictionary = words_file.read().split('\n')
dictionary_order = words_order_file.read().split('\n')

file_name = 'gen_paragraph__p__pre__r_'
recover_input = open(file_name, 'r', encoding='utf-8')
whole_text = recover_input.read()

is_recover = True

if is_recover is True:
    for i in range(len(dictionary_order)):
        if i % 10 == 0:
            print(i, len(dictionary_order))

        index = len(dictionary) - 1 - i

        whole_text = whole_text.replace('@' + str(index) + '#', dictionary[index])
else:
    for i in range(len(dictionary_order) - 1):
        if i % 10 == 0:
            print(i, len(dictionary_order))
        index = len(dictionary) - 1 - i
        arg_index = int(dictionary_order[index])

        whole_text = whole_text.replace(dictionary[arg_index], '@' + str(arg_index) + '#')

result_file = open(file_name + '_', 'w', encoding='utf-8')
result_file.write(whole_text)
result_file.close()
