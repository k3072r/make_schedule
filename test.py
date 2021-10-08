from copy import deepcopy
from make import get_index, get_not_locked_frames
import getxl
import openpyxl as px
import time
import random
import numpy

@profile
def hoge():
    filepath = "test.xlsm"
    wb = px.load_workbook(filename=filepath, keep_vba=True)

    schedule = getxl.get_schedule(wb)

    lists = get_not_locked_frames(schedule)

    length = len(lists)
    for i in range(10000):
        rndm = random.random()
        k = int((rndm * 1000000000) % length)
        (t_indice, i, j) = lists[k]

    for i in range(10000):
        (t_indice, i, j) = random.choice(lists)


hoge()