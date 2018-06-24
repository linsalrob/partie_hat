"""
Read a directory of focus output files and generate a single
file with the matrix of counts.
"""


import os
import sys
import gzip
import re


def read_directory(focus_dir):
    """
    Read the directory of focus files
    :param focus_dir: the directory containing the focus output files
    :return: a dict of counts and also a set of all genome ids we've seen
    """
    data={}
    allids=set()
    for f in os.listdir("focus"):
        if not f.endswith('_focus.txt.gz'):
            sys.stderr.write("Skipped: {}. It does not look like a compressed focus output file\n".format(f))
            continue
        data[f]={}
        gin = gzip.open(os.path.join("focus", f), 'rt')
        cont = True
        for l in gin:
            if 'Others (abundance <' in gin:
                continue
            if not l.strip():
                continue
            if l.startswith("Strain Level"):
                cont = False
                continue
            if cont:
                continue
            if l.startswith("Rank"):
                continue
            p=l.strip().split("\t")
            if len(p) < 3:
                sys.stderr.write("Too few args: {}\n".format(l))
                continue
            m=re.search("(PATRIC\|[\d\.]+)", p[1])
            if not m:
                sys.stderr.write("Can't parse {}\n".format(l))
                continue
            data[f.replace('_focus.txt.gz', '')][m.group(0)]=p[2]
            allids.add(m.group(0))

    return data, allids


def write_output(data, allids, outputf):
    """
    Write the output to a file
    :param data: the dict of focus file names and the counts for each genome
    :param allids: a set of all genome ids
    :param outputf: the output file to write
    :return: None
    """

    samples = data.keys()
    with open(outputf, 'w') as out:
        out.write("Genome\t{}\n".format("\t".join(samples)))
        for g in allids:
            out.write(g)
            for s in samples:
                out.write("\t{}".format(data[s].get(g, 0)))
            out.write("\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse a directory of focus files and generate a single tsv file")
    parser.add_argument('-d', help='directory of focus output files', required=True)
    parser.add_argument('-o', help='output filename', required=True)
    parser.add_argument('-v', help='verbose output', action="store_true")
    args = parser.parse_args()


    data, allids = read_directory(args.d)
    write_output(data, allids, args.o)
    




