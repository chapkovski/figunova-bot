import csv
import random

with open('clean_lenin.csv', 'r') as content_file:
    lineList = content_file.readlines()

    # with open('lenin.csv', 'a', encoding='utf8', ) as csvfile:
    #     for l in lineList:
    #         if len(l) > 10:
    #             csvfile.write(f'{l}\n')
    #         else:
    #             print(l)
    data = list(lineList)
    print(data[random.randrange(len(data))])

# import csv
# input = open('lenin.csv', 'r')
# output = open('clean_lenin.csv', 'w')
# writer = csv.writer(output)
# for row in csv.reader(input):
#     if row:
#         writer.writerow(row)
# input.close()
# output.close()