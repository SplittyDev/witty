#!/usr/bin/env python
__author__ = 'Splitty'

import os

def main():
    path = os.path.join('data', 'ext_brain.txt')
    f = open(path, 'r')
    lines = []
    for line in f:
        if line.replace('\r','') != '\n':
            lines.append(line.replace('\r','').replace('"','').strip())
    f.close()
    f = open(path, 'w')
    for line in lines:
        f.write('%s\n' % line)
    f.close()

if __name__ == '__main__':
    main()