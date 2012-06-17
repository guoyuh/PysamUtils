#!/usr/bin/python
import sys
import os
import string
import re
import subprocess
from optparse import OptionParser
import pysam

def yield_bedcoordinate(fh):
    """" yield a tuple of (chr, start,end) from bed file """
    for line  in fh:
        if '@' in line: continue
        fields=line.strip().split("\t")
        (chr, start, end) = fields[0:3]
        yield(chr,start, end )


""" generate a bam file with  window size around bed coordinates for a given BAM file - useful for doing alignment gazing/ Pysam processing on subsets of BAM files around regions of interest"""



def main():
    usage = "usage: %prog [options] bamfile  \n generate a shell script that generates locus specific BAM file of a certain   window size around bed coordinates for a given orignal BAM file\n\n"
    parser = OptionParser(usage)
    parser.add_option("--bedfile", type="string", dest="bedfile", help="bedfile")
    parser.add_option("--upstreampad", type="int", default=100, dest="upstream", help="upstream" )
    parser.add_option("--downstreampad", type="int", default=100, dest="downstream", help="downstream" )
    parser.add_option("--ref", type="string", default="human_reference_v37.fa", dest="ref", help="name of reference assembly (fasta) file (.fa)")
    parser.add_option("--bamprefix", type="string", default=None, dest="bamprefix", help="output prefix of bam file")

    (options, args)=parser.parse_args()
    if options.bamprefix == None:
        sys.write("please provide a value to --bamprefix option!\n ")
        sys.exit(1)


    bamfile=args[0]

    if os.path.isfile(bamfile) == False:
       sys.stderr.write("bam file doesn't exists! " + bamfile +"\n")
       sys.exit(1)

    bamindexfile=bamfile+".bai"

    if os.path.isfile(bamindexfile) == False:
        sys.stderr.write("bam index file doesn't exist! did you run samtools/bamtools index?\n")
        sys.exit(1)

    if os.path.isfile(options.bedfile) == False:
        sys.stderr.write("bed file doesn't exist! " + options.bedfile + "\n")
        exit(1)

    bam = pysam.Samfile( bamfile, "rb" )

    bedfh=open(options.bedfile, 'r')

    for coord_tuple in yield_bedcoordinate(bedfh):
        (chr, start, end)=coord_tuple
        regionstring=chr+":"+start+".."+end
        bamfilename=".".join( [ options.bamprefix, regionstring, 'bam' ] )

        outbam = pysam.Samfile(bamfilename, "wb", template=bam)


        print coord_tuple
        print chr, str( int(start)-options.upstream) , str( int(end)+options.downstream )
        for alignedread in bam.fetch( chr, int(start)-options.upstream, int(end)+options.downstream ):
            if alignedread.ispaired:
                outbam.write(alignedread)
        outbam.close()

    bam.close()

if __name__ == "__main__":
    main()
