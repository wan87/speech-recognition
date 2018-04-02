import sys
import time
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import yaml

from src import DataSet

from src.model import LSTMCTC, CTCNetwork

#from DataSet import read_number_data_sets


train_home_dictionary = '/Users/adamzvada/Documents/School/BP/SpeechRecognition/audio_numbers'

# HYPER PARAMETERS

# mfcc
# num_features =  247
num_features = 13
num_context = 4


# Accounting the 0th index +  space + blank label = 28 characters
num_classes = ord('z') - ord('a') + 1 + 1 + 1
num_epoches = 100
num_hidden = 100
num_layers = 3
batch_size = 8

FIRST_INDEX = ord('a') - 1  # 0 is reserved to space

tf.logging.set_verbosity(tf.logging.INFO)

logs_path = "./tensorboard"

def input_placehodler(shape):
    """
        Creates tensorflow placeholder as input to network
        :param: shape of input placeholder
        :return: placehodler of given shape
    """
    # Input tensor - shape
    return tf.placeholder(tf.float32, shape, name='x_input')


def sequence_length_placehodler(shape):
    """"
        Creates tensorflow placehodler of input audio sequence length of given shape
    """
    # 1d array of size [batch_size]
    return tf.placeholder(tf.int32, shape, name="sequence_length")


def label_sparse_placehodler():
    """
        Creates tensorflow placehodler for target text label as sparse matrix.
        Sparse placeholder is needed by CTC op.
    """
    # label of data
    return tf.sparse_placeholder(tf.int32, name='y_sparse_label')


def weights_and_biases(num_hidden, num_classes):
    """"
        Creation of weights and biases for NN layer
        @:param num_hidden - input dim for weights
        @:param num_classes - output dim for weights and biases dim
        @:return (tensorflow variable weights, tensorflow variable biases)
    """

    with tf.name_scope('weights'):
        weights = tf.Variable(tf.truncated_normal([num_hidden, num_classes], stddev=0.1))

    with tf.name_scope('biases'):
        biases = tf.Variable(tf.constant(0., shape=[num_classes]))

    tf.summary.histogram("weights", weights)
    tf.summary.histogram("biases", biases)

    return weights, biases


def init_state_placeholder():
    return tf.placeholder(tf.float32, [num_layers, 2, batch_size, num_hidden])

def lstm_nerual_network(x_input, weights, biases, num_hidden, num_layers, sequence_placehodler):
    """

    :param weights:
    :param biases:
    :param num_hidden:
    :param num_layers:
    :param sequence_placehodler:
    :return:
    """

    # state_per_layer_list = tf.unstack(init_state, axis=0)
    # rnn_tuple_state = tuple(
    #     [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[idx][0], state_per_layer_list[idx][1])
    #      for idx in range(num_layers)]
    # )

    cells = []
    for _ in range(num_layers):
        cells.append(tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True))

    #cell = tf.contrib.rnn.LSTMCell(num_hidden, state_is_tuple=True)

    stack = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)

    # x_input [batch, max_time, num_classes]
    # The second output is the last state and we will no use that
    outputs, state = tf.nn.dynamic_rnn(stack, x_input, sequence_placehodler, dtype=tf.float32)

    # shape = tf.shape(x_input)
    # batch_s, max_time_steps = shape[0]

    # Reshaping to apply the same weights over the timesteps [batch_size*max_time, num_hidden?] - fully connected
    outputs = tf.reshape(outputs, [-1, num_hidden])

    logits = tf.add(tf.matmul(outputs, weights), biases)
    tf.summary.histogram("predictions", logits)

    # Back to original shape
    logits = tf.reshape(logits, [batch_size, -1, num_classes])

    return logits, state



def ctc_loss_function(logits, sparse_target, sequence_length):
    """

    :param logits:
    :param sparse_target:
    :param sequence_length:
    :return:
    """

    # Requiered by CTC [max_timesteps, batch_size, num_classes], Convert form batch-major to time-major
    logits = tf.transpose(logits, [1, 0, 2])

    loss = tf.nn.ctc_loss(sparse_target, logits, sequence_length)
    cost = tf.reduce_mean(loss)

    return cost

def network_optimizer(cost):
    """
        Defines optimizer for tensorflow graph
        :param cost: minimizing for given cost
    """

    optimizer = tf.train.AdamOptimizer().minimize(cost)
    # optimizer = tf.train.MomentumOptimizer(learning_rate=0.005, momentum=0.9).minimize(cost)

    return optimizer

