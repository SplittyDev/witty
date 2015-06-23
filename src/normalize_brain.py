#!/usr/bin/env python
__author__ = 'Splitty'

import os
from nltk.tokenize import sent_tokenize

def main():
    path = os.path.join('data', 'ext_brain.txt')
    f = open(path, 'r')
    lines = []
    for line in f:
        newline = line.replace('\r', '').strip()
        lines.append(newline)
    sentences = sent_tokenize(' '.join(lines))
    lines.clear()
    for sentence in sentences:
        lines.append(sentence.strip())
    f.close()
    f = open(path, 'w')
    for line in lines:
        f.write('%s\n' % line)
    f.close()

if __name__ == '__main__':
    main()
