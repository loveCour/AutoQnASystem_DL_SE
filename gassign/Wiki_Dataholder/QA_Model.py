import tensorflow as tf
import numpy as np

from utils import *
from layers import *


class my_QA_Net:
    def __init__(self, c, q, c_maxlen, q_maxlen):
        self.dropout = 0.0
        self.c_mask = tf.cast(c, tf.bool)
        self.q_mask = tf.cast(q, tf.bool)
        self.c_len = tf.reduce_sum(tf.cast(self.c_mask, tf.int32), axis=1)
        self.q_len = tf.reduce_sum(tf.cast(self.q_mask, tf.int32), axis=1)

        self.c_maxlen = c_maxlen
        self.q_maxlen = q_maxlen

    def create_graph(self, c_emb, q_emb, d=96, nh=1, reuse=False):
        with tf.variable_scope("Embedding_Encoder_Layer"):
            c = residual_block(c_emb,
                               num_blocks=1,
                               num_conv_layers=4,
                               kernel_size=7,
                               mask=None,
                               num_filters=d,
                               num_heads=nh,
                               seq_len=self.c_len,
                               scope="Encoder_Residual_Block",
                               bias=False,
                               dropout=self.dropout,
                               reuse=reuse)
            q = residual_block(q_emb,
                               num_blocks=1,
                               num_conv_layers=4,
                               kernel_size=7,
                               mask=None,
                               num_filters=d,
                               num_heads=nh,
                               seq_len=self.q_len,
                               scope="Encoder_Residual_Block",
                               reuse=True,  # Share the weights between passage and question
                               bias=False,
                               dropout=self.dropout)

        with tf.variable_scope("Context_to_Query_Attention_Layer", reuse=reuse):
            # C = tf.tile(tf.expand_dims(c,2),[1,1,self.q_maxlen,1])
            # Q = tf.tile(tf.expand_dims(q,1),[1,self.c_maxlen,1,1])
            # S = trilinear([C, Q, C*Q], input_keep_prob = 1.0 - self.dropout)
            S = optimized_trilinear_for_attention([c, q], self.c_maxlen, self.q_maxlen,
                                                  input_keep_prob=1.0 - self.dropout)
            mask_q = tf.expand_dims(self.q_mask, 1)
            S_ = tf.nn.softmax(mask_logits(S, mask=mask_q))
            mask_c = tf.expand_dims(self.c_mask, 2)
            S_T = tf.transpose(tf.nn.softmax(mask_logits(S, mask=mask_c), dim=1), (0, 2, 1))
            self.c2q = tf.matmul(S_, q)
            self.q2c = tf.matmul(tf.matmul(S_, S_T), c)
            attention_outputs = [c, self.c2q, c * self.c2q, c * self.q2c]

        with tf.variable_scope("Model_Encoder_Layer", reuse=reuse):
            inputs = tf.concat(attention_outputs, axis=-1)
            self.enc = [conv(inputs, d, name="input_projection")]
            for i in range(3):
                if i % 2 == 0:  # dropout every 2 blocks
                    self.enc[i] = tf.nn.dropout(self.enc[i], 1.0 - self.dropout)
                self.enc.append(
                    residual_block(self.enc[i],
                                   num_blocks=7,
                                   num_conv_layers=2,
                                   kernel_size=5,
                                   mask=self.c_mask,
                                   num_filters=d,
                                   num_heads=nh,
                                   seq_len=self.c_len,
                                   scope="Model_Encoder",
                                   bias=False,
                                   reuse=True if i > 0 else None,
                                   dropout=self.dropout)
                )

        with tf.variable_scope("Output_Layer", reuse=reuse):
            start_logits = tf.squeeze(
                conv(tf.concat([self.enc[1], self.enc[2]], axis=-1), 1, bias=False, name="start_pointer"), -1)
            end_logits = tf.squeeze(
                conv(tf.concat([self.enc[1], self.enc[3]], axis=-1), 1, bias=False, name="end_pointer"), -1)
            self.logits = [mask_logits(start_logits, mask=self.c_mask),
                           mask_logits(end_logits, mask=self.c_mask)]

            logits1, logits2 = [l for l in self.logits]

            outer = tf.matmul(tf.expand_dims(tf.nn.softmax(logits1), axis=2),
                              tf.expand_dims(tf.nn.softmax(logits2), axis=1))
            outer = tf.matrix_band_part(outer, 0, 30)

            return logits1, logits2


