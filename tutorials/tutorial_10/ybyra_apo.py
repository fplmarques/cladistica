#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# ybyra_apo.py

# YBYRÁ - Copyright (C) 2014 - Denis Jacob Machado
# GNU General Public License version 3.0

# Denis Jacob Machado
# denisjacobmachado@gmail.com
# www.ib.usp.br/grant/anfibios/researchSoftware.html

# Import libraries

try:
	import argparse,re,os,subprocess
# 	from sets import Set
except:
	print("!ERROR importing standart libraries")
	exit()

# Set arguments
parser=argparse.ArgumentParser()
parser.add_argument("-m","--matrix",help="matrix in simplified NEXUS format (Data block only) or TNT (.ss) format",default="matrix.nex",required=True,metavar="nexus file")
parser.add_argument("-o","--output",help="prefix for output files",default="OUTPUT",required=False,metavar="prefix")
parser.add_argument("-t","--trees",help="trees in TREAD format",default="trees.tre",required=True,metavar="tree file")
parser.add_argument("-r","--root",help="Optional. Seletc a terminal to root the trees",default="",required=False,metavar="root")
parser.add_argument("-v","--verbose",help="increase output verbosity",action="store_true")
parser.add_argument("-N","--NO_MESSAGES",help="skip messages (except for errors)",action="store_true",required=False)
parser.add_argument("-S","--SVG",help="print results also as SVG plots",action="store_true",required=False)
parser.add_argument("-T","--TNT",help="path to TnT executable (default=tnt)",default="tnt",required=False,metavar="path")
parser.add_argument("-V","--version",help="print version and quit",action="store_true")
# parser.add_argument("--font_size",help="font-size in px for SVG plots (default = 10)",type=int,default=10,required=False,metavar="int")
parser.add_argument("--font_weight",help="font format (e.g., normal, bold, bolder, lighter) for SVG plots (default = bold)",type=str,default="bold",required=False,metavar="str")
parser.add_argument("--font_family",help="Font format(default = Arial)",type=str,default="Arial",required=False,metavar="str")
parser.add_argument("--plot_size",help="plot size in px (default = 25.0)",type=float,default=25.0,required=False,metavar="float")
parser.add_argument("--hold",type=int,help="TNT will keep up to N trees",default=1000,required=False,metavar="int")
parser.add_argument("--mxram",type=int,help="Maximun Use N Mbytes of RAM available for TNT",default=512,required=False,metavar="int")
parser.add_argument("--svg_constraint",help="print only selected type of transformations (1. unique, non-homoplastic; 2. unique, homoplastic; 3. non-unique, homoplastic; 4. ambiguous; leave it blank to print them all)",type=int,nargs="+",required=False,metavar="space-separated str")
parser.add_argument("--text_position",help="vertical text adjustment for characters (default = 0)",type=int,default=0,required=False,metavar="int")

args=parser.parse_args()

if(args.version):
	print("ybyra_apo.py version 2017.01.02")
	exit()

if(args.NO_MESSAGES):args.verbose=False
else:
	MESSAGE="""
ybyra_apo.py is part of the YBYRÁ project

YBYRÁ - Copyright (C) 2014 - Denis Jacob Machado

	YBYRÁ comes with ABSOLUTELY NO WARRANTY!
	These are free software, and you are welcome to
	redistribute them under certain conditions.
	For additional information, please visit:
	http://opensource.org/licenses/GPL-3.0

	YBYRÁ is available at
	www.ib.usp.br/grant/anfibios/researchSoftware.html

FORMATTING NOTE

	Input trees must be in TREAD format.
	Input matrices must be in simplified Nexus format
	(DATA block only).
	Taxon names must be identical in the matrix and in
	every tree.
	Taxon names can be as large as 80 characters.

CHARACTER NUMBER

	First character is 0, not 1
"""
	print(MESSAGE)
	try:raw_input("Press Enter to continue...")
	except:input("Press Enter to continue...")

