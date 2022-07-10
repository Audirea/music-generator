import os
import music21 as m21

# globals
DATASET_PATH = "dataset/deutschl/test"
SAVE_PATH = "preprocessed/deutschl/test"

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


def dataset_preprocessing():
    """
    Preprocesses the dataset.
    """
    # load dataset
    songs = load_songs(DATASET_PATH)

    for i, song in enumerate(songs):
        # filter using acceptance criteria
        if not is_acceptable_duration(song, ACCEPTABLE_DURATIONS):
            continue

        # transpose songs
        song = transpose_song(song)

        # endcode song
        encoded_song = encode_song(song)

        # write to file

        save_song(encoded_song, SAVE_PATH + "/" + str(i) + ".txt")


if __name__ == "__main__":

    # test

    # songs = load_songs(DATASET_PATH)
    # print(len(songs))

    # transposed_song = transpose_song(songs[0])
    # print(transposed_song.analyze('key'))
    # songs[0].show()

    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    dataset_preprocessing()
