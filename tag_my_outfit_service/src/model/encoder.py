
from sklearn.preprocessing import MultiLabelBinarizer, LabelBinarizer


class Encoder(object):

    def __init__(self, label_binarizer: (MultiLabelBinarizer, LabelBinarizer),
                 target_variable: str, is_multi_label: bool) -> None:
        self.target_variable = target_variable
        self.is_multi_label = is_multi_label
        self.encoder = label_binarizer

    def decode(self, np_zeros_ones_array):
        result = self.encoder.inverse_transform(np_zeros_ones_array)
        if not self.is_multi_label:
            result = [tuple([label]) for label in result]

        return result