def getStarted():
# Create TnT script
	if not args.root:
		tnt_script="""log %s.log;
Mxram %d ;
taxname +100 ;
NSTATES 32 ;
proc %s ;
hold %d ;
proc %s ;
taxname=;
apo [-;
ttags-;
ttags(;
naked-;
nelsen;
ttags);
tplot;
tsave *%s.tre;
save*;
tsave/;
log/;
quit"""%(args.output,args.mxram,args.matrix,args.hold,args.trees,args.output)
	else:
		tnt_script="""log %s.log;
Mxram %d ;
taxname +100 ;
NSTATES 32 ;
proc %s ;
hold %d ;
proc %s ;
taxname=;
OUTGROUP %s ;
REROOT ;
apo [-;
ttags-;
ttags(;
naked-;
nelsen;
ttags);
tplot;
tsave *%s.tre;
save*;
tsave/;
log/;
quit"""%(args.output,args.mxram,args.matrix,args.hold,args.trees,args.root,args.output)
# TnT command apo [- plot synapomorphies common all trees and prints them in the form of lists instead of plotting them on the tree
# 	Test scripting
	tnt_script_name="%s.run"%(args.output)
	handle=open(tnt_script_name,"w")
	handle.write(tnt_script)
	handle.close()
# Execute TnT script
	try:subprocess.call([args.TNT, "proc",tnt_script_name,";"])
	except:
		print("!ERROR executing TnT's script '%s' (check path to tnt executable)\n"%(tnt_script_name))
		exit()
	getConsensus()

def getConsensus():
# Edit consensus tree
	consensus_tree="%s.tre"%(args.output)
	handle=open(consensus_tree,"r")
	consensus_tree=handle.read()
	handle.close()
	consensus_tree=re.sub("tread\s+'[^']+'\s+","",consensus_tree)
	consensus_tree=re.sub("\s*proc.*;\s*","",consensus_tree)
	consensus_tree=re.compile("[^(]*(.+)").findall(consensus_tree)[0]
	consensus_tree=re.sub(r"\s*=\s*([\d]+)[^\s()]*",r":\1",consensus_tree)
	consensus_tree=re.sub(r"\s*([^:]+:\d+)\s*",r"\1,",consensus_tree)
	consensus_tree=re.sub(r"(,\s*\))",r")",consensus_tree)
	consensus_tree=re.sub(r"(,\s*;)",r";",consensus_tree)
	output="%s_nodes.tre"%(args.output)
	handle=open(output,"w")
	handle.write(consensus_tree)
	handle.close()
	nodes=[]
	nodes+=sorted(re.compile("([^():,]+):\s*\d+").findall(consensus_tree))
	numbers=sorted(re.compile(":\s*([\d]+)").findall(consensus_tree))
	for n in numbers:
		n="Node %s"%(n)
		nodes+=[n]
	consensus_tree=re.sub(":\s*[^(),;\s]+\s*","",consensus_tree)
	terminals=re.compile("([^(),;\s]+)").findall(consensus_tree)
	getSynapomorphies(nodes,terminals)

def getSynapomorphies(nodes,terminals):
	characters,length=getCharacters(terminals)
	clades=getClades()
