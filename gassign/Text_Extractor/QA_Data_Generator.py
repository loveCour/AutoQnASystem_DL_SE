import numpy as np
import codecs
import pandas

class Data_Generator:
    def check_hangeul_seq(self, z):
        a = '가'
        b = '힣'
        c = 'A'
        d = 'z'
        e = '0'
        f = '9'

        result = ''
        for i in range(len(z)):
            if a <= z[i] <= b:
                result += z[i]
            elif c <= z[i] <= d:
                result += z[i]
            elif e <= z[i] <= f:
                result += z[i]
            elif z[i] == '\n' or z[i] == ' ':
                result += z[i]

        return result

    def check_hangeul(self, z):
        a = '가'
        b = '힣'
        e = '0'
        f = '9'

        if a <= z <= b:
            return True
        elif e <= z <= f:
            return True
        else:
            # print('@@')
            # print(c)
            # input()
            return False

    def Bracket_Processing(self, string, start, end):
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

    def check_time(self, string):
        TK = string.split()
        for i in range(len(TK)):
            for j in range(len(TK[i]) - 1):
                if not ('0' <= TK[i][j] <= '9'):
                    return False

        return True

    def check_number(self, string):
        for i in range(len(string)):
            if not ('0' <= string[i] <= '9'):
                return False
        return True

    def check_name(self, string):
        a = self.names.searchsorted(string)

        if a >= self.names.shape[0]:
            return False

        if self.names[a] == string:
            return True
        else:
            return False

    def check_place(self, string):
        a = self.places.searchsorted(string)
        if a >= self.places.shape[0]:
            return False
        if self.places[a] == string:
            return True

        for i in range(self.places.shape[0]):
            TK2 = self.places[i].split()
            is_okay = True

            count = 0

            for j in range(len(TK2)):
                a = string.find(TK2[j])
                if a != -1:
                    count += 1

            if count > 1:
                return True

        return False

    def checkTrait(self, c):
        return (int((ord(c) - 0xAC00) % 28) != 0)

    def generate(self, title, info, answer, paragraphs, para_index):
        if self.checkTrait(info[len(info) - 1]) is True:
            lang = '은'
        else:
            lang = '는'
        lang = ''

        if self.check_number(answer) is True:
            question_gen = title + ' ' + info + lang + ' 몇'
        elif self.check_time(answer) is True:
            question_gen = title + ' ' + info + lang + ' 언제'
        elif self.check_name(answer) is True:
            question_gen = title + ' ' + info + lang + ' 누구'
        elif self.check_place(answer) is True:
            question_gen = title + ' ' + info + lang + ' 어디'
        else:
            question_gen = title + ' ' + info + lang + ''

        paragraph_TK_ = paragraphs.split('\n')
        paragraph_TK = paragraphs.split('\n')
        answer_TK = answer.split()
        start_word = answer_TK[0]
        end_word = answer_TK[len(answer_TK) - 1]

        line_TK = paragraph_TK[para_index].split()
        for i, word in enumerate(line_TK):
            a = word.find(start_word)
            b = word.find(end_word)

            TKs = ''
            new_line = ''

            if a != -1:
                TKs = '###!'
            if b != -1:
                TKs = '!!!#'

            if a != -1 or b != -1:
                for j in range(len(line_TK)):
                    if j == i:
                        new_line += TKs + ' '
                    else:
                        new_line += line_TK[j] + ' '
                paragraph_TK[para_index] = new_line[0: len(new_line) - 1]
                line_TK = paragraph_TK[para_index].split()

        temp_Paragraph = ''
        Paragraph = ''

        for i, line in enumerate(paragraph_TK):
            temp_Paragraph += line + '. '
            Paragraph += paragraph_TK_[i] + '. '

        TK = temp_Paragraph.split()

        start_index = -1
        end_index = -1
        for i in range(len(TK)):
            a = TK[i].find('###!')
            b = TK[i].find('!!!#')

            if a != -1:
                start_index = i
            if b != -1:
                end_index = i

        if start_index == -1:
            start_index = end_index

        """
        print(start_index, end_index)
        print(paragraph_TK_[para_index])
        print(answer)
        print(info)
        print(temp_Paragraph)
        print(start_word, end_word)
        print(question_gen)
        input()
        """

        if start_index != -1 and end_index != -1:
            self.paragraph_file.write(self.check_hangeul_seq(paragraphs))
            self.paragraph_file.write('\n')
            self.paragraph_file.write('@#!')
            self.paragraph_file.write('\n')

            self.question_file.write(self.check_hangeul_seq(question_gen))
            self.question_file.write('\a')

            line = str(answer) + ',' + str(para_index)
            self.label_file.write(line)
            self.label_file.write('\a')

            return True
        else:

            return False

    def __init__(self):
        self.question_file = open('gen_question', 'w', encoding='utf-8')
        self.paragraph_file = open('gen_paragraph', 'w', encoding='utf-8')
        self.label_file = open('gen_label', 'w', encoding='utf-8')

        name_file = open('hw_names', 'r', encoding='utf-8')
        places_file = open('hw_places', 'r', encoding='utf-8')

        self.names = np.array(name_file.read().split('\n'), dtype='<U20')
        self.names.sort()
        self.places = np.array(places_file.read().split('\n'), dtype='<U20')
        self.places.sort()

        exclusion_list = []
        exclusion_list.append('이름')
        exclusion_list.append('제목')
        exclusion_list.append('날짜')
        exclusion_list.append('연도')
        exclusion_list.append('국가')
        exclusion_list.append('언어')
        exclusion_list.append('시대')
        exclusion_list.append('음악')

        paragraph_file = open('wiki_corpus', 'r', encoding='utf-8')
        rule_file = open('wiki_info', 'r', encoding='utf-8')
        # 정보가 들어있는 텍스트파일

        exo_Questions = []
        exo_Titles = []

        exobrain_data1 = pandas.read_excel('exo1.xlsx')
        temp = exobrain_data1['질문']
        temp2 = exobrain_data1['위키피디아 제목']

        for i in range(len(temp)):
            a = str(temp[i]).find(str(temp2[i]))
            if a != -1:
                exo_Questions.append(str(temp[i]).replace('?', ''))
                exo_Titles.append(str(temp2[i]))
        exobrain_data1 = pandas.read_excel('exo3.xlsx')
        temp = exobrain_data1['질문']
        temp2 = exobrain_data1['위키피디아 제목']

        for i in range(len(temp)):
            a = str(temp[i]).find(str(temp2[i]))
            if a != -1:
                exo_Questions.append(str(temp[i]).replace('?', ''))
                exo_Titles.append(str(temp2[i]))

        print(len(exo_Questions))
        print(len(exo_Titles))

        #엑소브레인 데이터셋

        paragraph = paragraph_file.read().split('\a')
        information = rule_file.read().split('\a')

        print(len(paragraph), len(information))

        Dictionary = []
        Paragraphs = []
        """
        a = self.check_place('대한민국')
        if a is True:
            print('ok')
        else:
            print('no')
        input()
        """
        for i in range(len(information)):
            TK = paragraph[i].split('\n')

            Dictionary.append(TK[0])
            result_str = ''
            for j in range(1, len(TK)):
                TK[j] += ' '
                TK2 = TK[j].split('. ')

                for k in range(len(TK2) - 1):
                    result_str += TK2[k] + '\n'

            Paragraphs.append(result_str)

        Dictionary = np.array(Dictionary, dtype='<U20')
        Dictionary_Index = Dictionary.argsort()
        Dictionary.sort()

        count = 0
        check_count = 0

        for inform in information:
            check_count += 1
            print(check_count, count)

            lines = inform.split('\n')

            title = lines[0]
            title = self.Bracket_Processing(title, '(', ')')

            title_index = Dictionary_Index[Dictionary.searchsorted(title)]

            paragraph_text = Paragraphs[title_index].split('\n')

            for i in range(1, len(lines)):
                info_line = lines[i]
                answer = info_line.split('=')

                if len(answer) > 1:
                    answer[0] = answer[0].strip()
                    answer[1] = answer[1].strip()

                    is_okay = True
                    for e_l in exclusion_list:
                        if str(answer[0]) == str(e_l):
                            is_okay = False

                    if self.check_hangeul(answer[0]) is False:
                        is_okay = False

                    is_Continue = True

                    if is_okay is True:
                        is_okay3 = True

                        for index, paragraph_line in enumerate(paragraph_text):
                            if is_Continue is False:
                                is_Continue = True
                                break

                            if len(paragraph_text) > 2 and len(answer[1]) > 1:
                                is_okay1 = True
                                tk1 = answer[1].split()
                                for j in range(len(tk1)):
                                    a = paragraph_line.find(tk1[j])
                                    if a == -1:
                                        is_okay1 = False

                                a = paragraph_line.find(answer[0])
                                if a == -1:
                                    is_okay1 = False

                                if is_okay1 is True:
                                    is_okay3 = False
                                    is_Continue = False

                                    check = self.generate(title, answer[0], answer[1], Paragraphs[title_index], index)
                                    if check is True:
                                        count += 1
                                    break

                        if is_okay3 is True:
                            for index, paragraph_line in enumerate(paragraph_text):
                                if is_Continue is False:
                                    break

                                if len(paragraph_text) > 2 and len(answer[1]) > 1 and is_Continue is True:
                                    paragraph_line_TK = paragraph_line.split()
                                    tk1 = answer[1].split()

                                    is_okay1 = True

                                    for j in range(len(paragraph_line_TK) - len(tk1) + 1):
                                        is_okay2 = True

                                        for k in range(0, len(tk1)):
                                            a = paragraph_line_TK[j + k].find(tk1[k])
                                            if a == -1:
                                                is_okay2 = False

                                        if is_okay2 is True:
                                            self.generate(title, answer[0], answer[1], Paragraphs[title_index], index)
                                            is_Continue = False
                                            count += 1
                                            break

                                    if is_Continue is False:
                                        break
        print(count)