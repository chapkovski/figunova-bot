import random

with open('lenin/clean_lenin.csv', 'r') as content_file:
    data = content_file.readlines()


def get_lenin_answer():
    return data[random.randrange(len(data))]