# Get synapomorphies from log
	log_file="%s.log"%(args.output)
	if(not os.path.isfile(log_file)):
		print("!ERROR: file %s not found"%(log_file))
		exit()
	else:
		handle=open(log_file,"r")
		log=handle.read()
		handle.close()
	log=re.compile("\(Node numbers refer to nodes in consensus\)(.+)Naked",re.DOTALL).findall(log)[0]
	for n in nodes:
		find="\s*%s\s*:"%(n)
		replace="\n#%s"%(n)
		log=re.sub(find,replace,log)
		log=re.sub("\:\s*\n#","\n#",log)
	log=re.sub("\n"," ",log)
	log=re.sub("\s+"," ",log)
	log=re.sub("#","\n#",log)
	log=re.sub("#.+\s+No\s+\w+pomorphies\s*","",log)
	log=re.sub(r"#Node ([^\s]+)\s+",r"'Node \1',",log)
	log=re.sub(r"#([^\s]+)\s+",r"\n'\1',",log)
	log=re.sub("Some\s+trees\s*:.+","",log)
	log=re.sub("\s*All\s+trees\s*:\s+","",log)
	synapomorphies={}
	for node in nodes:
		pattern="'%s'(.+)"%(node)
		found=re.compile(pattern).findall(log)
		if(found):
			chars=re.compile("Char\.\s+(\d+):").findall(found[0])
			if(chars):
				pairs=[]
				for char in chars:
					pattern="Char\.\s+%s\s*:\s*[^>]+>\s*([^\s]+)"%(char)
					state=re.compile(pattern).findall(found[0])
					pairs+=[[int(char),state[0]]]
				synapomorphies[node]=pairs
	if(args.verbose)and(synapomorphies):
		print(">Unambiguous synapomorphies [char. no., state]:")
		for key in sorted(synapomorphies):
			print("%s: %s"%(key,synapomorphies[key]))
	log=re.sub(r"Char\.\s*(\d+)\s*:\s*([^\s]+)\s*-->\s*([^\s]+)",r"'\1(\2-\3)',",log)
	log=re.sub("No autapomorphies|No synapomorphies","'EMPY',",log)
	log="'NODE','NON-AMBIGUOUS SYNAPOMORPHIES FOR EACH NODE'%s\n'See %s_nodes.tre'"%(log,args.output)
	log=re.sub(",\s*\n","\n",log)
	csv_file="%s.csv"%(args.output)
	handle=open(csv_file,"w")
	handle.write(log)
	handle.close()
	exclusive=getExclusive(clades,characters,length,terminals)
	special,nonspecial=exclusiveSynapomorphies(synapomorphies,exclusive)
	private,nonprivate=privateSynapomorphies(nonspecial,clades,terminals,characters)
	output="'Nodes','Unambiguous synapomorphies (character no.: character state)'\n"
	for key in sorted(synapomorphies):
		edited=str(synapomorphies[key])
		edited=re.sub("'|\s","",edited)
		edited=re.sub("\[\[|\]\]","'",edited)
		edited=re.sub("\],\[","','",edited)
		edited=re.sub("'\]","]'",edited)
		output+="'%s',%s\n"%(key,edited)
	output+="'','Exclusive character states (character no.: character state)'\n"
	for key in sorted(exclusive):
		edited=str(exclusive[key])
		edited=re.sub("'|\s","",edited)
		edited=re.sub("\[\[|\]\]","'",edited)
		edited=re.sub("\],\[","','",edited)
		edited=re.sub("'\]","]'",edited)
		output+="'%s',%s\n"%(key,edited)
	output+="'','Exclusive synapomorphies (character no.: character state)'\n"
	for key in sorted(special):
		edited=str(special[key])
		edited=re.sub("'|\s","",edited)
		edited=re.sub("\[\[|\]\]","'",edited)
		edited=re.sub("\],\[","','",edited)
		edited=re.sub("'\]","]'",edited)
		output+="'%s',%s\n"%(key,edited)
	output+="'','Private synapomorphies (character no.: character state)'\n"
	for key in sorted(private):
		edited=str(private[key])
		edited=re.sub("'|\s","",edited)
		edited=re.sub("\[\[|\]\]","'",edited)
		edited=re.sub("\],\[","','",edited)
		edited=re.sub("'\]","]'",edited)
		output+="'%s',%s\n"%(key,edited)
	output+="'','Non-private synapomorphies (character no.: character state)'\n"
	for key in sorted(nonprivate):
		edited=str(nonprivate[key])
		edited=re.sub("'|\s","",edited)
		edited=re.sub("\[\[|\]\]","'",edited)
		edited=re.sub("\],\[","','",edited)
		edited=re.sub("'\]","]'",edited)
		output+="'%s',%s\n"%(key,edited)
	out_file="%s_characters.csv"%(args.output)
	handle=open(out_file,"w")
	handle.write(output)
	handle.close()
	if(args.verbose):
		MESSAGE="""
	A table with synapomorphies and exclusive characters
	was saved as %s_characters.csv.
	Node numbers correspond to branch labels in
	%s_nodes.tre.

NOTE:
	Characters were optimized on every tree from
	%s.
	Consensus was not used for optimization.
"""%(args.output,args.output,args.trees)
		print(MESSAGE)
	if(args.SVG):printSvg(special,private,nonprivate,exclusive,length,terminals)

def getCharacters(terminals):
	MATRIX="%s"%(args.matrix)
	handle=open(MATRIX,"r")
	matrix=handle.read()
	handle.close()
	try:
		matrix=re.compile("matrix\s+([^;]+)\s+;",re.IGNORECASE|re.DOTALL).findall(matrix)[0]
	except:
		matrix=re.compile("xrea[^\n\r]+[\n\r\s]+(.+?);",re.IGNORECASE|re.DOTALL).findall(matrix)[0]
	characters={}
	for node in terminals:
		pattern="%s\s+(.+)\s*"%(node)
		line=re.compile(pattern).findall(matrix)
		line=re.sub(r"[\s]","",line[0])
		STATES=[]
		for i in line:STATES+=[i]
		states=[]
		if(STATES.count("{")):
			while(STATES.count("{")):
				x=STATES.index("{")
				y=STATES.index("}")
				head=[]
				if(x!=0):
					head=STATES[0:x]
				body=STATES[x+1:y]
				states+=head+[body]
				tail=[]
				if(y!=len(STATES)-1):
					tail=STATES[y+1:]
				STATES=tail
			states+=STATES
		elif(STATES.count("[")):
			while(STATES.count("[")):
				x=STATES.index("[")
				y=STATES.index("]")
				head=[]
				if(x!=0):
					head=STATES[0:x]
				body=STATES[x+1:y]
				states+=head+[body]
				tail=[]
				if(y!=len(STATES)-1):
					tail=STATES[y+1:]
				STATES=tail
			states+=STATES
		else:
			states=STATES
		characters[node]=states
		length=len(states)
	return[characters,length]

