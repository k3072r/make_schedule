from copy import deepcopy
from make import get_index
import getxl
import openpyxl as px
import time

a = [1, 2, 3]
b = [4, 5, 6]

c = deepcopy(a)
d = deepcopy(b)

c[1], d[2] = d[2], c[1]

print("hoge")