#!/usr/bin/python
import sys, getopt
from Bio import SeqIO
def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile.fas> -o <outputfile.tnt>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile.fas> -o <outputfile.fas>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   #print 'Input file is "', inputfile
   #print 'Output file is "', outputfile
   infile = open(inputfile)
   outfile = open(outputfile, 'w')
   outfile.write('nstates dna'+';'+'\n')
   outfile.write('xread'+'\n')						# writing heads in XREAD file
   outfile.write("'This file was converted from "+ inputfile +"'\n")	# writing heads in XREAD file
   GetCharNum = SeqIO.parse(infile, "fasta")
   CharNum = GetCharNum.next()
   Chars = str(len(CharNum.seq))
   outfile.write(Chars+'\t')
   infile.close()
   infile = open(inputfile)
   GetTaxNum = list(SeqIO.parse(infile, "fasta"))
   TaxNum = str(len(GetTaxNum))
   outfile.write(TaxNum+'\n')
   infile.close()
   infile = open(inputfile)
   for seq_record in SeqIO.parse(infile, "fasta"):
       terminals = str(seq_record.id)	# var terminals receive taxon names
       outfile.write(terminals+'\t')	# write name in output_file followed by TAB
       seqs = str(seq_record.seq)	# var seqs  receive sequence data for each terminal
       outfile.write(seqs+'\n')		# write sequence data in output_file followed by new line
   outfile.write(';'+'\n'+'proc/;')	# tail for TNT file
   infile.close()
   outfile.close()
   print ' '
   print "I am done!\n"
if __name__ == "__main__":
   main(sys.argv[1:])