class QA_Net:
    def __init__(self, c, q, c_maxlen, q_maxlen):
        self.dropout = 0.0
        self.c_mask = tf.cast(c, tf.bool)
        self.q_mask = tf.cast(q, tf.bool)
        self.c_len = tf.reduce_sum(tf.cast(self.c_mask, tf.int32), axis=1)
        self.q_len = tf.reduce_sum(tf.cast(self.q_mask, tf.int32), axis=1)

        self.c_maxlen = c_maxlen
        self.q_maxlen = q_maxlen

    def create_graph(self, c_emb, q_emb, p_length, q_length, d=600, nh=1, reuse=False):
        with tf.variable_scope("Embedding_Encoder_Layer"):
            x_p = residual_conv_block(c_emb, 3, 2, 3, d, False, p_length, 8, 'res_block', True, 0.0,
                                    False, reuse)

            x_q = residual_conv_block(q_emb, 3, 2, 3, d, False, q_length, 8, 'res_block', True, 0.0,
                                    False, True)

        with tf.variable_scope("bi_att", reuse=reuse):
            cell_fw_modelling = tf.contrib.rnn.LSTMCell(d)
            cell_bw_modelling = tf.contrib.rnn.LSTMCell(d)

            cell_fw_modelling2 = tf.contrib.rnn.LSTMCell(d)
            cell_bw_modelling2 = tf.contrib.rnn.LSTMCell(d)

            encoding_x_p_ = tf.expand_dims(x_p, axis=2)
            encoding_x_p_ = tf.tile(encoding_x_p_, multiples=[1, 1, q_length, 1])

            encoding_x_q_ = tf.expand_dims(x_q, axis=1)
            encoding_x_q_ = tf.tile(encoding_x_q_, multiples=[1, p_length, 1, 1])

            p_mul_q = tf.multiply(encoding_x_p_, encoding_x_q_)
            concat_data = tf.concat([encoding_x_p_, encoding_x_q_, p_mul_q], axis=3)
            S = Fully_Connected(concat_data, 1, 'att_s', None, reuse=reuse)
            S = tf.squeeze(S, axis=3)

            c2q = tf.matmul(tf.nn.softmax(S, dim=-1), x_q)
            b = tf.nn.softmax(tf.reduce_max(S, axis=2), dim=-1)
            b = tf.expand_dims(b, axis=1)
            q2c = tf.matmul(b, x_p)
            q2c = tf.tile(q2c, [1, p_length, 1])

            G = tf.concat([x_p, c2q, tf.multiply(x_p, c2q), tf.multiply(x_p, q2c)], axis=2)

        with tf.variable_scope("modelling", reuse=reuse):
            (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cell_fw_modelling, cell_bw=cell_bw_modelling, inputs=G,
                sequence_length=seq_length(G), dtype=tf.float32, time_major=False)

            M = tf.concat([fw_outputs, bw_outputs], -1)
            M_state = tf.concat([fw_state[-1], bw_state[-1]], -1)

            G_M = tf.concat([G, M], axis=2)
            G_M_ = Fully_Connected(G_M, 1, name='Prediction1', activation=None)
            G_M_ = tf.squeeze(G_M_, axis=-1)

            prediction1 = G_M_

        with tf.variable_scope("modelling2", reuse=reuse):
            (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cell_fw_modelling2, cell_bw=cell_bw_modelling2, inputs=M,
                sequence_length=seq_length(M), dtype=tf.float32, time_major=False)

            M2 = tf.concat([fw_outputs, bw_outputs], -1)
            M2_state = tf.concat([fw_state[-1], bw_state[-1]], -1)
            G_M2 = tf.concat([G, M2], axis=2)
            G_M2_ = Fully_Connected(G_M2, 1, name='Prediction2', activation=None)
            G_M2_ = tf.squeeze(G_M2_, axis=-1)

            prediction2 = G_M2_

        return prediction1, prediction2

        with tf.variable_scope("Model_Encoder_Layer", reuse=reuse):
            inputs = tf.concat(attention_outputs, axis=-1)
            self.enc = [conv(inputs, d, name="input_projection")]
            for i in range(3):
                if i % 2 == 0:  # dropout every 2 blocks
                    self.enc[i] = tf.nn.dropout(self.enc[i], 1.0 - self.dropout)
                self.enc.append(
                    residual_block(self.enc[i],
                                   num_blocks=7,
                                   num_conv_layers=2,
                                   kernel_size=5,
                                   mask=self.c_mask,
                                   num_filters=d,
                                   num_heads=nh,
                                   seq_len=self.c_len,
                                   scope="Model_Encoder",
                                   bias=False,
                                   reuse=True if i > 0 else None,
                                   dropout=self.dropout)
                )

        with tf.variable_scope("Output_Layer", reuse=reuse):
            start_logits = tf.squeeze(
                conv(tf.concat([self.enc[1], self.enc[2]], axis=-1), 1, bias=False, name="start_pointer"), -1)
            end_logits = tf.squeeze(
                conv(tf.concat([self.enc[1], self.enc[3]], axis=-1), 1, bias=False, name="end_pointer"), -1)
            self.logits = [mask_logits(start_logits, mask=self.c_mask),
                           mask_logits(end_logits, mask=self.c_mask)]

            logits1, logits2 = [l for l in self.logits]

            outer = tf.matmul(tf.expand_dims(tf.nn.softmax(logits1), axis=2),
                              tf.expand_dims(tf.nn.softmax(logits2), axis=1))
            outer = tf.matrix_band_part(outer, 0, 30)

            return logits1, logits2

