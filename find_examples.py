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
    with open(envf, 'r', errors='ignore') as fin:
        for l in fin:
            if l.startswith('genome_id'):
                continue
            p = l.strip().split("\t")
            if p[3]:
                data["PATRIC|{}".format(p[0])] = p[3]
    return data


def read_tsv(fname, nummgs):
    """
    Read the tsv file and return a dictionary
    :param fname: file name to read
    :param nummgs: number of metagenomes to retain
    :return: dict of dicts
    """

    data = {}
    with open(fname, 'r') as fin:
        l = fin.readline()
        header = l.strip().split("\t")
        choices = [randint(1, len(header)) for x in range(nummgs)]
        for i in choices:
            data[header[i]] = {}
        for l in fin:
            p = l.strip().split("\t")
            for i in choices:
                data[header[i]][p[0]] = p[i]
    return data


def count_environments(environ, data, minval):
    """
    Count the environments each metagenome is present in
    :param environ: the environments dict
    :param data: the metagenomics data from read_tsv
    :param minval: the minimum value (0 - 100) to save that sample
    :return: a hash of the metagenomes and the environments they are in, and a set of the uniques
    """

    counts = {}
    uniques = set()
    for m in data:
        counts[m] = {}
        for g in data[m]:
            if g not in environ:
                environ[g] = 'UNKNOWN'
            if float(data[m][g]) > 0:
                counts[m][environ[g]] = counts[m].get(environ[g], 0) + float(data[m][g])
        if max(counts[m].values())> minval:
            sys.stderr.write("The most abundant env for {} is {}\n".format(m, max(counts[m].values())))
            uniques.add(m)

    return counts, uniques


def filter_by_count(data, uniques):
    """
    Filter the data to retain only those in uniques
    :param data: the dict of tsv
    :param uniques: the ones to filter
    :return: a modified dict
    """

    return {x:data[x] for x in uniques}

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


def write_envs(counts, countf):
    """
    Write the environment counts to countf
    :param counts: the environment counts
    :param countf: the file to write to
    :return: None
    """

    with open(countf, 'w') as out:
        for c in counts:
            out.write("{}\t{}\n".format(c, counts[c]))




def write_tsv(data, outputf):
    """
    Write the data to a
    :param data: the data to write
    :param outputf: the ouput file name
    :return:
    """

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
    parser.add_argument('-e', help='environments file (probably patric_metadata_isolation_host_env.tsv', required=True)
    parser.add_argument('-n', help='number of metagenomes to include, default=1000', default=1000, type=int)
    parser.add_argument('-m', help='minimum value to save a sample (0 - 90), default=90%', default=90, type=int)
    parser.add_argument('-c', help='counts output file to write')
    parser.add_argument('-o', help='output file to write', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    sys.stderr.write("Reading environments\n")
    envs = read_environments(args.e)
    sys.stderr.write("Reading table\n")
    data = read_tsv(args.f, args.n)
    sys.stderr.write("Finding uniques\n")
    envcounts, uniques = count_environments(envs, data, args.m)
    if args.c:
        sys.stderr.write("Environment counts\n")
        write_envs(envcounts, args.c)
    sys.stderr.write("Filtering by counts\n")
    data = filter_by_count(data, uniques)
    sys.stderr.write("Deleting zeros\n")
    data = clean_zeros(data)
    sys.stderr.write("Output\n")
    write_tsv(data, args.o)
