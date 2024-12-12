import hashlib
import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from unittest.mock import patch
from measure_time import mark_global_point


@patch('matplotlib.pyplot.savefig')
def test_mark_global_point(mock_savefig):
    """
    ????????? ??????? mark_global_point, ????????, ???????? ?? ??? savefig ??? ?????????? ???????.
    """
    statistics = {1: 2.0, 2: 1.5, 3: 1.0, 4: 0.5}
    file_name = "statistics.png"
    mark_global_point(statistics, file_name)
    mock_savefig.assert_called_with(file_name)
