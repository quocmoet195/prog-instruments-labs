import hashlib
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from unittest.mock import patch
from measure_time import measure_time

@patch('measure_time.create_card_number')
def test_measure_time(mock_create_card_number):
    """
    ????????? ??????? measure_time, ??????????, ??? ??? ???????? create_card_number ? ?????????? ?????.
    """
    mock_create_card_number.return_value = "4274020236520877"
    hash_number = "0438cbc33cb25114ed4ae1cf863527401db733c2d55a01563a84f2955ad5233a129a0220fec715208fee40c9710343d402e22f97f1f8b3dc312f7a20e6585ad2"
    bins= [ 427603, 427653, 427921, 427959, 427439, 427961, 427433, 427451, 427434, 427447, 
           427402, 485463, 427680, 481776, 480114, 427918, 427951, 427697, 427463, 427909, 
           522860, 475794, 479583, 427968, 220220, 557000, 481777, 427627, 427436, 427955, 
           427638, 427967, 427429, 536961, 427460, 427444, 427648, 427643, 427613, 427941, 
           427641, 527404, 427407, 546922, 427615, 427406, 427411, 427416, 427407, 427417, 
           427418, 427420, 427422, 427425, 427427, 427428, 427430, 427432, 427433, 427436, 
           427438, 427444, 427448, 427449, 427459, 427466, 427472, 427475, 427477, 427499, 
           427600, 427601, 427602, 427616, 427620, 427622, 427625, 427635, 427648, 427659, 
           427666, 427672, 427674, 427677, 427680, 427699, 427901, 427902, 427916, 427920, 
           427922, 427925, 427930, 427948, 427959, 427966, 427972, 427975, 427977, 427999 ]
    last_four_numbers = "0877"
    file_statistic = "statistics.json"
    measure_time(hash_number, bins, last_four_numbers, file_statistic)
    mock_create_card_number.assert_called() 
