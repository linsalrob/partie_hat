"""
Create a subset of the data for development purposes. This just creates a mini tsv data set that is easy to work with!
"""

import os
import sys
import argparse
from random import randint

def read_environments(envf):
    """
    Read the environments file. We are only keeping environment at the moment
    :param envf: the environments file
    :return: a dict of all the data
    """

    data = {}
    with open(envf, 'r') as fin:
        for l in fin:
            if l.startswith('genome_id'):
                continue
            p = l.strip().split("\t")
            if p[3]:
                data["PATRIC|{}".format(p[0])] = p[3]
    return data


def read_tsv(fname):
    """
    Read the tsv file and return a dictionary
    :param fname: file name to read
    :return: dict of dicts
    """

    data = {}
    with open(fname, 'r') as fin:
        l = fin.readline()
        header = l.strip().split("\t")
        for i in range(1, len(header)):
            data[header[i]] = {}
        for l in fin:
            p = l.strip().split("\t")
            for i in range(1, len(header)):
                data[header[i]][p[0]] = p[i]
    return data


def count_environments(environ, mgs):
    """
    Count the environments each metagenome is present in
    :param environ: the environments dict
    :param mgs: the metagenomics data from read_tsv
    :return: a hash of the metagenomes and the environments they are in, and a set of the uniques
    """

    counts = {}
    uniques = set()
    for m in data:
        counts[m] = set()
        for g in counts[m]:
            if g not in environ:
                environ[g] = 'UNKNOWN'
            counts[m].add(environ[g])
        if len(counts[m]) == 1:
            sys.stderr.write("{} is only in {}\n".format(m, counts[m]))
        uniques.add(m)

    return counts, uniques


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
    sys.stderr.write("Cleaning up. We have {} metagenomes and {} genome ids\n".format(len(mgs), len(genomeids)))
    for g in genomeids:
        total = 0
        for m in mgs:
            total += float(data[m][g])
        if 0 == total:
            todelete.add(g)
    sys.stderr.write("deleting {} genome ids from {} total ids\n".format(len(todelete), len(genomeids)))

    for m in mgs:
        for g in todelete:
            data[m].pop(g)
    return data


def write_tsv(data, outputf, towrite=None):
    """
    Write the data to a
    :param data: the data to write
    :param outputf: the ouput file name
    :param towrite: a set of those names to print. If none, all are printed
    :return:
    """

    if towrite:
        mgs = towrite
    else:
        mgs = data.keys()
    genomes = data[list(mgs)[0]].keys()
    with open(outputf, 'w') as out:
        out.write("\t{}\n".format("\t".join(mgs)))
        for g in genomes:
            out.write(g)
            for m in mgs:
                out.write("\t{}".format(data[m][g]))
            out.write("\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a mini data set for development purposes")
    parser.add_argument('-f', help='tsv file of focus outputs', required=True)
    parser.add_argument('-e', help='environments file (probably patric_metadata_20180526_isolation_host_env.tsv', required=True)
    parser.add_argument('-n', help='number of metagenomes to include, default=100', default=100, type=int)
    parser.add_argument('-o', help='output file to write', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    envs = read_environments(args.e)
    data = read_tsv(args.f)
    envcounts, uniques = count_environments(envs, data)
    data = clean_zeros(data)
    write_tsv(data, args.o, uniques)
