import csv
import random
import csv
import nltk

with open('bible.txt', errors='ignore') as content_file:
    content = content_file.read()
    divided = nltk.sent_tokenize(content, language="russian")
print(len(divided))
import codecs

with open('test.csv', 'w', encoding='utf8', ) as csvfile:
    for p in divided:
        if len(p) > 10:
            csvfile.write(f'{p}\n')
