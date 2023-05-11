#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  usage: python3 subedgesgaps.py [-h] -i INPUT [-g GAP] [-m MISSING] [-d]
#
#	example: python3 subedgesgaps.py -i cytb_renamed_aln.fas
#
#  optional arguments:
#    -h, --help            show this help message and exit
#    -i INPUT, --input INPUT
#                          Input file (alignment in FASTA format containing
#                          trailing gaps)
#    -g GAP, --gap GAP     Gap symbol (default = '-')
#    -m MISSING, --missing MISSING
#                         Missing symbol (default = 'N')
#    -d, --delete          Delete trailing gaps instead of replacing them

# handleTrailingsGaps.py
# Removes triling gaps or replace them by Ns

# By Denis Jacob Machado on April 19, 2018
# This algorithm is case sensitive

# Import modules and libraries
import argparse, re, sys

# Set arguments
parser=argparse.ArgumentParser()
parser.add_argument("-i","--input",help="Input file (alignment in FASTA format containing trailing gaps)",type=str,required=True)
parser.add_argument("-g","--gap",help="Gap symbol (default = '-')",type=str,default="-",required=False)
parser.add_argument("-m","--missing",help="Missing symbol (default = 'N')",type=str,default="N",required=False)
parser.add_argument("-d","--delete",help="Delete trailing gaps instead of replacing them",action="store_true",default=False,required=False)
args=parser.parse_args()

# Define functions
def read_fasta():
	alignment = {}
	handle = open(args.input,"r")
	for head,body in re.compile("(>[^\n\r]+)([^>]+)", re.M | re.S).findall(handle.read()):
		head = re.sub("\s", "", head)
		body = re.sub("\s", "", body)
		alignment[head] = body
	handle.close()
	return alignment

def handle_trailing_gaps(alignment):
	for head in alignment:
		body = alignment[head]
		gap = args.gap
		if(args.delete):
			mis = ""
		else:
			mis = args.missing
		try:
			left = len(re.compile("^{}+".format(gap)).findall(body)[0])
		except:
			left = 0
		try:
			right = len(re.compile("{}+$".format(gap)).findall(body)[0])
		except:
			right = 0
		body = body[left:len(body)-right]
		body = "{}{}{}".format(left*mis,body,right*mis)
		alignment[head] = body
	return alignment

def report(alignment):
	for head in alignment:
		sys.stdout.write("{}\n{}\n".format(head,alignment[head]))
	return

# Execute functions
alignment = read_fasta()
handle_trailing_gaps(alignment)
report(alignment)

# Quit
exit()
