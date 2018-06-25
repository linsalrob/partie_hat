"""
Create a subset of the data for development purposes. This just creates a mini tsv data set that is easy to work with!
"""

import os
import sys
import argparse
from random import randint

def read_tsv(fname, nummgs):
    """
    Read the tsv file and return a dictionary
    :param fname: file name to read
    :param nummgs: number of metagenomes to retain
    :return: dict of dicts
    """

    data = {}
    with open(fname, 'r') as fin:
        header = fin.readline()
        p=header.strip().split("\t")
        choices = [randint(1, len(p)) for x in range(nummgs)]
        for i in choices:
            data[choices[i]] = {}
        for l in fin:
            p = l.strip().split("\t")
            for i in choices:
                data[choices[i]][p[0]] = p[i]
    return data

def clean_zeros(data):
    """
    Remove any genome for which every
    :param data: the data set
    :type data: dict
    :return: a dict of dicts
    """

    mgs = list(data.keys())
    todelete = set()
    genomeids = data[mgs[0]].keys()
    for g in genomeids:
        total = 0
        for m in mgs:
            total += float(data[m][g])
        if 0 == total:
            todelete.add(g)
    sys.stderr.write("deleting {} genome ids from {} total ids\n".format(len(todelete), len(todelete)))

    for m in mgs:
        for g in todelete:
            data[m].pop(g)
    return data


def write_tsv(data, outputf):
    """
    Write the data to a
    :param data:
    :param outputf:
    :return:
    """

    mgs = data.keys()
    with open(outputf, 'w') as out:
        out.write("\t{}\n".format("\t".join(mgs)))
        for d in data:
            out.write(d)
            for m in mgs:
                out.write("\t{}".format(data[m][d]))
            out.write("\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a mini data set for development purposes")
    parser.add_argument('-f', help='tsv file of focus outputs', required=True)
    parser.add_argument('-n', help='number of metagenomes to include, default=100', default=100, type=int)
    parser.add_argument('-o', help='output file to write', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    data = read_tsv(args.f)
    data = clean_zeros(data)
    write_tsv(data, args.o)