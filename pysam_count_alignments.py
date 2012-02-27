#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser
import pysam
from bx.bitset_builders import *

""" iterator to yield coordinates in a bed file """
def yield_bedcoordinate(fh):
    """" yield a tuple of (chr, start,end) from bed file """
    for line in fh:
        if '@' in line: continue
        fields=line.strip().split("\t")
        (chr, start, end) = fields[0:3]
        yield(chr, int(start), int(end) )

def main():

    """ given a bam file and bed file, count the number of alignments in a given bed coordinate  """
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    usage = "usage: %prog [options] file.bam"
    parser = OptionParser(usage)
    parser.add_option("--bed", type="string", dest="bedfile", help="bed file of coordinates", default=None)
    parser.add_option("--mapq", type="float", dest="mapq", default=30., help="Exclude alignments from analysis if they have a mapping less than mapq (default is 30)")
    parser.add_option("--bq", type ="float", dest="bq", default =20. , help="Exclude bases from analysis if their supporting base quality is less that --bq (default is 20)")

    (options, args)=parser.parse_args()
    

    if options.bedfile == None:
        sys.stderr.write("please provide a bed file!\n")
        exit(1)

    bamfilename=args[0]
    bedfh=open(options.bedfile,'r')

    #read the bed file in to a bitset 
    bitsets = binned_bitsets_from_file( open( options.bedfile ) )

    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)

    #open the sam/bam file    
    samfile = pysam.Samfile(bamfilename, 'rb')

    #iterate thru the bed coordinates
    for coord_tuple in yield_bedcoordinate(bedfh):
        (chrom, start, end ) = coord_tuple
        readcount=0
        if 'chr' in chrom:
            newchrom=string.replace(chrom, 'chr','')
            chrom=newchrom
            print chrom, start, end
            #now fetch the reads that are in the bed interval (chrom, start, stop)
            for alignedread in samfile.fetch(chrom, start, end):
                print alignedread
                print alignedread.pos, alignedread.aend
                # now check and see if the alignment start posiiton starts in a target region
                if chrom in bitsets and bitsets[chrom].count_range( alignedread.pos-1, alignedread.pos ) >= 1:
                    print "read starts in target region: ",  alignedread.pos, alignedread.aend
                    #if so increment the number of reads starting in the region
                    readcount +=1
        #print the total number of reads starting in the region            
        outstring = "\t".join( [chrom, str(start), str(end), str(readcount), bamfilename ] )
        print outstring

if __name__ == "__main__":
    main()
