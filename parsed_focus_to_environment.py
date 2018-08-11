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
        data = {x : {} for x in header}
        for l in fin:
            p = l.strip().split("\t")
            for i, j in enumerate(p):
                if 0 == i:
                    continue
                data[header[i]][p[0]] = j
    return data

def write_json(data, outputf):
    """
    Write the data to a file. We output the SRR ID and the json string
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
    parser = argparse.ArgumentParser(description="Add the environment")
    parser.add_argument('-f', help='tsv matrix from parse_focus.py', required=True)
    parser.add_argument('-e', help='environments file from patric (probably patric_metadata_isolation_host_env.tsv', required=True)
    parser.add_argument('-o', help='json output file to write', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()

    sys.stderr.write("Reading environments\n")
    envs = read_environments(args.e)
    sys.stderr.write("Reading table\n")
    data = read_tsv(args.f)
    sys.stderr.write("Creating output\n")
    write_json(data, args.o)