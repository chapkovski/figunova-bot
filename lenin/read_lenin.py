import random

with open('clean_lenin.csv', 'r') as content_file:
    data = content_file.readlines()


def get_lenin_answer():
    return data[random.randrange(len(data))]
