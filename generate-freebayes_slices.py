#!/usr/bin/python
import sys
import os
import string
import re
from optparse import OptionParser


def yield_bedcoordinate(fh):
    """" yield a tuple of (chr, start,end) from bed file """
    for line  in fh:
        if '@' in line: continue
        fields=line.strip().split("\t")
        (chr, start, end) = fields[0:3]
        yield(chr,start, end )


""" generate a shell script that generates  window size around bed coordinates for a given BAM file - useful for doing alignment gazing/ Pysam processing on subsets of BAM files around regions of interest"""



def main():
    usage = "usage: %prog [options] bamfile\n generate a shell script that generates locus specific BAM file of a certain   window size around bed coordinates for a given orignal BAM file\n\n"
    parser = OptionParser(usage)
    parser.add_option("--bedfile", type="string", dest="bedfile", help="bedfile")
    parser.add_option("--window", type="int", default=100, dest="window", help="window" )
    parser.add_option("--refbin", type="string", default="/d2/data/references/build_37", dest="refbin", help="directory of reference assembly")
    parser.add_option("--ref", type="string", default="human_reference_v37.fa", dest="ref", help="name of reference assembly (fasta) file (.fa)")
    parser.add_option("--ogap", type="string", default="/share/software/ogap/ogap", dest="ogap", help="ogap exectuable")
    parser.add_option("--baq", type="string", default="/share/software/samtools/samtools-0.1.16/samtools calmd -AEru ", dest="baq", help="BAQ executable")
    parser.add_option("--freebayes", type="string", default="/share/home/indapa/software/freebayes/bin", dest="freebayes", help="freebayes executable")
    parser.add_option("--bamtools", type="string", default="/share/software/bamtools/bin/bamtools filter", dest="bamtools", help="bam tools executable")
    (options, args)=parser.parse_args()

    bamfile=args[0]

    if os.path.isfile(bamfile) == False:
        sys.stderr.write("bam file doesn't exists! " + bamfile +"\n")
        exit(1)

    if os.path.isfile(options.bedfile) == False:
        sys.stderr.write("bed file doesn't exist! " + options.bedfile + "\n")
        exit(1)

    bedfh=open(options.bedfile, 'r')

    for coord_tuple in yield_bedcoordinate(bedfh):
        print coord_tuple



if __name__ == "__main__":
    main()
