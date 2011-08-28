#!/usr/bin/env python
import sys
import os
import string
import re
from optparse import OptionParser

import pysam

def yield_bedcoordinate(fh):
    """" yield a tuple of (chr, start,end) from bed file """
    for line  in fh:
        if '@' in line: continue
        fields=line.strip().split("\t")
        (chr, start, end) = fields[0:3]
        yield(chr, int(start), int(end) )


def main():
    """ given a bam file and bed file the program prints out the count of each type of base piled up at postion
        contained in the interval of a bed file. If no bases are piled up at that position it will not appear 
        in the output """
    usage = "usage: %prog [options] file.bam"
    parser = OptionParser(usage)
    parser.add_option("--bed", type="string", dest="bedfile", help="bed file of coordinates")
    parser.add_option("--mapq", type="float", dest="mapq", default=30., help="Exclude alignments from analysis if they have a mapping less than mapq (default is 30)")
    parser.add_option("--bq", type ="float", dest="bq", default =20. , help="Exclude bases from analysis if their supporting base quality is less that --bq (default is 20)")
    
    parser.add_option("--includeDuplicates", action="store_false", dest="duplicate", help="include duplicate marked reads in analysis (turned off by default) ")
    (options, args)=parser.parse_args()

    bamfilename=args[0]
    bedfh=open(options.bedfile,'r')

    if os.path.exists(bamfilename+".bai") == False:
        sys.stderr.write("please check for existence of bam index file (*.bai)\n")
        exit(1)
    

    pybamfile = pysam.Samfile(bamfilename, "rb" )
    print "#chrom targetStart targetEnd POS  A_count C_count G_count T_count N_count"
    for coord_tuple in yield_bedcoordinate(bedfh):
        (chrom, start, end ) = coord_tuple
        if 'chr' in chrom:
            newchrom=string.replace(chrom, 'chr','')
            chrom=newchrom

        for pileupcolumn in pybamfile.pileup( chrom, start, end):

            if pileupcolumn.pos != start:
                continue
            sys.stdout.write('chr'+chrom+ " " + str(start) +  " " + str(end) + " " + str(pileupcolumn.pos) + " ")

            #print 'coverage at base %s = %s' % (pileupcolumn.pos , pileupcolumn.n)
            seqdict={}
            for (base,count) in ( ('A',0), ('C',0), ('G',0), ('T',0), ('N',0) ):
                seqdict[base]=count

            for pileupread in pileupcolumn.pileups:
                #print '\tbase in read %s = %s' % (pileupread.alignment.qname, pileupread.alignment.seq[pileupread.qpos])
                
                if pileupread.alignment.is_duplicate == True and options.duplicate == False:
                    continue
                if  pileupread.alignment.mapq < options.mapq: 
                    continue

                if  ( ord ( pileupread.alignment.qual[ pileupread.qpos ] )  - 33 ) < options.bq: 
                    continue
                seqdict[ pileupread.alignment.seq[pileupread.qpos] ] +=1
            for nt in ('A', 'C', 'G', 'T', 'N'):
                sys.stdout.write( str(seqdict[nt]) + " ")
            sys.stdout.write("\n")
            #print pileupcolumn.pos
        #sys.stdout.write("\n")
    pybamfile.close()

if __name__ == "__main__":
    main()
