import tensorflow as tf
from tensorflow import keras
import os

from preprocessing import generate_training_data, SINGLE_STRING_DIR, MAPPER_DIR, SEQUENCE_LENGTH

# changes can be applied here
INPUT_UNITS = None  # any length of sequence can be used
OUTPUT_UNITS = 38  # mapper length is better
NUM_UNITS = [256]
LOSS = 'sparse_categorical_crossentropy'
LEARNING_RATE = 0.001
BATCH_SIZE = 64  # sequence length is better
EPOCHS = 1

SAVE_MODEL_DIR = "models/deutschl"
SAVE_MODEL_NAME = "deutschl_erk.h5"


def build_model(input_units, output_units, num_units, loss, learning_rate):
    """
    Builds a model using keras
    :return: model
    """
    _input = keras.layers.Input(shape=(input_units, output_units))

    # change lstm layers according to the number of units in the hidden layer
    x = keras.layers.LSTM(num_units[0])(_input)
    x = keras.layers.Dropout(0.2)(x)

    _output = keras.layers.Dense(output_units, activation='softmax')(x)

    model = keras.Model(_input, _output)

    model.compile(
        loss=loss,
        optimizer=keras.optimizers.Adam(learning_rate),
        metrics=['accuracy']
    )

    model.summary()

    return model


# change here
def train_model(
    output_units=OUTPUT_UNITS,
    input_units=INPUT_UNITS,
    loss=LOSS,
    num_units=NUM_UNITS,
    learning_rate=LEARNING_RATE,
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
):
    """
    :param output_units = Number of output units ouputs in output layer
    :param num_units = Number of units in hidden layer
    :param loss = Loss function to use
    :param metrics = Metrics to use
    :param epochs = Number of epochs to train for
    :param batch_size = Batch size to use

    """

    # check existence of the directory
    if not os.path.exists(SAVE_MODEL_DIR):
        os.makedirs(SAVE_MODEL_DIR)

    # get inputs and targets
    inputs, targets = generate_training_data(
        SINGLE_STRING_DIR, MAPPER_DIR, SEQUENCE_LENGTH)

    # build model
    model = build_model(input_units, output_units,
                        num_units, loss, learning_rate)

    # train model
    model.fit(
        inputs,
        targets,
        epochs=epochs,
        batch_size=batch_size
    )

    # save model
    model.save(SAVE_MODEL_DIR + '/' + SAVE_MODEL_NAME)


if __name__ == "__main__":
    train_model()