def ctc_decoder(logits, sequence_length):
    """

    :param logits:
    :param sequence_length:
    :return:
    """

    # Requiered by CTC [max_timesteps, batch_size, num_classes]
    logits = tf.transpose(logits, [1, 0, 2])

    decoded, _ = tf.nn.ctc_greedy_decoder(logits, sequence_length)

    return decoded

def compute_label_error_rate(decoded_sparse_label, sparse_target):
    """

    :param decoded_sparse_label:
    :param sparse_target:
    :return:
    """
    # Compute the edit (Levenshtein) distance of the top path
    # Compute the label error rate (accuracy)
    label_error_rate = tf.reduce_mean(tf.edit_distance(tf.cast(decoded_sparse_label, tf.int32), sparse_target))

    return label_error_rate



def train_network(dataset):

    graph = tf.Graph()


    # Create tensorflow placeholders for network
    # n_input + (2 * n_input * n_context)]
    #x = input_placehodler([None, None, num_features + 2*num_features*num_context])
    x = input_placehodler([None, None, num_features])
    y_sparse = label_sparse_placehodler()
    sequence_length = sequence_length_placehodler([None])
    init_state = init_state_placeholder()

    weights, baises = weights_and_biases(num_hidden, num_classes)

    #logits, state = lstm_nerual_network(x, weights, baises, num_hidden, num_layers, sequence_length, init_state)
    logits, _ = lstm_nerual_network(x, weights, baises, num_hidden, num_layers, sequence_length)

    cost = ctc_loss_function(logits, y_sparse, sequence_length)

    optimizer = network_optimizer(cost)

    decoded = ctc_decoder(logits, sequence_length)

    label_error_rate = compute_label_error_rate(decoded[0], y_sparse)


    # graph = tf.Graph()
    #
    # with graph.as_default():
    #logits, seq_len = lstm_network()
    #cost, targets, optimizer, ler, decoded = ctc_optimizer(logits, seq_len)


    # set TF logging verbosity
    #tf.logging.set_verbosity(tf.logging.INFO)

    #with tf.Session(graph=graph) as session:

    tf.summary.scalar("cost", cost)
    tf.summary.scalar("label_error_rate", label_error_rate)

    with tf.Session() as session:

        session.run(tf.global_variables_initializer())

        writer = tf.summary.FileWriter(logs_path, graph=session.graph)

        for epoch in range(num_epoches):

            epoch_loss = 0
            ler_loss = 0

            start = time.time()

            current_state = np.zeros((num_layers, 2, batch_size, num_hidden))

            for batch in range(int(dataset.train.num_examples / batch_size)):
                summary_op = tf.summary.merge_all()

                train_x, train_y_sparse, train_sequence_length = dataset.train.next_batch(batch_size)

                feed = {
                    x : train_x,
                    y_sparse : train_y_sparse,
                    sequence_length : train_sequence_length,
                    #init_state: current_state
                }

                batch_cost, _, summary = session.run([cost, optimizer, summary_op], feed)
                #batch_cost, _, _, summary = session.run([cost, optimizer, state, summary_op], feed)

                epoch_loss += batch_cost * batch_size

                writer.add_summary(summary, epoch * batch_size + batch)

                ler_loss += session.run(label_error_rate, feed) * batch_size

                # Decoding
                d = session.run(decoded[0], feed_dict=feed)
                str_decoded = ''.join([chr(x) for x in np.asarray(d[1]) + FIRST_INDEX])
                # Replacing blank label to none
                str_decoded = str_decoded.replace(chr(ord('z') + 1), '')
                # Replacing space label to space
                str_decoded = str_decoded.replace(chr(ord('a') - 1), ' ')

                print('Decoded: %s' % str_decoded)

            epoch_loss /= dataset.train.num_examples
            ler_loss /= dataset.train.num_examples

            log = "Epoch {}/{}, train_cost = {:.3f}, train_ler = {:.3f}, " \
                  "val_cost = {:.3f}, val_ler = {:.3f}, time = {:.3f}"

            print(log.format(epoch + 1, num_epoches, epoch_loss, ler_loss,
                             0, 0, time.time() - start))


def main(config_path=None):

    if config_path is None:
        print("Processing default config.")

        dataset = DataSet.read_number_data_sets(train_home_dictionary)

        train_network(dataset)
    else:
        print("Processing CONFIG in filename: %s", config_path)

        with open(config_path, 'r') as f:
            config = yaml.load(f)

            model_name = config_path['model_name']
            corpus = config_path['corpus']



if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        main(config_path=args[1])
    else:
        main()


