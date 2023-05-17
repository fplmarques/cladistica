#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# usage: ./fast2tnt.py fasta_file.fas > fasta_file_aln.fas
##
# LIBRARIES
##

import os
import sys
from Bio import SeqIO

num_character = 0
num_taxa = 0
def make_dictionary_from_fasta(source_fasta_file):
  sequence_data = {}
  with open(source_fasta_file, 'r') as f:
    for terminal in SeqIO.parse(f, "fasta"):
      taxon = terminal.id
      sequence = str(terminal.seq)
      global num_taxa
      num_taxa += 1
      global num_character
      num_character = len(sequence)
      sequence_data[taxon] = sequence
    return sequence_data


def main():
  source_fasta_file = sys.argv[1]
  sequence_data = make_dictionary_from_fasta(source_fasta_file)
  print(f'nstates dna;')
  print(f'mxram 1024;')
  print(f'xread')
  print(f'{num_character} {num_taxa}')
  for tax, seqs in sequence_data.items():
    print(f'{tax}\t{seqs}')
  print(f';')
  print(f'taxname=;')
  print(f'hold 100000;')
  print(f'proc-/;')

##
# INITIALIZATION
##

if __name__ == "__main__":
  main()

exit()
