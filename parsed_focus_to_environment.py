"""
Read the output from parse_focus.py and add the environment. We output this as a json file
"""

import os
import sys
import argparse



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

def read_tsv(fname, envs):
    """
    Read the tsv file we parsed from the focus output and return a dictionary of metagenomes and environment counts

    The tsv has SRR IDs in the columns and each row is a genome.
    :param fname: file name to read
    :param envs: the environment dict for each genome
    :return: dict of metagenomes and their environments
    """


    srrenvs = {}

    with open(fname, 'r') as fin:
        l = fin.readline()
        srr = l.strip().split("\t")
        srrenvs = {x : {} for x in srr}
        for l in fin:
            p = l.strip().split("\t")
            thisenvironment = envs.get(p[0], "UNKNOWN")
            for i,j in enumerate(p, start=1):
                if float(j) > 0:
                    srrenvs[srr[i]][thisenvironment] = srrenvs[srr[i]].get(thisenvironment, 0) + float(j)
    return srrenvs


def write_json(data, outputf):
    """
    Write the data to a file. We output the SRR ID and the json string
    :param data: the data to write
    :param outputf: the ouput file name
    :return:
    """

    with open(outputf, 'w') as out:
        for mg in data.keys():
            out.write("{}\t{}".format(mg, data[mg]))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add the environment")
    parser.add_argument('-f', help='tsv matrix from parse_focus.py', required=True)
    parser.add_argument('-e', help='environments file from patric (probably patric_metadata_isolation_host_env.tsv', required=True)
    parser.add_argument('-o', help='json output file to write', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    sys.stderr.write("Reading environments\n")
    envs = read_environments(args.e)
    sys.stderr.write("Reading table\n")
    mgdata = read_tsv(args.f, envs)
    sys.stderr.write("Creating output\n")
    write_json(mgdata, args.o)