class AOA_Reader:
    def __init__(self):
        self.hidden_size = 200
        self.keep_prob = 0.95

    def create_graph(self, x_p, x_q, p_length, q_length, context_encoding=False, reuse=False, is_training=True):
        d = 296
        x_p.set_shape([None, p_length, d])
        x_q.set_shape([None, q_length, d])

        with tf.variable_scope("context_encoding", reuse=reuse):
            cell_fw_p = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_p = tf.contrib.rnn.DropoutWrapper(cell_fw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_bw_p = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_p = tf.contrib.rnn.DropoutWrapper(cell_bw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_fw_modelling = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_modelling = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling, input_keep_prob=self.keep_prob,
                                                              output_keep_prob=self.keep_prob)
            cell_bw_modelling = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_modelling = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling, input_keep_prob=self.keep_prob,
                                                              output_keep_prob=self.keep_prob)

            cell_fw_modelling2 = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling2, input_keep_prob=self.keep_prob,
                                                               output_keep_prob=self.keep_prob)
            cell_bw_modelling2 = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling2, input_keep_prob=self.keep_prob,
                                                               output_keep_prob=self.keep_prob)

            if context_encoding is True:
                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_p, cell_bw=cell_bw_p, inputs=x_p,
                    sequence_length=seq_length(x_p), dtype=tf.float32, time_major=False)

                encoding_x_p = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_p_state = tf.concat([fw_state[-1], bw_state[-1]], -1)

                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_p, cell_bw=cell_bw_p, inputs=x_q,
                    sequence_length=seq_length(x_q), dtype=tf.float32, time_major=False)

                encoding_x_q = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_q_state = tf.concat([fw_state[-1], bw_state[-1]], -1)
            else:
                encoding_x_p = x_p
                encoding_x_q = x_q

        with tf.variable_scope("Embedding_Encoder_Layer"):
            encoding_x_p = self_attention_block(encoding_x_p, d, p_length, mask=None, num_heads=1,
                                           scope="self_attention_layers", reuse=reuse,
                                           is_training=is_training,
                                           bias=False, dropout=0.05)

            encoding_x_q = self_attention_block(encoding_x_q, d, q_length, mask=None, num_heads=1,
                                           scope="self_attention_layers", reuse=True,
                                           is_training=is_training,
                                           bias=False, dropout=0.05)

        with tf.variable_scope("attention", reuse=reuse):
            H_Q_T = tf.transpose(encoding_x_q, perm=[0, 2, 1])

            M_Vector = tf.matmul(encoding_x_p, H_Q_T)
            Alpha = tf.nn.softmax(M_Vector, dim=1)
            Beta_ = tf.nn.softmax(M_Vector, dim=2)
            Beta = tf.expand_dims(tf.reduce_mean(Beta_, axis=1), dim=-1)

            Att = tf.matmul(Alpha, Beta)
            Att_Vector = tf.tile(Att, [1, 1, d * 1])
            Att_Vector_Representation = tf.multiply(Att_Vector, encoding_x_p)

            Gamma = tf.matmul(Alpha, encoding_x_q)
            Gamma_Vector_Representation = tf.multiply(Gamma, encoding_x_p)

        with tf.variable_scope("attention_W", reuse=reuse) as scope:
            W_H_P = Fully_Connected(encoding_x_p, d * 1, 'weight_paragraph', None, reuse=reuse)
            W_M_Vector = tf.matmul(W_H_P, H_Q_T)

            W_Alpha = tf.nn.softmax(W_M_Vector, dim=1)
            W_Beta_ = tf.nn.softmax(W_M_Vector, dim=2)
            W_Beta = tf.expand_dims(tf.reduce_mean(W_Beta_, axis=1), dim=-1)

            W_Att = tf.matmul(W_Alpha, W_Beta)
            W_Att_Vector = tf.tile(W_Att, [1, 1, d * 1])
            W_Att_Vector_Representation = tf.multiply(W_Att_Vector, encoding_x_p)

            W_Gamma = tf.matmul(W_Alpha, encoding_x_q)
            W_Gamma_Vector_Representation = tf.multiply(W_Gamma, encoding_x_p)

            scope.reuse_variables()

        with tf.variable_scope("attention_W_Q", reuse=reuse) as scope:
            W_H_Q = Fully_Connected(encoding_x_q, d * 1, 'weight_question', None, reuse=reuse)
            W_Q_M_Vector = tf.matmul(encoding_x_p, W_H_Q, transpose_b=True)

            W_Q_Alpha = tf.nn.softmax(W_Q_M_Vector, dim=1)
            W_Q_Beta_ = tf.nn.softmax(W_Q_M_Vector, dim=2)
            W_Q_Beta = tf.expand_dims(tf.reduce_mean(W_Q_Beta_, axis=1), dim=-1)

            W_Q_Att = tf.matmul(W_Q_Alpha, W_Q_Beta)
            W_Q_Att_Vector = tf.tile(W_Q_Att, [1, 1, d * 1])
            W_Q_Att_Vector_Representation = tf.multiply(W_Q_Att_Vector, encoding_x_p)

            W_Q_Gamma = tf.matmul(W_Q_Alpha, encoding_x_q)
            W_Q_Gamma_Vector_Representation = tf.multiply(W_Q_Gamma, encoding_x_p)

            scope.reuse_variables()

        with tf.variable_scope("attention_flow", reuse=reuse) as scope:
            C_Input = tf.concat([encoding_x_p, Att_Vector_Representation, Gamma_Vector_Representation,
                                 W_Att_Vector_Representation, W_Gamma_Vector_Representation,
                                 W_Q_Att_Vector_Representation, W_Q_Gamma_Vector_Representation], axis=2)

            G = Fully_Connected(C_Input, self.hidden_size * 1, 'G_weight', tf.nn.relu, reuse=reuse)

            scope.reuse_variables()

        with tf.variable_scope("modeling", reuse=reuse) as scope:
            output_, encoding_ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw_modelling,
                                                                 cell_bw=cell_bw_modelling,
                                                                 inputs=G,
                                                                 sequence_length=seq_length(G),
                                                                 dtype=tf.float32)

            output_fw, output_bw = output_
            output = tf.concat([output_fw, output_bw], axis=2)

            scope.reuse_variables()

        with tf.variable_scope("decoding_Start", reuse=reuse) as scope:
            Prediction_Start_ = Fully_Connected(output, 1, 'start_decoding', tf.nn.relu, reuse=reuse)
            Prediction_Start = tf.squeeze(Prediction_Start_, axis=2)

        with tf.variable_scope("modeling_stop", reuse=reuse) as scope:
            C_Input = tf.concat([Prediction_Start_, C_Input], axis=2)
            output_, encoding_ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw_modelling2,
                                                                 cell_bw=cell_bw_modelling2,
                                                                 inputs=C_Input,
                                                                 sequence_length=seq_length(C_Input),
                                                                 dtype=tf.float32)

            output_fw, output_bw = output_
            output = tf.concat([output_fw, output_bw], axis=2)

            scope.reuse_variables()

        with tf.variable_scope("decoding_Start",reuse=reuse) as scope:
            Prediction_Stop = Fully_Connected(output, 1, 'stop_decoding', tf.nn.relu, reuse=reuse)
            Prediction_Stop = tf.squeeze(Prediction_Stop, axis=2)

        return Prediction_Start, Prediction_Stop

