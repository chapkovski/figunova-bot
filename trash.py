import numpy as np
from utils import cp

x = y = [1, 2, 3]
a, b = np.polyfit(x, y, deg=1)
cp(a, b)
predicted = [a * i + b for i in x]
cp(predicted)
