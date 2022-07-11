import os
import music21 as m21
import json

# globals
# ex : "dataset/deutschl/test"
DATASET_DIR = "dataset/deutschl/test"

# ex : "preprocessed/encode/deutschl/test"
ENCODED_SAVE_DIR = "preprocessed/encode/deutschl/test"

# ex : "preprocessed/single_string/deutschl/test"
SINGLE_STRING_DIR = "preprocessed/single_string/deutschl/test"

# ex :  "preprocessed/mapping/deutschl/test"
MAPPER_DIR = "preprocessed/mapping/deutschl/test"

ACCEPTABLE_DURATIONS = [
    0.25,  # sixteenth note
    0.5,  # eighth note
    0.75,
    1.0,  # quarter note
    1.5,
    2.0,  # half note
    3,
    4.0,  # whole note
]
SEQUENCE_LENGTH = 64


def load_songs(path):
    """
    Loads all songs in the given path.
    """
    songs = []
    for file in os.listdir(path):
        if file.endswith(".krn"):
            song = m21.converter.parse(path + "/" + file)
            songs.append(song)
    return songs


def is_acceptable_duration(song, durations):
    """
    Checks if the duration is acceptable.
    """
    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in durations:
            return False

    return True


def transpose_song(song):
    """
    Transposes the song C major to A minor.
    """

    # get key signature
    parts = song.getElementsByClass(m21.stream.Part)
    measures = parts[0].getElementsByClass(m21.stream.Measure)
    key_signature = measures[0][4]

    if not isinstance(key_signature, m21.key.Key):
        key_signature = song.analyze('key')

    # get intervels for tansposition
    if key_signature.mode == "major":
        interval = m21.interval.Interval(
            key_signature.tonic, m21.pitch.Pitch("C"))
    elif key_signature.mode == "minor":
        interval = m21.interval.Interval(
            key_signature.tonic, m21.pitch.Pitch("A"))

    # transpose by intervel
    return song.transpose(interval)


def encode_song(song, time_step=0.25):
    """
    Encodes the song.
        This gives time series representation of the song.

    Convert score into time series.It is representing quater lengths of notes.
    The symblos are:
        r: rest
        '_': notes/rests
        integer: for midi notes


    parameters are: 
    song: music21.stream
    time_step : duraion of each time step in quater length


    return : string (encoded song as time series string)
    """

    encoded_songs = []

    for event in song.flat.notesAndRests:
        # for notes
        if isinstance(event, m21.note.Note):
            symbol = event.pitch.midi

        # for rests
        elif isinstance(event, m21.note.Rest):
            symbol = "r"

        for step in range(int(event.duration.quarterLength/time_step)):
            if(step == 0):
                encoded_songs.append(symbol)
            else:
                encoded_songs.append("_")

    return " ".join(map(str, encoded_songs))


def save_song(song, path):
    """
    Saves the song to the given path.
    """
    with open(path, "w") as f:
        f.write(song)


def dataset_preprocessing(dataset_path, save_path):
    """
    Preprocesses the dataset.
    """
    # load dataset
    songs = load_songs(dataset_path)

    for i, song in enumerate(songs):
        # filter using acceptance criteria
        if not is_acceptable_duration(song, ACCEPTABLE_DURATIONS):
            continue

        # transpose songs
        song = transpose_song(song)

        # endcode song
        encoded_song = encode_song(song)

        # check directory exists if not create
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # write to file
        save_song(encoded_song, save_path + "/" + str(i) + ".txt")


def create_single_string(dataset_path, save_path, sequence_length):
    """
    Creates a single string from the song.
    """
    delimiter = "/ "*sequence_length
    songs = ""

    # load songs
    for file in os.listdir(dataset_path):
        with open(dataset_path + "/" + file, "r") as f:
            song = f.read()
            # add to string with seperating delimiter
            songs += song + " " + delimiter

    # remove last delimiter
    songs = songs[:-1]

    # check directory exists if not create
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save to file
    with open(save_path + '/single-string.txt', "w") as f:
        f.write(songs)

    return songs  # return the single string


def mapping(songs, save_path):
    """
    Creates a mapping file from the single string.
    """

    songs = songs.split()

    vocalbulary = list(set(songs))

    # create mapping
    mapping = {}
    for i, symbol in enumerate(vocalbulary):
        mapping[symbol] = i

    # check directory exists if not create
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # save to file
    with open(save_path + '/mapping.json', "w") as fp:
        json.dump(mapping, fp, indent=4)


def main():
    """
    Main function.
    """
    dataset_preprocessing(DATASET_DIR, ENCODED_SAVE_DIR)
    print("Preprocessing done.")
    songs = create_single_string(
        ENCODED_SAVE_DIR, SINGLE_STRING_DIR, SEQUENCE_LENGTH)
    print("Single string created.")
    mapping(songs, MAPPER_DIR)
    print("Mapping created.")


if __name__ == "__main__":
    main()
    print("Done.")
    print("Please check the files:")
    # print("DATASET_DIR: " + DATASET_DIR + '')
    print("ENCODED_SAVE_DIR: " + ENCODED_SAVE_DIR)
    print("SINGLE_STRING_DIR: " + SINGLE_STRING_DIR + '/single-string.txt')
    print("MAPPER_DIR: " + MAPPER_DIR + '/mapping.json')
    print("Thank you.Bye.")
    exit()