class BIDAF:
    def __init__(self):
        self.hidden_size = 200
        self.keep_prob = 0.9

    def create_graph(self, x_p, x_q, p_length, q_length, context_encoding=False, reuse=False, is_training=True):
        d = 400

        with tf.variable_scope("context_encoding", reuse=reuse):
            cell_fw_p = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_fw_p = tf.contrib.rnn.DropoutWrapper(cell_fw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_fw_q = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_fw_q = tf.contrib.rnn.DropoutWrapper(cell_fw_q, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_bw_p = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_bw_p = tf.contrib.rnn.DropoutWrapper(cell_bw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_bw_q = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_bw_q = tf.contrib.rnn.DropoutWrapper(cell_bw_q, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)

            cell_fw_modelling = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_fw_modelling = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling, input_keep_prob=self.keep_prob,
                                                    output_keep_prob=self.keep_prob)
            cell_bw_modelling = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_bw_modelling = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling, input_keep_prob=self.keep_prob,
                                                    output_keep_prob=self.keep_prob)

            cell_fw_modelling2 = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_fw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling2, input_keep_prob=self.keep_prob,
                                                    output_keep_prob=self.keep_prob)
            cell_bw_modelling2 = tf.contrib.rnn.LSTMCell(self.hidden_size)
            cell_bw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling2, input_keep_prob=self.keep_prob,
                                                    output_keep_prob=self.keep_prob)

            if context_encoding is True:
                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_p, cell_bw=cell_bw_p, inputs=x_p,
                    sequence_length=seq_length(x_p), dtype=tf.float32, time_major=False)

                encoding_x_p = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_p_state = tf.concat([fw_state[-1], bw_state[-1]], -1)

                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_q, cell_bw=cell_bw_q, inputs=x_q,
                    sequence_length=seq_length(x_q), dtype=tf.float32, time_major=False)

                encoding_x_q = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_q_state = tf.concat([fw_state[-1], bw_state[-1]], -1)
            else:
                encoding_x_p = x_p
                encoding_x_q = x_q

        with tf.variable_scope("res_self_att"):
            encoding_x_p = self_attention_block(encoding_x_p, d, p_length, mask=None, num_heads=1,
                                           scope="self_attention_layers", reuse=reuse,
                                           is_training=is_training,
                                           bias=False, dropout=0.1)

            encoding_x_q = self_attention_block(encoding_x_q, d, q_length, mask=None, num_heads=1,
                                           scope="self_attention_layers", reuse=True,
                                           is_training=is_training,
                                           bias=False, dropout=0.1)

        with tf.variable_scope("bi_att", reuse=reuse):
            encoding_x_p_ = tf.expand_dims(encoding_x_p, axis=2)
            encoding_x_p_ = tf.tile(encoding_x_p_, multiples=[1, 1, q_length, 1])

            encoding_x_q_ = tf.expand_dims(encoding_x_q, axis=1)
            encoding_x_q_ = tf.tile(encoding_x_q_, multiples=[1, p_length, 1, 1])

            p_mul_q = tf.multiply(encoding_x_p_, encoding_x_q_)
            concat_data = tf.concat([encoding_x_p_, encoding_x_q_, p_mul_q], axis=3)
            S = Fully_Connected(concat_data, 1, 'att_s', None, reuse=reuse)
            S = tf.squeeze(S, axis=3)

            c2q = tf.matmul(tf.nn.softmax(S, dim=-1), encoding_x_q)
            b = tf.nn.softmax(tf.reduce_max(S, axis=2), dim=-1)
            b = tf.expand_dims(b, axis=1)
            q2c = tf.matmul(b, x_p)
            q2c = tf.tile(q2c, [1, p_length, 1])

            G = tf.concat([x_p, c2q, tf.multiply(x_p, c2q), tf.multiply(x_p, q2c)], axis=2)

        with tf.variable_scope("modelling", reuse=reuse):
            (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cell_fw_modelling, cell_bw=cell_bw_modelling, inputs=G,
                sequence_length=seq_length(G), dtype=tf.float32, time_major=False)

            M = tf.concat([fw_outputs, bw_outputs], -1)
            M_state = tf.concat([fw_state[-1], bw_state[-1]], -1)

            G_M = tf.concat([G, M], axis=2)
            G_M_ = Fully_Connected(G_M, 1, name='Prediction1', activation=None)
            G_M_ = tf.squeeze(G_M_, axis=-1)

            prediction1 = G_M_

        with tf.variable_scope("modelling2", reuse=reuse):
            (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                cell_fw=cell_fw_modelling2, cell_bw=cell_bw_modelling2, inputs=M,
                sequence_length=seq_length(M), dtype=tf.float32, time_major=False)

            M2 = tf.concat([fw_outputs, bw_outputs], -1)
            M2_state = tf.concat([fw_state[-1], bw_state[-1]], -1)
            G_M2 = tf.concat([G, M2], axis=2)
            G_M2_ = Fully_Connected(G_M2, 1, name='Prediction2', activation=None)
            G_M2_ = tf.squeeze(G_M2_, axis=-1)

            prediction2 = G_M2_

        return prediction1, prediction2