def getClades():
	tree="%s_nodes.tre"%(args.output)
	handle=open(tree,"r")
	tree=handle.read()
	handle.close()
	clades={}
	while True:
		subtree=re.compile("(\([^()]+\):\d+)").findall(tree)
		if(subtree):
			for i in subtree:
				node="Node %s"%(re.compile("\):(\d+)").findall(i)[0])
				j=re.sub("\(|\)|:\d+","",i)
#				 terminals=sorted(list(Set(re.compile("([^(),]+)").findall(j))))
				terminals=sorted(list(set(re.compile("([^(),]+)").findall(j))))
				clades[node]=terminals
				tree=tree.replace(i,j)
		else:break
	return clades

def getExclusive(clades,characters,length,terminals):
	exclusive={}
	for node in clades: # for each internal node
		char=[]
		for n in range(0,length): # for each character
			add=True
			state=[]
			for terminal in clades[node]:
				state+=[characters[terminal][n]] # get character states
			if(state.count(state[0])==len(state)): # if character state is stable inside the node
				candidate=state[0]
				for outside_terminal in characters: # compare with the rest of the terminals
#					 if(outside_terminal not in clades[node])and(Set(candidate)&Set(characters[outside_terminal][n])): # stop if it is not exclusive
					if(outside_terminal not in clades[node])and(set(candidate)&set(characters[outside_terminal][n])): # stop if it is not exclusive
						add=False
						break
			else:
				add=False # stop if there is no exclusive character was found
			if(add==True):
				char+=[[n,candidate]]
		if(char):
			exclusive[node]=char
	for terminal in terminals: # for each terminal node
		char=[]
		for n in range(0,length): # for each character
			add=True
			candidate=characters[terminal][n] # get character state
			others=[]
			for other_terminal in terminals: # compare with the rest of the terminals
#				 if(not other_terminal==terminal)and(Set(candidate)&Set(characters[other_terminal][n])):
				if(not other_terminal==terminal)and(set(candidate)&set(characters[other_terminal][n])):
					add=False
					break
			if(add==True):
				char+=[[n,candidate]]
		if(char):
			exclusive[terminal]=char
	if(args.verbose)and(exclusive):
		print(">Exclusive character states [char. no., state]:")
		for key in sorted(exclusive):
			print("%s: %s"%(key,exclusive[key]))
	return exclusive

def exclusiveSynapomorphies(synapomorphies,exclusive):
	special={}
	nonspecial={}
	for key in synapomorphies:
		selected=[]
		unselected=[]
		for char in synapomorphies[key]:
			if(key in exclusive):
				if char in exclusive[key]:
					selected+=[char]
				else:unselected+=[char]
			else:unselected+=[char]
		if(selected):special[key]=selected
		if(unselected):nonspecial[key]=unselected
	if(args.verbose)and(special):
		print(">Exclusive synapomorphies ('pure') [char. no., state]:")
		for key in sorted(special):
			print("%s: %s"%(key,special[key]))
	if(args.verbose)and(nonspecial):
		print(">Non-exclusive synapomorphies [char. no., state]:")
		for key in sorted(nonspecial):
			print("%s: %s"%(key,nonspecial[key]))
	return [special,nonspecial]

def privateSynapomorphies(nonspecial,clades,terminals,characters):
	private={}
	nonprivate={}
	for key in nonspecial:
		if(key in terminals):
			for item in nonspecial[key]:
				character,state=item
				isPrivate=True
				for terminal in terminals:
					if(not terminal==key)and(characters[terminal][character]==state):
						isPrivate=False
						break
				if(isPrivate==True)and(not key in private):private[key]=[item]
				elif(isPrivate==True)and(key in private):private[key]+=[item]
				elif(isPrivate==False)and(not key in nonprivate):nonprivate[key]=[item]
				else:nonprivate[key]+=[item]
		elif(key in clades):
			for item in nonspecial[key]:
				character,state=item
				isPrivate=True
				for terminal in terminals:
					if(not terminal in clades[key])and(characters[terminal][character]==state):
						isPrivate=False
						break
				if(isPrivate==True)and(not key in private):private[key]=[item]
				elif(isPrivate==True)and(key in private):private[key]+=[item]
				elif(isPrivate==False)and(not key in nonprivate):nonprivate[key]=[item]
				else:nonprivate[key]+=[item]
	return [private,nonprivate]

