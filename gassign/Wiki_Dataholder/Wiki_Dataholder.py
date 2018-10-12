
import codecs
import numpy


class Data_holder:
    def find_all(self, a_str, sub):
        start = 0
        while True:
            start = a_str.find(sub, start)
            if start == -1: return
            yield start
            start += len(sub)  # use start += 1 to find overlapping matches

    def __init__(self):
        print('data processing...')

        self.whole_batch_index = 0
        self.Batch_Index = 0

        self.Batch_Size = 100
        self.Total_Batch_Size = 0

        self.P_Length = 200
        self.Q_Length = 20
        self.Word_Embedding_Dimension = 200

        #source data prep-rocessing
        self.Labels_start = []
        self.Labels_stop = []
        self.Questions = []
        self.Paragraphs = []
        self.Paragraphs_ = []

        self.exo_Labels_start = []
        self.exo_Labels_stop = []
        self.exo_Questions = []
        self.exo_Paragraphs = []

        """
        korean embedding
        """
        #word2vec_kor = codecs.open('C:\\Users\\Administrator\\Desktop\\qadataset\\kor_word2vec_100d', 'r', 'utf-8')
        word2vec_kor = codecs.open('kor_word2vec_200d', 'r', 'utf-8')

        self.kor_words = []
        self.kor_vectors = []

        arr = []
        for i in range(100):
            pm = 1

            if i % 2 == 0:
                pm = -1

            arr.append(0.002 * pm * i)
        self.kor_words.append('#END')
        self.kor_vectors.append(arr)

        arr = []
        for i in range(100):
            pm = 1

            if i % 2 == 0:
                pm = 0.1
            elif i % 3 == 0:
                pm = -1

            arr.append(0.1 * pm)
        self.kor_words.append('#START')
        self.kor_vectors.append(arr)

        for line in word2vec_kor:
            tokens = line.split('\t')
            self.kor_words.append(tokens.pop(0))
            self.kor_vectors.append(tokens)

        word = self.kor_words[0]

        self.kor_dictionary = numpy.array(self.kor_words)
        self.word2vec_arg_index = self.kor_dictionary.argsort()
        self.kor_dictionary.sort()

        """
        source dataset loading
        """
        label_file = open('gen_label_model_final', 'r', encoding='utf-8')
        question_file = open('gen_question_final', 'r', encoding='utf-8')
        sentence_file = open('gen_paragraph__p__pre__r_____model_final', 'r', encoding='utf-8')
        sentence_file_ = open('gen_paragraph__p__pre__r_____model_temp', 'r', encoding='utf-8')

        Labels_index = label_file.read().split('\a')
        Questions = question_file.read().split('\a')
        Paragraphs = sentence_file.read().split('\a')
        Paragraphs_ = sentence_file_.read().split('\a')
        """
        print(len(Paragraphs))
        print(len(Paragraphs_))
        while(True):
            print('text')
            inp = int(input())
            print(Paragraphs[inp])
            print(Paragraphs_[inp])
        """
        for i in range(len(Labels_index) - 1):
            self.Labels_start.append(int(Labels_index[i].split('#')[0]) - 1)
            self.Labels_stop.append(int(Labels_index[i].split('#')[1]) - 1)
            self.Questions.append(str(Questions[i]).strip())
            self.Paragraphs.append(str(Paragraphs[i]).strip())
            self.Paragraphs_.append(str(Paragraphs_[i]).strip())

        self.Paragraphs_Input = numpy.zeros(shape=[len(self.Paragraphs), self.P_Length], dtype=numpy.int32)
        self.Questions_Input = numpy.zeros(shape=[len(self.Questions), self.Q_Length], dtype=numpy.int32)
        self.Start_Label_Input = numpy.zeros(shape=[len(self.Paragraphs), 1], dtype=numpy.int32)
        self.Stop_Label_Input = numpy.zeros(shape=[len(self.Paragraphs), 1], dtype=numpy.int32)

        for i in range(len(self.Paragraphs)):
            #paragraph
            length = self.P_Length
            TK = self.Paragraphs[i].split()
            if len(TK) < length:
                length = len(TK)

            for j in range(length):
                index = self.kor_dictionary.searchsorted(TK[j])
                if index >= self.kor_dictionary.shape[0]:
                    index = 0
                if self.kor_dictionary[index] == TK[j]:
                    self.Paragraphs_Input[i, j] = self.word2vec_arg_index[index]

            #question
            length = self.Q_Length
            TK = self.Questions[i].split()
            if len(TK) < length:
                length = len(TK)

            for j in range(length):
                index = self.kor_dictionary.searchsorted(TK[j])
                if index >= self.kor_dictionary.shape[0]:
                    index = 0
                if self.kor_dictionary[index] == TK[j]:
                    self.Questions_Input[i, j] = self.word2vec_arg_index[index]

            #label
            self.Start_Label_Input[i, 0] = self.Labels_start[i]
            self.Stop_Label_Input[i, 0] = self.Labels_stop[i]

        print('wiki data length:', len(self.Labels_stop), len(self.Paragraphs))
        ###########################

        """
        target data processing
        """
        label_file = open('exo_label_', 'r', encoding='utf-8')
        question_file = open('exo_question__', 'r', encoding='utf-8')
        sentence_file = open('exo_paragraph__', 'r', encoding='utf-8')

        exo_Labels_index = label_file.read()
        exo_Labels_index = exo_Labels_index[0:len(exo_Labels_index) - 1].split('\a')
        exo_Questions = question_file.read()
        exo_Questions = exo_Questions[0:len(exo_Questions) - 1].split('\n')
        exo_Paragraphs = sentence_file.read()
        exo_Paragraphs = exo_Paragraphs[0:len(exo_Paragraphs) - 3].split('@#!')

        self.exo_Questions = exo_Questions
        self.exo_Paragraphs = exo_Paragraphs

        exo_start_label = []
        exo_stop_label = []

        for i in range(len(exo_Labels_index)):
            TK = exo_Labels_index[i].split('#')
            exo_start_label.append(int(TK[0]))
            exo_stop_label.append((int(TK[1])))

        self.exo_Labels_start = exo_start_label
        self.exo_Labels_stop = exo_stop_label

        print('exobrain qa dataset length:', len(exo_Paragraphs))

        self.Exo_Paragraphs_Input = numpy.zeros(shape=[len(exo_Paragraphs), self.P_Length], dtype=numpy.int32)
        self.Exo_Questions_Input = numpy.zeros(shape=[len(exo_Questions), self.Q_Length], dtype=numpy.int32)
        self.Exo_Start_Label_Input = numpy.zeros(shape=[len(exo_Paragraphs), 1], dtype=numpy.int32)
        self.Exo_Stop_Label_Input = numpy.zeros(shape=[len(exo_Paragraphs), 1], dtype=numpy.int32)

        for i in range(len(exo_Paragraphs)):
            #paragraph
            length = self.P_Length
            TK = exo_Paragraphs[i].split()
            if len(TK) < length:
                length = len(TK)

            for j in range(length):
                index = self.kor_dictionary.searchsorted(TK[j])
                if self.kor_dictionary[index] == TK[j]:
                    self.Exo_Paragraphs_Input[i, j] = self.word2vec_arg_index[index]

            #question
            length = self.Q_Length
            TK = exo_Questions[i].split()
            if len(TK) < length:
                length = len(TK)

            for j in range(length):
                index = self.kor_dictionary.searchsorted(TK[j])
                if self.kor_dictionary[index] == TK[j]:
                    self.Exo_Questions_Input[i, j] = self.word2vec_arg_index[index]

            #label
            self.Exo_Start_Label_Input[i, 0] = exo_start_label[i]
            self.Exo_Stop_Label_Input[i, 0] = exo_stop_label[i]

            ###########################
            #input loading complete
            ##########################

        self.Test_Batch_index = self.Paragraphs_Input.shape[0] - 2000
        self.Test_Batch_index2 = self.Exo_Paragraphs_Input.shape[0] - 200

        #self.Test_Batch_index = 0
        #self.Test_Batch_index2 = 0

    def get_Next_Batch(self):
        source_batch_size = 45
        target_batch_size = 1

        #Source Data
        np_range = numpy.arange(0, self.Paragraphs_Input.shape[0] - 2000, dtype='i')
        numpy.random.shuffle(np_range)

        source_paragraph = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)
        source_question = numpy.zeros(shape=[source_batch_size, self.Q_Length], dtype=numpy.int32)
        source_start_label = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)
        source_stop_label = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)

        for i in range(source_batch_size):
            source_paragraph[i] = self.Paragraphs_Input[np_range[i]]
            source_question[i] = self.Questions_Input[np_range[i]]
            source_start_label[i, self.Start_Label_Input[np_range[i]]] = 1
            source_stop_label[i, self.Stop_Label_Input[np_range[i]]] = 1

        # Target Data
        np_range = numpy.arange(0, self.Exo_Paragraphs_Input.shape[0] - 200, dtype='i')
        numpy.random.shuffle(np_range)

        target_paragraph = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)
        target_question = numpy.zeros(shape=[target_batch_size, self.Q_Length], dtype=numpy.int32)
        target_start_label = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)
        target_stop_label = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)

        for i in range(target_batch_size):
            target_paragraph[i] = self.Exo_Paragraphs_Input[np_range[i]]
            target_question[i] = self.Exo_Questions_Input[np_range[i]]
            target_start_label[i, self.Exo_Start_Label_Input[np_range[i]]] = 1
            target_stop_label[i, self.Exo_Stop_Label_Input[np_range[i]]] = 1

        return source_paragraph, source_question, source_start_label, source_stop_label, target_paragraph, target_question, target_start_label, target_stop_label

    def get_Test_Source_Batch(self):
        source_batch_size = 40

        #Source Data
        if self.Test_Batch_index + source_batch_size > self.Paragraphs_Input.shape[0]:
            return 0, 0, 0, 0, 0

        np_range = numpy.arange(self.Test_Batch_index, self.Test_Batch_index + source_batch_size, dtype='i')

        source_paragraph = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)
        source_question = numpy.zeros(shape=[source_batch_size, self.Q_Length], dtype=numpy.int32)
        source_start_label = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)
        source_stop_label = numpy.zeros(shape=[source_batch_size, self.P_Length], dtype=numpy.int32)

        for i in range(source_batch_size):
            source_paragraph[i] = self.Paragraphs_Input[np_range[i]]
            source_question[i] = self.Questions_Input[np_range[i]]
            source_start_label[i, self.Labels_start[np_range[i]]] = 1
            source_stop_label[i, self.Labels_stop[np_range[i]]] = 1

        self.Test_Batch_index += source_batch_size

        return source_paragraph, source_question, source_start_label, source_stop_label, np_range

    def get_Test_Target_Batch(self):
        target_batch_size = 40

        # Target Data
        if self.Test_Batch_index2 + target_batch_size > self.Exo_Paragraphs_Input.shape[0]:
            return 0, 0, 0, 0, 0

        np_range = numpy.arange(self.Test_Batch_index2, self.Test_Batch_index2 + target_batch_size, dtype='i')

        target_paragraph = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)
        target_question = numpy.zeros(shape=[target_batch_size, self.Q_Length], dtype=numpy.int32)
        target_start_label = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)
        target_stop_label = numpy.zeros(shape=[target_batch_size, self.P_Length], dtype=numpy.int32)

        for i in range(target_batch_size):
            target_paragraph[i] = self.Exo_Paragraphs_Input[np_range[i]]
            target_question[i] = self.Exo_Questions_Input[np_range[i]]
            target_start_label[i, self.exo_Labels_start[np_range[i]]] = 1
            target_stop_label[i, self.exo_Labels_stop[np_range[i]]] = 1

        self.Test_Batch_index2 += target_batch_size

        return target_paragraph, target_question, target_start_label, target_stop_label, np_range