class SA_NET:
    def __init__(self):
        self.hidden_size = 200
        self.keep_prob = 0.95

    def create_graph(self, x_p, x_q, p_length, q_length, context_encoding=False, reuse=False, is_training=True):
        d = 296
        x_p.set_shape([None, p_length, d])
        x_q.set_shape([None, q_length, d])

        with tf.variable_scope("context_encoding", reuse=reuse):
            cell_fw_p = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_p = tf.contrib.rnn.DropoutWrapper(cell_fw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_bw_p = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_p = tf.contrib.rnn.DropoutWrapper(cell_bw_p, input_keep_prob=self.keep_prob,
                                                      output_keep_prob=self.keep_prob)
            cell_fw_modelling = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_modelling = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling, input_keep_prob=self.keep_prob,
                                                              output_keep_prob=self.keep_prob)
            cell_bw_modelling = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_modelling = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling, input_keep_prob=self.keep_prob,
                                                              output_keep_prob=self.keep_prob)

            cell_fw_modelling2 = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_fw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_fw_modelling2, input_keep_prob=self.keep_prob,
                                                               output_keep_prob=self.keep_prob)
            cell_bw_modelling2 = tf.contrib.rnn.GRUCell(self.hidden_size)
            cell_bw_modelling2 = tf.contrib.rnn.DropoutWrapper(cell_bw_modelling2, input_keep_prob=self.keep_prob,
                                                               output_keep_prob=self.keep_prob)

            if context_encoding is True:
                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_p, cell_bw=cell_bw_p, inputs=x_p,
                    sequence_length=seq_length(x_p), dtype=tf.float32, time_major=False)

                encoding_x_p = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_p_state = tf.concat([fw_state[-1], bw_state[-1]], -1)

                (fw_outputs, bw_outputs), (fw_state, bw_state) = tf.nn.bidirectional_dynamic_rnn(
                    cell_fw=cell_fw_p, cell_bw=cell_bw_p, inputs=x_q,
                    sequence_length=seq_length(x_q), dtype=tf.float32, time_major=False)

                encoding_x_q = tf.concat([fw_outputs, bw_outputs], -1)
                encoding_x_q_state = tf.concat([fw_state[-1], bw_state[-1]], -1)
            else:
                encoding_x_p = x_p
                encoding_x_q = x_q

        with tf.variable_scope("attention", reuse=reuse):
            M_Vector = tf.matmul(encoding_x_p, encoding_x_q, transpose_b=True)
            Alpha = tf.nn.softmax(M_Vector, dim=1)
            Beta = tf.nn.softmax(M_Vector, dim=2)

            encoding_x_q_m = Fully_Connected(encoding_x_q, d * 1, 'weight_paragraph', None, reuse=reuse)
            Memory1 = tf.matmul(Alpha, encoding_x_q_m)
            Memory2 = tf.matmul(Beta, encoding_x_q_m)
            Memory3 = tf.matmul(Alpha, encoding_x_q)
            Memory4 = tf.matmul(Beta, encoding_x_q)

        with tf.variable_scope("attention_flow", reuse=reuse) as scope:
            C_Input = tf.concat([encoding_x_p, Memory1, Memory2, Memory3, Memory4], axis=2)
            G = Fully_Connected(C_Input, self.hidden_size * 1, 'G_weight', tf.nn.relu, reuse=reuse)

            scope.reuse_variables()

        with tf.variable_scope("Embedding_Encoder_Layer"):
            G = self_attention_block(G, self.hidden_size, p_length, mask=None, num_heads=1,
                                           scope="self_attention_layers", reuse=reuse,
                                           is_training=is_training,
                                           bias=False, dropout=0.05)

        with tf.variable_scope("modeling", reuse=reuse) as scope:
            output_, encoding_ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw_modelling,
                                                                 cell_bw=cell_bw_modelling,
                                                                 inputs=G,
                                                                 sequence_length=seq_length(G),
                                                                 dtype=tf.float32)

            output_fw, output_bw = output_
            output = tf.concat([output_fw, output_bw], axis=2)

            scope.reuse_variables()

        with tf.variable_scope("decoding_Start", reuse=reuse) as scope:
            Prediction_Start_ = Fully_Connected(output, 1, 'start_decoding', tf.nn.relu, reuse=reuse)
            Prediction_Start = tf.squeeze(Prediction_Start_, axis=2)

        with tf.variable_scope("modeling_stop", reuse=reuse) as scope:
            C_Input = tf.concat([Prediction_Start_, C_Input], axis=2)
            output_, encoding_ = tf.nn.bidirectional_dynamic_rnn(cell_fw=cell_fw_modelling2,
                                                                 cell_bw=cell_bw_modelling2,
                                                                 inputs=C_Input,
                                                                 sequence_length=seq_length(C_Input),
                                                                 dtype=tf.float32)

            output_fw, output_bw = output_
            output = tf.concat([output_fw, output_bw], axis=2)

            scope.reuse_variables()

        with tf.variable_scope("decoding_Start",reuse=reuse) as scope:
            Prediction_Stop = Fully_Connected(output, 1, 'stop_decoding', tf.nn.relu, reuse=reuse)
            Prediction_Stop = tf.squeeze(Prediction_Stop, axis=2)

        return Prediction_Start, Prediction_Stop