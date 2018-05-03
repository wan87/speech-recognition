import os
from tqdm import tqdm

from src.dataset.DatasetBase import DatasetBase


class VCTKDataset(DatasetBase):
    """" VCTKDataset process data from VCTK Corpus
    Args:
        dataset_path
        num_features
        num_context
    """


    def __init__(self, dataset_path, num_features, num_context):
        DatasetBase.__init__(self, num_features, num_context)
        self.dataset_path = dataset_path

        self.read_vctk_dataset()


    def read_vctk_dataset(self, dataset_path=None):
        """" Retrives filenames from VCTK structues corpus and stores them in VCTKDataset object
        Args:
            dataset_path (string) - given path to home directory of dataset
        """

        if dataset_path is not None:
            self.dataset_path = dataset_path

        print("Retriving all filenames for VCTK training dataset from path", self.dataset_path)

        audio_dataset_path = os.path.join(self.dataset_path, 'wav48')
        label_dataset_path = os.path.join(self.dataset_path, 'txt')

        # gets list of directories for diffrent speakers
        speakers_dirs = os.listdir(audio_dataset_path)

        for speaker_dir in tqdm(speakers_dirs, total=len(speakers_dirs)):

            # get full paths for speakers
            speaker_audio_path = os.path.join(audio_dataset_path, speaker_dir)
            speaker_label_path = os.path.join(label_dataset_path, speaker_dir)

            # ignore inconsistency in data or anything that is not directory
            if not os.path.isdir(speaker_audio_path) or not os.path.isdir(speaker_label_path):
                continue

            # Getting full paths to all audios and labels of the speaker
            audio_paths = [os.path.join(speaker_audio_path, speaker_filename) for speaker_filename in os.listdir(speaker_audio_path)]
            label_paths = [os.path.join(speaker_label_path, speaker_filename) for speaker_filename in os.listdir(speaker_label_path)]

            # concatenate speaker filenames
            self._audio_filenames = self._audio_filenames + audio_paths
            self._label_filenames = self._label_filenames + label_paths


        self._num_examples = len(self._audio_filenames)


def test_dataset():

    dataset_path = '/Users/adamzvada/Desktop/VCTK-Corpus'

    vctk_dataset = VCTKDataset(dataset_path, 13, 4)

    train_input, sparse_targets, train_length = vctk_dataset.next_batch(8)

if __name__ == "__main__":

    test_dataset()