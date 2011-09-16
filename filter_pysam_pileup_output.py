#!/usr/bin/python
import sys
import os
import string
import re
import bx.seq.twobit
from optparse import OptionParser

""" print  output lines from pysam_pileup.py that fail filters  based on min depth and min alt allele count of pileup counts at positions """


def depth (datadict):
    keys=['A','C', 'G', 'T']
    totaldepth=0
    for nt in keys:
        totaldepth+= datadict[nt]
    return totaldepth

def refcount (datadict, refallele):
     keys=['A','C', 'G', 'T']
     for nt in keys:
         if nt == refallele:
             return datadict[nt]
     return None

def main():
    usage = "usage: %prog [options] pileup.output.txt\n \n print  output lines from pysam_pileup.py \n that fail filters  based on min depth and min alt allele count of pileup counts at positions\n"
    parser = OptionParser(usage)
    parser.add_option("--depth", type="int", dest="depth", default = 5, help="keep lines with at least coverage at least greater than  depth (default 5)")
    parser.add_option("--alt", type="int", dest="alt", default=5, help="keep lines with at # of non-ref alleles greater than to nonref (default 5)")
    parser.add_option("--twobit", type="string", dest="tbf", help="two bit file")
    parser.add_option("--v", action="store_true", dest="reverse",  help="print regions that  pass filters ")

    (options, args)=parser.parse_args()
    if options.tbf == None:
        sys.stderr.write("please provide a two bit file ( --twobit option)\n")
        exit(1)
    try:
        sys.stderr.write("opening twobitfile...\n")
        twobit=bx.seq.twobit.TwoBitFile( open( options.tbf ) )
    except:
        sys.stderr.write("unable to open twobit file!\n")



    pileupfile=args[0]
    pileupfh=open (pileupfile, 'r')
    headerline=pileupfh.readline()
    headerline=headerline.replace('#', '')
    headerline=headerline.replace('_count', '')
    fields=headerline.strip().split (' ')

    fields = [elem for elem in fields if elem != '']
    bitseen = {}
    for line in pileupfh:
        if '#' in line: continue
        line= line.strip()
        line=line.replace('chr','')
        datafields=line.strip().split(' ')
        coord_string = " ".join( datafields[0:3])
        #print coord_string
        if coord_string not in bitseen.keys():
            bitseen[coord_string]=1
        else:
             bitseen[coord_string]+=1
             continue
        
        datafields=[elem for elem in datafields if elem != '']
        datafields = [int(x) for x in datafields]
        datadict = dict(zip(fields, datafields))
        start=datadict['targetStart']
        end=datadict['targetEnd']
        chrom='chr'+str(datadict['chrom'])
        
        try:
            refallele=twobit[chrom][start:end ]
            refallele=refallele.upper()
        except:
            sys.stderr.write("unable to fetch sequence from 2bit file!\n")
            continue

        pileupdepth = depth(datadict)
        altcount= pileupdepth - refcount (datadict, refallele)

        # if total depth is < than desired depth, pass on the record
        if ( pileupdepth )  < options.depth  :
            if not options.reverse:
                print "failed min depth " + str(options.depth) + ": " + line
                continue
      
        # if alt count is less than options.alt, pass on the record
        elif ( altcount ) < options.alt :
            if not options.reverse:
                print "failed alt allele count " + str(options.alt) + ": " + line
                continue
        elif options.reverse == True:
            print line
        else:
            pass
if __name__ == "__main__":
    main()
