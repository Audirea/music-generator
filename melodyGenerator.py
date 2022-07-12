
from more_itertools import one
from tensorflow import keras
import numpy as np

import json
import os


from preprocessing import SEQUENCE_LENGTH

MODEL_PATH = "models/deutschl/deutschl_erk.h5"
MAPPER_PATH = "preprocessed/mapping/deutschl/erk/mapping.json"


class MelodyGenerator:
    """  
    model for melody generation 
    """

    def __init__(
        self,
        model_path=MODEL_PATH,
        mapper_path=MAPPER_PATH,
        sequence_length=SEQUENCE_LENGTH
    ):
        """
        :param model_path: path to the model
        """
        self.model = keras.models.load_model(model_path)

        with open(mapper_path, "r") as f:
            self.mapper = json.load(f)

        self.start_symbol = ["/"]*sequence_length

    def get_char_with_temp(self, probabilites, temperature):
        """
        """
        predictions = np.log(probabilites) / temperature
        probabilites = np.exp(predictions) / np.sum(np.exp(predictions))
        return np.random.choice(range(len(probabilites)), p=probabilites)

    def generate_melody(self, seed, num_steps, max_squence_length, temperature):
        """

        """

        # start symbol add to prerior in seed
        seed = seed.split()
        melody = seed
        seed = self.start_symbol + seed

        # seed into integer
        seed = [self.mapper[char] for char in seed]

        for _ in range(num_steps):

            # limit seed
            seed = seed[-max_squence_length:]

            # one hot encode seed
            one_hot = keras.utils.to_categorical(
                seed, num_classes=len(self.mapper))

            # (1, max_sequence_length, num of symbols in the vocabulary)
            onehot_seed = one_hot[np.newaxis, ...]

            # predict next note using probabilistic model
            probabilites = self.model.predict(onehot_seed)[0]
            output_integer = self.get_char_with_temp(probabilites, temperature)

            # add to seed
            seed.append(output_integer)

            # convert to string
            output_symbol = [k for k, v in self.mapper.items()
                             if v == output_integer][0]

            if output_symbol == "/":
                break

            # update melody
            melody.append(output_symbol)

        return melody


if __name__ == "__main__":
    mg = MelodyGenerator()
    seed = "55 _ _ _ 60 _ _ _ 55 _ _ _ 55 _"
    melody = mg.generate_melody(
        seed=seed,
        num_steps=100,
        max_squence_length=SEQUENCE_LENGTH,
        temperature=1
    )
    print(melody)