def printSvg(special,private,nonprivate,exclusive,length,terminals):
	try:
		import svgwrite
	except:
		print(">ERROR: Could not find package svgwrite.\n[Package information: <https://pypi.python.org/pypi/svgwrite/>]")
		exit()
	nodes=[]
	if(args.svg_constraint):
		svg_constraint=args.svg_constraint
	else:
		svg_constraint=[1,2,3,4]
	if(1 in svg_constraint):
		for key in special:
			nodes+=[key]
	if(2 in svg_constraint):
		for key in nonprivate:
			if(not key in nodes):
				nodes+=[key]
	if(3 in svg_constraint):
		for key in private:
			if(not key in nodes):
				nodes+=[key]
	if(4 in svg_constraint):
		for key in exclusive:
			if(not key in nodes):
				nodes+=[key]
	nodes=sorted(nodes)
	for node in nodes:
		characters={} # character and color
		states={} # character and state
		if(node in exclusive)and(4 in svg_constraint):
			for i in exclusive[node]:
				characters[i[0]]="white"
				states[i[0]]=i[1]
		if(node in private)and(3 in svg_constraint):
			for i in private[node]:
				characters[i[0]]="blue"
				states[i[0]]=i[1]
		if(node in nonprivate)and(2 in svg_constraint):
			for i in nonprivate[node]:
				characters[i[0]]="red"
				states[i[0]]=i[1]
		if(node in special)and(1 in svg_constraint):
			for i in special[node]:
				characters[i[0]]="black"
				states[i[0]]=i[1]
		svgFilename="%s_%s.svg"%(args.output,re.sub("\s","_",node))
		dwg=svgwrite.Drawing(filename=svgFilename,size=(u'100%', u'100%'))
		x=0
		for key in sorted(characters):
			x+=1
			CHAR=str(key)
			STATE=str(states[key])
			COLOR=str(characters[key])
			if(COLOR=="white"):
				TEXT="black"
			else:
				TEXT="white"
			X1=(x-1)*args.plot_size
			X2=(args.plot_size/2.0)+(x-1)*args.plot_size
			dwg.add(dwg.rect(insert=(X1,0),
				size=("{}px".format(args.plot_size),"{}px".format(args.plot_size)), # The relation between the absolute units is as follows: 1in = 2.54cm = 25.4mm = 72pt = 6pc
				stroke_width="{}".format( 1*(args.plot_size/25.0)  ),
				stroke="black",
				fill=COLOR))
			dwg.add(dwg.text(STATE,
				insert=(X2,  17.5*(args.plot_size/25.0) ),
				fill=TEXT,
				# style="font-size:%dpx;font-family:%s;font-weight:%s;text-anchor:middle"%(args.font_size,args.font_family,args.font_weight)))
				style="font-size:%dpx;font-family:%s;font-weight:%s;text-anchor:middle"%( 10.0*(args.plot_size/25.0) ,args.font_family,args.font_weight)))
			dwg.add(dwg.text(CHAR,
				insert=(X2, 35*(args.plot_size/25.0) + args.text_position),
				fill="black",
				# style="font-size:%dpx;font-family:%s;font-weight:%s;text-anchor:middle"%(args.font_size,args.font_family,args.font_weight)))
				style="font-size:%dpx;font-family:%s;font-weight:%s;text-anchor:middle"%( 10.0*(args.plot_size/25.0) ,args.font_family,args.font_weight)))
		dwg.save()
	if(args.verbose):
		MESSAGE="""
SVG files successfully written to disk.
	Character states are at the center of each cell
	Character number are at the bottom of each cell
			(character counting starts at 0, not 1)
	Black cells are unambiguous, unique, non-homoplastic synapomorphies
	Red cells are unambiguous, non-private synapomorphies
	Blue cells are unambiguous, private synapomorphies
	White cells are ambiguous optimized synapomorphies
"""
		print(MESSAGE)


getStarted()

# 	VARIABLES:
# 	characters: character matrix with character states
# 	synapomorphies: list of sinapomorphies
# 	clades: terminals per node

exit()
