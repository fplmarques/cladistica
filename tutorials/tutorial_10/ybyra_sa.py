#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# ybyra_sa.py

# YBYRÁ - Copyright (C) 2014 - Denis Jacob Machado
# GNU General Public License version 3.0

# Denis Jacob Machado
# denisjacobmachado@gmail.com
# www.ib.usp.br/grant/anfibios/researchSoftware.html

COPYRIGTH="""
ybyra_sa.py is part of the YBYRÁ project

YBYRÁ - Copyright (C) 2014 - Denis Jacob Machado

    YBYRÁ comes with ABSOLUTELY NO WARRANTY!
    These are free software, and you are welcome to
    redistribute them under certain conditions
    For additional information, please visit:
    http://opensource.org/licenses/GPL-3.0

    YBYRÁ is available at
    www.ib.usp.br/grant/anfibios/researchSoftware.html
"""
print(COPYRIGTH)

###MODULES AND LIBRARIES###
# from cStringIO import StringIO
from io import StringIO
import argparse,itertools,linecache,math,re

###GET ARGUMENTS###
parser=argparse.ArgumentParser()
parser.add_argument("-v","--verbose",help="increase output verbosity",action="store_true")
parser.add_argument("-f","--configuration",help='specifies which configuration file to use',metavar="<configuration file name>",default="configuration.txt")
parser.add_argument("-d","--different",help="trees have different terminals",action="store_true")
parser.add_argument("-m","--msdist",help="prunes trees for MSdist",action="store_true")
parser.add_argument("-w","--wildcards",help="lists possible rogue taxa",action="store_true")
parser.add_argument("-c","--clear",help="removes YBYRÁ's output files from current directory",action="store_true")
parser.add_argument("-V","--version",help="print version and quit",action="store_true")
parser.add_argument("--text_position",help="vertical text adjustment for text (default = 0)",type=int,default=0)
parser.add_argument("--font_size",help="font-size in px for SVG plots (default = 24)",type=int,default=24)
parser.add_argument("--font_weight",help="font-weight (e.g., normal, bold, bolder, lighter) for SVG plots (default = bold)",type=str,default="bold")
args=parser.parse_args()

if(args.version):
    print("ybyra_sa.py version 2022.03.02")
    exit()

###CLEAN-UP###
if(args.clear):
    print("#Cleaning up...")
    import glob,os
    prefixes=["SCRIPT_*.sh","PRUNED_*.trees","LIST_*.csv","MATCHES_*.txt","TREES_*.tre","COMMENTS_*.txt","BRACKETS_*.txt","CLADES_*.txt","SPLITS_*.txt","MATRIX_*.tsv","SA_*.tsv","LABELED_*.tre","RUG_*.svg","MSDIST_*.txt"]
    for prefix in prefixes:
        files2remove=glob.glob(prefix)
        for file in files2remove:
            try:
                os.remove(file)
            except:
                print("--Could not find/remove %s"%(prefix))
    print(">Done!")
    exit()

###FUNCTIONS###
class Tree:
    def __init__(t,inputfile,root,output,tree_number,sa,svg,pools,compare_opt,stroke,color,text,verbose,captions,treeCount,listOfClades,msdistInConfig):
        t.inputfile=inputfile
        t.root=root
        t.output=output
        t.n=int(tree_number)
        t.sa=str(sa)
        t.svg=svg
        t.sa_pools=pools
        t.compare_opt=compare_opt
        t.stroke=stroke
        t.color=color
        t.text=text
        t.verbose=verbose
        t.constrictTreeList=[]
        if(not t.sa_pools=="n"):
            for subList in t.sa_pools:
                for treeNumber in subList:
                    t.constrictTreeList+=[int(treeNumber)]
            t.constrictTreeList=sorted(set(t.constrictTreeList))
        t.caption=captions
        t.trees="TREES_"+t.output+".tre"
        t.costs="COMMENTS_"+t.output+".txt"
        t.count_trees=treeCount
        t.listOfClades=listOfClades
        t.msdist_path=msdistInConfig

    def lines(t): # Be sure that there is one tree per line when only one input tree file is given
        print("#Pruning trees...")
        with open (t.inputfile,"r") as input:
            new_costs_lines=""
            trees=input.read()
            trees=re.sub("[\s*]","",trees)
            trees=re.sub(":[^(^)^,^;^\[^\]]+","",trees)
            trees=trees.replace(");",")[No_Comment];")
            trees=re.sub(";",r";\n",trees)
            all_comments=re.compile("\[(\S+)").findall(trees)
            costs=open(t.costs,"w")
            t.count_trees=1
            for comments in all_comments:
                if((t.constrictTreeList.count(t.count_trees))or(t.n==t.count_trees)):
                    new_costs_lines+="Tree No. "+str(t.count_trees)+":\t"+re.sub(r"];","",str(comments))+"\t(tree no. "+str(t.count_trees)+" in file "+t.inputfile+")"+"\n"
                else:
                    new_costs_lines+="#\n"
                t.count_trees+=1
            costs.write(new_costs_lines)
            costs.close()
            trees=re.sub("\[(\S+)","",trees)
            try:
                trees=re.sub(r"\r\n",r";\r\n",trees)
            except:
                trees=re.sub(r"\n",r";\n",trees)
            output=open(t.trees,"w")
            output.write(trees)
            output.close()
            input.close()
        if(t.verbose==1):
            print(">Found %d trees (%s selected).\n>File %s was created."%(t.count_trees-1,len(t.constrictTreeList),t.trees))

    def test_brackets(t): # Check brackets
        print("#Checking brackets...")
        trees=open(t.trees,"r")
        totalCount=0
        currentCount=0
        for tree in trees.readlines():
            totalCount+=1
            if((t.constrictTreeList.count(totalCount))or(t.n==totalCount)):
                currentCount+=1
                openbra=re.compile("[(]").findall(tree)
                closbra=re.compile("[)]").findall(tree)
                nopenbra=len(openbra) # Count "("
                nclosbra=len(closbra) # Count ")"
                if not nopenbra==nclosbra:
                    originalFile=linecache.getline(t.costs,totalCount)
                    originalFile=re.compile("\((.*)\)").findall(originalFile)
                    print(">ERROR: Missing brackets: %s!"%originalFile[0])
                    exit()
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                    print("-Bracket check : Tree No. %d OK! (%d of %d)."%(totalCount,currentCount,len(t.constrictTreeList)))
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                    print("-Bracket check : Tree No. %d OK! (%d of %d)."%(totalCount,currentCount,len(t.constrictTreeList)+1))
        trees.close()

    def test_terminals(t): # Check terminals and make a list
        if(args.different): # Removes terminals that are not in every tree
            print("#Removing terminals that are not in every tree...")
            t.removedTerminals=[]
            try:
                from Bio import Phylo
            except ImportError:
                print(">ERROR: Could not load Biopyhton module. Will not be able to use trees with different terminals. [Module information: <http://biopython.org/wiki/Main_Page>]")
            else:
                from Bio import Phylo
#                 from sets import Set
                trees=Phylo.parse(t.trees,"newick")
                commonTerminals=[]
                count=0
                for tree in trees:
                    count+=1
                    if((not t.constrictTreeList)or(count in t.constrictTreeList)or(t.n==count)):
                        names=[]
                        for clade in tree.get_terminals():
                            if(clade.name):
                                if clade.name in names:
                                    print(">ERROR: Duplicate terminal name (%s)."%clade.name)
                                    exit()
                                names+=[clade.name]
                        if not commonTerminals:
                            commonTerminals=names
#                         else:commonTerminals=list(Set(commonTerminals)&Set(names))
                        else:
                            commonTerminals=list(set(commonTerminals)&set(names))
                trees=Phylo.parse(t.trees,"newick")
                prunned_trees=[]
                count=0
                for tree in trees:
                    count+=1
                    if((not t.constrictTreeList)or(count in t.constrictTreeList)or(t.n==count)):
                        for clade in tree.get_terminals():
                            if(clade.name):
                                if(not clade.name in commonTerminals):
                                    tree.prune(clade)
                                    if not clade.name in t.removedTerminals:
                                        t.removedTerminals+=[clade.name]
                    prunned_trees+=[tree]
                Phylo.write(prunned_trees,t.trees,"newick")
                print(">%d terminal(s) removed."%(len(t.removedTerminals)))
        print("#Checking terminals...")
        readTheTrees=open(t.trees,"r")
        countLines=1
        tree1=""
        for line in readTheTrees.readlines():
            if(countLines==t.n):
                tree1=line
                break
            countLines+=1
        readTheTrees.close()
        tree1=re.sub(":\d*\.*\d*","",tree1)
        t.terminals=re.compile("[(),]?(\w+)[(),;]?").findall(tree1)
        t.terminals=sorted(t.terminals)
        trees=open(t.trees,"r")
        totalCount=0
        currentCount=0
        for tree in trees:
            tree=re.sub(":\d*\.*\d*","",tree)
            totalCount+=1
            if((t.constrictTreeList.count(totalCount))or(t.n==totalCount)):
                currentCount+=1
                terminals=re.compile("[(),]?(\w+)[(),;]?").findall(tree)
                terminals=sorted(terminals)
                if not terminals==t.terminals:
                    originalFile=linecache.getline(t.costs,totalCount)
                    originalFile=re.compile("\((.*)\)").findall(originalFile)
                    print(">ERROR: Terminals differs from the first tree: %s! | %d terminals."%(originalFile[0],len(terminals)))
                    print(">NOTE: Use the --diffent (-d) option if you want remove terminals that are not in every tree.")
                    exit()
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                    print("-Check terminals : Tree No. %d | %d terminals (%d of %d)."%(totalCount,len(terminals),currentCount,len(t.constrictTreeList)))
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                    print("-Check terminals : Tree No. %d | %d terminals (%d of %d)."%(totalCount,len(terminals),currentCount,len(t.constrictTreeList)+1))
        trees.close()
        if(t.verbose==1):
            print(">%d terminals were found in each selected tree."%(len(t.terminals)))

    def roots(t): # Root each tree the same and remove Split labels
        try:
            from Bio import Phylo
        except ImportError:
            print(">ERROR: Could not load Biopyhton module. Trees will not be (re)rooted. [Module information: <http://biopython.org/wiki/Main_Page>]")
        else:
            from Bio import Phylo
            print("#Rooting selected trees | Phylo module...")
            trees=Phylo.parse(t.trees,"newick")
            root=t.root
            rooted_trees=[]
            count=0
            for tree in trees:
                count+=1
                if(t.constrictTreeList.count(count)or(t.n==count)):
                    try:
                        tree.root_with_outgroup(root)
                    except ValueError:
                        print(">ERROR: Could not find terminal %s in tree no. %d"%(root,count))
                        exit()
                    else:
                        print("-Rooting tree no. %d"%count)
                rooted_trees+=[tree]
            Phylo.write(rooted_trees,t.trees,"newick")
            if(t.verbose==1):
                print(">Trees (re-)rooted in %s."%(t.root))
                print(">The (re-)rooted trees were saved in %s."%(t.trees))
                print(">Start pruning trees...")
            readFromFile=open(t.trees,"r")
            new_lines=""
            for tree in readFromFile.readlines():
                new_lines=new_lines+re.sub(":\+*\-*[0-9]*\.*[0-9]*","",tree)
            readFromFile.close()
            write2file=open(t.trees,"w")
            write2file.write(new_lines)
            write2file.close()
            if(t.verbose==1):
                print(">Rooting is done.")

    def msdist_prune(t): # Prepare files for MSdist 0.5 analysis
        print("#Pruning trees for MSdist...")
        from Bio import Phylo
#         from sets import Set
        trees=Phylo.parse(t.trees,"newick")
        scriptName="SCRIPT_"+t.output+".sh"
        script=open(scriptName,"w")
        script.close()
        try:
            firstTree=trees.next()
        except:
            firstTree=next(trees)
        terminals=firstTree.get_terminals()
        for terminal in terminals:
            list=[]
            trees=Phylo.parse(t.trees,"newick")
            count=0
            for tree in trees:
                count+=1
                if((not t.constrictTreeList)or(count in t.constrictTreeList)or(t.n==count)):
                    names={}
                    for clade in tree.get_terminals():
                        if clade.name:
                            if clade.name in names:
                                raise ValueError("Duplicate key: %s"%clade.name)
                            names[clade.name]=clade
                    tree.prune(names[str(terminal)])
                    list+=[tree]
            outputName="PRUNED_"+str(terminal)+".trees"
            Phylo.write(list,outputName,"newick")
            scriptLine="java -jar MSdist.jar -m -i "+outputName+" -o MSDIST_"+str(terminal)+".txt\n"
            script=open(scriptName,"a")
            script.write(scriptLine)
            script.close()
        MESSAGE=">Use the PRUNED tree files to locate potentially problematic terminals\n-Step 1: Move the PRUNED tree files and the %s to MSdit/bin/\n-Step 2: Execute the bash script %s from the MSdist/bin/ directory: $ sh %s\n-Step 3: Copy the MSDIST text files back to the ybyra_sa.py directory\n-Step 4: Examine the results with the --wildcards (-w) option\n"%(scriptName,scriptName,scriptName)
        if(t.msdist_path=="empty"):
            print(MESSAGE)
        else:
            print("#Runing MSdist at %s"%(t.msdist_path))
            currentDirectory=os.getcwd()
            for terminal in terminals:
                subprocess.call("mv PRUNED_%s.trees %s"%(terminal,t.msdist_path),shell=True)
            subprocess.call("mv %s %s"%(scriptName,t.msdist_path),shell=True)
            subprocess.call("sh %s"%(scriptName),shell=True,cwd=t.msdist_path)
            for terminal in terminals:
                subprocess.call("rm PRUNED_%s.trees"%(terminal),shell=True,cwd=t.msdist_path)
            subprocess.call("rm %s"%(scriptName),shell=True,cwd=t.msdist_path)
            for terminal in terminals:
                subprocess.call("mv MSDIST_%s.txt %s"%(terminal,currentDirectory),shell=True,cwd=t.msdist_path)

    def msdist_results(t): # Examine MSdist results and make a list of possible wildcards
        print("#Examining MSdist output...")
        import glob,os
        means=[]
        FILE_TIPE="MSDIST*.txt"
        for STATSFILE in glob.iglob(os.path.join(FILE_TIPE)):
            with open(STATSFILE,"r") as result:
                data=result.readlines()
                lastLine=data[len(data)-1]
                terminal=re.compile("MSDIST\_(.+)\.txt").findall(STATSFILE)
                terminal=terminal[0]
                mean=re.compile("MatchingSplit\s+(\d+\.*\d+)").findall(lastLine)
                mean=float(mean[0])
                means+=[[mean]+[terminal]]
            result.close()
        outputName="LIST_"+t.output+".csv"
        output=open(outputName,"w")
        outputInfo="\'Teminal name','Avg. distances'\n"
        for mean in sorted(means):
            outputInfo+="\'"+str(mean[1])+"','"+str(mean[0])+"\'\n"
        output.write(outputInfo)
        output.close()
        print(">The list of terminals that most affect distances was printed in %s."%outputName)

    def list_positions(t): # List brackets positions in each tree. This will be used to identify clades
        print("#Listing the position of brackets...")
        t.positions="BRACKETS_"+t.output+".txt"
        positions=open(t.positions,"w")
        positions.close()
        tree_file=open(t.trees,"r")
        positions=open(t.positions,"a")
        count=0
        generalCount=0
        for tree in tree_file.readlines():
            count+=1
            if(t.constrictTreeList.count(count)or(t.n==count)):
                generalCount+=1
                if((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                    print("-Recording brackets positions : Tree No. %d (%d of %d)."%(count,generalCount,len(t.constrictTreeList)))
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                    print("-Recording brackets positions : Tree No. %d (%d of %d)."%(count,generalCount,len(t.constrictTreeList)+1))
                countopenbrackets=0
                listopenbrackets=[]
                listclosebrackets=[]
                for char1 in tree:
                    if char1=="(":
                        listopenbrackets+=[countopenbrackets]
                        countclosebrackets=countopenbrackets+1
                        countPairs=1
                        for char2 in tree[countopenbrackets+1:
                            len(tree)-1]:
                            if char2=="(":
                                countPairs+=1
                            elif char2==")":
                                countPairs-=1
                                if countPairs==0:
                                    if(listclosebrackets.count([countclosebrackets])==0):
                                        listclosebrackets+=[countclosebrackets] # Builds list of closing brackets positions
                                    break
                            countclosebrackets+=1
                    countopenbrackets+=1
                listopenbrackets=str(listopenbrackets)
                listclosebrackets=str(listclosebrackets)
                positionsline=listopenbrackets+"\t"+listclosebrackets+"\n"
            else:
                positionsline="#\n"
            positions.write(positionsline)
        positions.close()
        tree_file.close()
        if(t.verbose==1):
            print(">The file %s was created"%t.positions)

    def list_clades(t):
        if(t.verbose==1):
            print("#Searching for clades...")
        t.groups="CLADES_"+t.output+".txt"
        clades_file=open(t.groups,"w")
        clades_file.close()
        clades_file=open(t.groups,"a")
        t.all_clades=[]
        generalCounter=0
        with open(t.positions,"r") as positions:
            for lineno,linestr in enumerate(positions,1):
                if(t.constrictTreeList.count(lineno)or(t.n==lineno)):
                    generalCounter+=1
                    if((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                        print("-Listing clades : Tree No. %d (%d of %d)."%(lineno,generalCounter,len(t.constrictTreeList)))
                    elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                        print("-Listing clades : Tree No. %d (%d of %d)."%(lineno,generalCounter,len(t.constrictTreeList)+1))
                    cladesline=""
                    linestr=re.sub(r"[\[\]()\n ]","",linestr)
                    stropenbrackets,strclosebrackets=linestr.split("\t")
                    listopenbrackets=[int(n) for n in stropenbrackets.split(",")]
                    listclosebrackets=[int(n) for n in strclosebrackets.split(",")]
# Get tree
                    readTheTrees=open(t.trees,"r")
                    countLines=1
                    tree=""
                    for line in readTheTrees.readlines():
                        if(countLines==lineno):
                            tree=line
                            break
                        countLines+=1
                    readTheTrees.close()
# Get clades from each tree
                    for item2 in range(len(listopenbrackets)):
                        min=int(listopenbrackets[item2])
                        max=int(listclosebrackets[item2])
                        clade=tree[min:max]
                        clade=re.sub("r[\[\]\n().;]","",clade)
                        clade=clade.split(","or" ")
                        clade=sorted(clade)
# Creating global list of clades
                        if (len(clade)>=2 and t.all_clades.count(clade)==0):
                            t.all_clades+=[clade]
                        if cladesline.count(str(clade))==0:
                            cladesline+=str(clade)+"; "
                    cladesline="Tree No. "+str(lineno)+"\t"+cladesline[:len(cladesline)-2]+"\n"
                    clades_file.write(cladesline)
                else:
                    clades_file.write("#\n")
        t.ngroups=len(t.all_clades)
# Uncomment the following four lines to print footer with clade info
#        end_line=""
#        end_line="All clades:\t"+str(t.all_clades)+"\n" # Uncomment this line if you want to print all clades found
#        end_line+="Number of different clades:\t"+str(t.ngroups)+"\n" # Uncomment this line if you want to print the number of different clades found
#        clades_file.write(end_line)
        clades_file.close()
        if(t.verbose==1):
            print(">The file %s was created"%t.groups)

    def list_splits(t):
        print("#Searching for splits...")
        t.groups="SPLITS_"+t.output+".txt"
        splits_file=open(t.groups,"w")
        splits_file.close()
        splits_file=open(t.groups,"a")
        t.all_splits=[]
        generalCounter=0
        with open(t.positions,"r") as positions:
            for lineno,linestr in enumerate(positions,1):
                if(t.constrictTreeList.count(lineno)or(t.n==lineno)):
                    generalCounter+=1
                    if((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                        print("-Listing splits : Tree No. %d (%d of %d)."%(lineno,generalCounter,len(t.constrictTreeList)))
                    elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                        print("-Listing splits : Tree No. %d (%d of %d)."%(lineno,generalCounter,len(t.constrictTreeList)+1))
                    listsplits=[]
                    splitsline=""
                    linestr=re.sub("[\[\]()\n ]","",linestr)
                    stropenbrackets,strclosebrackets=linestr.split("\t")
                    listopenbrackets=[int(n) for n in stropenbrackets.split(",")]
                    listclosebrackets=[int(n) for n in strclosebrackets.split(",")]
# Get tree
                    readTheTrees=open(t.trees,"r")
                    countLines=1
                    tree=""
                    for line in readTheTrees.readlines():
                        if(countLines==lineno):
                            tree=line
                            break
                        countLines+=1
                    readTheTrees.close()
# Get clades from each tree
                    for item2 in range(len(listopenbrackets)):
                        min=int(listopenbrackets[item2])
                        max=int(listclosebrackets[item2])
                        clade=tree[min:max]
                        clade=re.sub(r"[\[\]\n().;]","",clade)
                        clade=clade.split(","or" ")
                        clade=sorted(clade)
# Getting splits for each tree
                        outlist=[]
                        for item in t.terminals:
                            if clade.count(item)==0:
                                outlist+=[item]
                        if(len(outlist)>=2):
                            outlist=sorted(outlist)
                        if (len(clade)>=2 and len(outlist)>=2):
                            listsplits=[clade]+[outlist]
                            listsplits=sorted(listsplits)
# Creating global list of splits
                            if t.all_splits.count(listsplits)==0:
                                t.all_splits+=[listsplits]
                            splitsline+=str(listsplits)+"; "
                    splitsline="Tree No. "+str(lineno)+"\t"+splitsline[:len(splitsline)-2]+"\n"
                    splits_file.write(splitsline)
        t.ngroups=len(t.all_splits)
        end_line=""
#         end_line="All splits:\t"+str(t.all_splits)+"\n" # Uncomment this line if you want to print all splits found
#         end_line+="Number of different splits:\t"+str(t.ngroups)+"\n" # Uncomment this line if you want to print the number of different splits found
        splits_file.write(end_line)
        splits_file.close()
        if(t.verbose==1):
            print(">The file %s was created"%t.groups)

    def match(t):
        if arg11==["0"]:
            print("#MATCHES: Comparing trees split by split...")
        elif arg11==["1"]:
            print("#MATCHES: Comparing trees clade by clade...")
        t.matches="MATCHES_"+t.output+".txt"# Defines file name for match file
        matches=open(t.matches,"w")
        matches.close()
        matches=open(t.matches,"a")
        matchlist_rooted=[]
        matchlist_unrooted=[]
# List clades of the chosen tree
        mainpositions=linecache.getline(t.positions,t.n)
        mainpositions=re.sub(r"[\[\]()\n ]","",mainpositions)
        stropenbrackets,strclosebrackets=mainpositions.split("\t")
        listopenbrackets=[int(n) for n in stropenbrackets.split(",")]#remake list of open brackets
        listclosebrackets=[int(n) for n in strclosebrackets.split(",")]#remake list of close brackets
        countLines=0
# Get tree
        readTheTrees=open(t.trees,"r")
        countLines=1
        tree=""
        for line in readTheTrees.readlines():
            if(countLines==t.n):
                tree=line
                break
            countLines+=1
        readTheTrees.close()
        templist=[]
        mainlist=[]
        for item in range(len(listopenbrackets)):
            min=int(listopenbrackets[item])
            max=int(listclosebrackets[item])
            clade=tree[min:max]
            clade=re.sub(r"[\[\]\n().;]","",clade)
            clade=clade.split(","or" ")
            templist+=[clade]
# Sorting main list
        for clade in templist:
            clade=sorted(clade)
# Clades to splits
            if arg11==["0"]:
                outlist=[]
                for item in t.terminals:
                    if clade.count(item)==0:
                        outlist+=[item]
                if(len(outlist)>=2):
                    outlist=sorted(outlist)
                newSplit=[clade]+[outlist]
            elif arg11==["1"]:
                newSplit=[clade]
            if(arg11==["0"] and len(clade)>=2 and len(outlist)>=2 and mainlist.count([newSplit])==0):
                mainlist+=[newSplit]
            if(arg11==["1"] and len(clade)>=2 and mainlist.count([newSplit])==0):
                mainlist+=[newSplit]
        mainlist=str(mainlist)
# List clades of other trees
        generalCounter=0
        with open(t.positions,"r") as positions:
            for lineno,linestr in enumerate(positions,1):
                if lineno==(t.n):
                    pass
                elif(t.constrictTreeList.count(lineno)):
                    generalCounter+=1
                    if((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                       print("-Comparing trees : Tree No. %d with tree No. %d (%d of %d)."%(t.n,lineno,generalCounter,len(t.constrictTreeList)-1))
                    elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                        print("-Comparing trees : Tree No. %d with tree No. %d (%d of %d)."%(t.n,lineno,generalCounter,len(t.constrictTreeList)))
                    linestr=re.sub(r"[\[\]()\n ]","",linestr)
                    stropenbrackets,strclosebrackets=linestr.split("\t")
                    listopenbrackets=[int(n) for n in stropenbrackets.split(",")]
                    listclosebrackets=[int(n) for n in strclosebrackets.split(",")]
# Get tree
                    readTheTrees=open(t.trees,"r")
                    countLines=1
                    tree=""
                    for line in readTheTrees.readlines():
                        if(countLines==lineno):
                            tree=line
                            break
                        countLines+=1
                    readTheTrees.close()
                    templist=[]
                    locallist=[]
                    matchcode=1
                    for item2 in range(len(listopenbrackets)):
                        min=int(listopenbrackets[item2])
                        max=int(listclosebrackets[item2])
                        clade=tree[min:max]
                        clade=re.sub(r"[\[\]\n().;]","",clade)
                        clade=clade.split(","or" ")
                        templist+=[clade]
                    for clade in templist:
                        clade=sorted(clade)
# Clades to splits
                        if arg11==["0"]:
                            outlist=[]
                            for item in t.terminals:
                                if clade.count(item)==0:
                                    outlist+=[item]
                            if(len(outlist)>=2):
                                outlist=sorted(outlist)
                            newSplit=[clade]+[outlist]
                        elif arg11==["1"]:
                            newSplit=[clade]
                        if(arg11==["0"] and len(clade)>=2 and len(outlist)>=2 and locallist.count([newSplit])==0):
                            locallist+=[newSplit]
                        elif(arg11==["1"] and len(clade)>=2 and locallist.count([newSplit])==0):
                            locallist+=[newSplit]
# Compare splits (rooted)
                    if arg11==["0"]:
                        for Split in locallist:
                            if mainlist.count(str(Split))==0:
                                if mainlist.count(str(Split[0]))==0:
                                    matchcode=0
                                    break
                                else:
                                    matchcode=2
                    elif arg11==["1"]:
                        for clade in locallist:
                            if mainlist.count(str(clade))==0:
                                matchcode=0
                                break
                    if matchcode==1:
                        matchlist_rooted+=[lineno]
                    elif matchcode==2:
                        matchlist_unrooted+=[lineno]
# Print result
            if(len(matchlist_rooted)>=1 and t.verbose==1):
                print("--List of matches: %s."%(matchlist_rooted))
                print("--No. of matches = %d."%(len(matchlist_rooted)))
            if(len(matchlist_unrooted)>=1 and t.verbose==1):
                print("--List of matches (if rooted at the same node): %s."%(matchlist_unrooted))
                print("--No. of matches (if rooted at the same node) = %d."%(len(matchlist_unrooted)))
            if(len(matchlist_rooted)==0 and len(matchlist_unrooted)==0 and t.verbose==1):
                print("--No matches!")
            text="Comparing Tree No. %d.\n"%t.n
            if (len(matchlist_rooted)==0 and len(matchlist_unrooted)==0):
                text=text+"No matches!\n"
            else:
                text=text+"Matches\tComment/Cost\tNote\n"
                if len(matchlist_rooted)>=1:
                    for tree in matchlist_rooted:
                        cost=linecache.getline(t.costs,tree)
                        text+="%s\n"%str(cost)
                if len(matchlist_unrooted)>=1:
                    for tree in matchlist_unrooted:
                        cost=linecache.getline(t.costs,tree)
                        text+="%s\tWould match if trees were rooted at the same node\n"%str(cost)
        matches.write(text)
        matches.close()
        if(t.verbose==1):
            print(">The file %s was created."%t.matches)

    def matrix(t):
        if arg11==["0"]:
            print("#MATRIX: Comparing trees Split by Split...")
        elif arg11==["1"]:
            print("#MATRIX: Comparing trees clade by clade...")
        t.matrix="MATRIX_"+t.output+".tsv"
        output=open(t.matrix,"w")
        output.close()
        output=open(t.matrix,"a")
        first_line="# Selected tree: T1. Tree being compared: T2. Number of shared clades or splits: S. Number of unique splits or clades in both trees: U. Local Distance: LD = 1 - (S/U). Number of unique splits or clades in all trees: A. Global Distance (GD) = 1 - (S/A)\n"
        if(arg11==["0"])or(arg11==["1"]):
            if(arg4==["4"]):
                first_line+="T1\tT2\tS\tU\tLD\tA\tGD\n"
            else:
                first_line+="T1\tT2\tS\tU\tLD\n"
        output.write(first_line)
# List clades on the selected tree
        first_positions=linecache.getline(t.positions,t.n)
        first_positions=re.sub(r"[\[\]()\n ]","",first_positions)
        stropenbrackets,strclosebrackets=first_positions.split("\t")
        listopenbrackets=[int(n) for n in stropenbrackets.split(",")]
        listclosebrackets=[int(n) for n in strclosebrackets.split(",")]
# Get tree
        readTheTrees=open(t.trees,"r")
        countLines=1
        tree1=""
        for line in readTheTrees.readlines():
            if(countLines==t.n):
                tree1=line
                break
            countLines+=1
        readTheTrees.close()
        templist=[]
        first_groups=[]
        for item in range(len(listopenbrackets)):
            min=int(listopenbrackets[item])
            max=int(listclosebrackets[item])
            clade=tree1[min:max]
            clade=re.sub(r"[\[\]\n().;]","",clade)
            clade=clade.split(","or" ")
            templist+=[sorted(clade)]
        if arg11==["1"]:
            first_groups=templist # if splits are being compared
        elif arg11==["0"]: # if clades are being compared
# Clades to splits
            for clade in templist:
                outlist=[]
                for item in t.terminals:
                    if clade.count(item)==0:
                        outlist+=[item]
                if(len(outlist)>=2):
                    outlist=sorted(outlist)
                if (len(clade)>=2 and len(outlist)>=2):
                    newSplit=[clade]+[outlist]
                    if first_groups.count(sorted(newSplit))==0:
                        first_groups+=[sorted(newSplit)]
# List clades on the 2nd tree
        list=[]
        count=0
        generalCounter=0
        for i in range(t.count_trees):
            if not (i==0 or i==t.n or t.constrictTreeList.count(i)==0):
                generalCounter+=1
                combined_groups=[]
                combined_groups+=first_groups
                count+=1
                if((t.verbose==1)and(t.constrictTreeList.count(t.n))):
                    print("-Comparing trees : Tree No. %d with tree No. %d (%d of %d)."%(t.n,i,count,len(t.constrictTreeList)-1))
                elif((t.verbose==1)and(t.constrictTreeList.count(t.n)==0)):
                    print("-Comparing trees : Tree No. %d with tree No. %d (%d of %d)."%(t.n,i,count,len(t.constrictTreeList)))
                second_positions=linecache.getline(t.positions,i)
                second_positions=re.sub(r"[\[\]()\n ]","",second_positions)
                stropenbrackets,strclosebrackets=second_positions.split("\t")
                listopenbrackets=[int(n) for n in stropenbrackets.split(",")]
                listclosebrackets=[int(n) for n in strclosebrackets.split(",")]
# Get tree
                readTheTrees=open(t.trees,"r")
                countLines=1
                tree2=""
                for line in readTheTrees.readlines():
                    if(countLines==i):
                        tree2=line
                        break
                    countLines+=1
                readTheTrees.close()
                templist=[]
                second_groups=[]
                for item in range(len(listopenbrackets)):
                    min=int(listopenbrackets[item])
                    max=int(listclosebrackets[item])
                    clade=tree2[min:max]
                    clade=re.sub(r"[\[\]\n().;]","",clade)
                    clade=clade.split(","or" ")
                    if templist.count([sorted(clade)])==0:
                        templist+=[sorted(clade)]
                if arg11==["1"]:
                    second_groups=templist
                elif arg11==["0"]:
# Clades to splits
                    for clade in templist:
                        outlist=[]
                        for item in t.terminals:
                            if clade.count(item)==0:
                                outlist+=[item]
                        if(len(outlist)>=2):
                            outlist=sorted(outlist)
                        if (len(clade)>=2 and len(outlist)>=2):
                            newSplit=[clade]+[outlist]
                            second_groups+=[sorted(newSplit)]
# List all splits in both trees without repetitions
                countsg=0
                for group in second_groups:
                    if combined_groups.count(group)==0:
                        combined_groups+=[group]
                    if first_groups.count(group)>=1:
                        countsg+=1
# Print results and close
                cb=len(combined_groups)*1.00
                sb=countsg*1.00
                ld=float(1.00-(sb/cb))
                if arg4==["4"]:
                    gd=float(1.00-(sb/t.ngroups))
                    new_line=str(t.n)+"\t"+str(i)+"\t"+str(sb)+"\t"+str(cb)+"\t"+str(ld)+"\t"+str(t.ngroups)+"\t"+str(gd)+"\n"
                else:
                    new_line=str(t.n)+"\t"+str(i)+"\t"+str(sb)+"\t"+str(cb)+"\t"+str(ld)+"\n"
                output.write(new_line)
        output.close()
        if(t.verbose==1):
            print(">The file %s was created"%t.matrix)

###SENSITIVITY ANALYSIS###

    def main_sa(t): # Executes this function if no clades nor trees were specified
# Execute necessary functions (if not done before)
        if not (arg4==["1"] or arg4==["2"] or arg4==["3"] or arg4==["4"]):
            hennig.list_positions()
        if not (arg4==["2"] or arg4==["4"]):
            if arg11==["0"]:
                hennig.list_splits()
            elif arg11==["1"]:
                hennig.list_clades()
# Set trees to be examined
        t.trees2look=[]
        if t.sa_pools=="n":
            for integer in range(1,t.count_trees):
                t.trees2look+=[str(integer)]
            t.trees2look=[t.trees2look]
        else:
            t.trees2look=t.sa_pools
            unique_trees=[]
            repeat=0
            while repeat==0:
                for pool in t.sa_pools:
                    if repeat==0:
                        for tree in pool:
                            if not unique_trees.count(tree):
                                print(">WARNING: there are repeated trees in the pools.")
                                repeat+=1
                                break
                    else:
                        break
        if(listOfClades[0]=="empty"):
            hennig.all_in_tree()
        else:
            hennig.selectedByUser()

    def all_in_tree(t): # This function is executed when user wants SA but did not give clades nor trees
        print("#Sensitivity analysis...")
        if arg11==["0"]:
            print(">Start searching for all splits in Tree No. %d..."%t.n)
        elif arg11==["1"]:
            print(">Start searching for all clades in Tree No. %d..."%t.n)
        selected_tree=linecache.getline(t.groups,t.n)
        if arg11==["0"]:
            selected_tree=re.compile("\[\[.*?\]\]").findall(selected_tree)
        elif arg11==["1"]:
            selected_tree=re.compile("\['.*?'\]").findall(selected_tree)
        count_group=0
        t.sa_results=[]
        for group in selected_tree:
            t.current_group=group
            pool_results=[]
            count_group+=1
            if(arg11==["0"] and t.verbose==1):
                print("-Examining tree : Split %d of %d"%(count_group,len(selected_tree)))
            elif(arg11==["1"] and t.verbose==1):
                print("-Examining tree : Clade %d of %d"%(count_group,len(selected_tree)))
            count_pools=0
            for pool in t.trees2look:
                count_pools+=1
                count_wins=0
                count_fails=0
                for tree in pool:
                    current_tree=linecache.getline(t.groups,int(tree))
                    if current_tree.count(group):
                        count_wins+=1
                    else:
                        count_fails+=1
                pool_results+=[[count_wins]+[count_fails]]
            t.sa_results+=[[group]+pool_results]
        t.selected_groups=selected_tree
        hennig.txt_sa()
        if not t.svg=="n":
            try:
                import svgwrite
            except ImportError:
                print(">ERROR: Could not find package svgwrite and will not print Navajo rugs.")
                print("[Package information: <https://pypi.python.org/pypi/svgwrite/>]")
            else:
                hennig.svg_sa()
# Id clades on the selected tree...
        hennig.recon_groups()
        hennig.id_groups()

    def selectedByUser(t):
        print("#Sensitivity analysis...")
        if arg11==["0"]:
            print(">Start searching for selected splits in Tree No. %d..."%t.n)
# Transform clades into splits...
            listOfSplits=[]
            for clade in t.listOfClades:
                if(len(clade)>1):
                    tempList=[]
                    for terminal in t.terminals:
                        if(clade.count(terminal)==0):
                            tempList+=[terminal]
                            tempList=sorted(tempList)
                if((len(clade)>1)and(len(tempList)>1)):
                    tempList=[clade]+[tempList]
                    tempList=sorted(tempList)
                    listOfSplits+=[tempList]
            tempListOfGroups=sorted(listOfSplits)
        elif arg11==["1"]:
            print(">Start searching for selected clades in Tree No. %d..."%t.n)
            tempListOfGroups=[]
            for clade in t.listOfClades:
                if((len(clade)>1)and(tempListOfGroups.count(clade)==0)):
                    tempListOfGroups.append(clade)
        listOfGroups=[]
        for group in tempListOfGroups:
            if group not in listOfGroups:
                listOfGroups.append(group)
        count_group=0
        t.sa_results=[]
        for group in listOfGroups:
            group=str(group)
            t.current_group=group
            pool_results=[]
            count_group+=1
            if(arg11==["0"] and t.verbose==1):
                print("-Examining tree : Split %d of %d"%(count_group,len(listOfGroups)))
            elif(arg11==["1"] and t.verbose==1):
                print("-Examining tree : Clade %d of %d"%(count_group,len(listOfGroups)))
            count_pools=0
            for pool in t.trees2look:
                count_pools+=1
                count_wins=0
                count_fails=0
                for tree in pool:
                    current_tree=linecache.getline(t.groups,int(tree))
                    if current_tree.count(group):
                        count_wins+=1
                    else:
                        count_fails+=1
                pool_results+=[[count_wins]+[count_fails]]
            t.sa_results+=[[group]+pool_results]
        hennig.txt_sa()
        if not t.svg=="n":
            try:
                import svgwrite
            except ImportError:
                print(">ERROR: Could not find package svgwrite and will not print Navajo rugs.")
                print("[Package information: <https://pypi.python.org/pypi/svgwrite/>]")
            else:
                hennig.svg_sa()

    def txt_sa(t):
        print("#Printing results of the sensitivity analysis (TSV file)...")
        t.TSVfile="SA_"+t.output+".tsv"
        output=open(t.TSVfile,"w")
        first_line="Line No.\tPartial\tTotal\tPrevalence\tClades\n\t(Wins:Fails)\t(Hits:Number of Trees)\t(%)\n"
        text=""
        count_groups=0
        for group in t.sa_results:
            count_groups+=1
            if(t.verbose==1):
                print("-Printing results : %d of %d."%(count_groups,len(t.sa_results)))
            total_wins=0
            total_fails=0
            hits=""
            for counter in range(1,len(group)):
                partial_result=group[counter]
                hits+=str(partial_result)+"; "
                total_wins+=partial_result[0]
                total_fails+=partial_result[1]
            hits=re.sub("[\[\]]","",re.sub(", ",":",hits))
            total=str(total_wins)+":"+str(total_wins+total_fails)
            prevalence=(total_wins*100.00/(total_wins+total_fails))
            text+="%d\t%s\t%s\t%s\t%s\n"%(count_groups,hits[:len(hits)-2],total,prevalence,re.sub(r"[\[\]]","",re.sub("(\], \[)"," : ",group[0])))
        output.write(first_line+text)
        output.close()
        if(t.verbose==1):
            print(">Done! Sensitivity analysis printed into %s."%t.TSVfile)

## print sa result as tree part 1
    def recon_groups(t):
# Creates a new empty list
        t.groups2label=[]
# Get brackets positions
        brackets=linecache.getline(t.positions,t.n)
        positions=re.compile("\[(.*?)\]").findall(brackets)
        listopenbrackets=re.compile("(\d+)\s*,*\s*").findall(positions[0])
        listclosebrackets=re.compile("(\d+)\s*,*\s*").findall(positions[1])
# Get selected tree
        readTheTrees=open(t.trees,"r")
        countLines=1
        tree=""
        for line in readTheTrees.readlines():
            if(countLines==t.n):
                tree=line
                break
            countLines+=1
        readTheTrees.close()
# Get clades from selected tree
        for item in range(len(listopenbrackets)):
            min=int(listopenbrackets[item])
            max=int(listclosebrackets[item])
            clade=tree[min:max]
            clade=re.sub(r"[\[\]\n().;]","",clade)
            clade=clade.split(","or" ")
            clade=sorted(clade)
# Creating global list of clades
            if(t.compare_opt=="1" and len(clade)>=2):
                t.groups2label+=[[min,max]]
            elif(t.compare_opt=="0"):
                outlist=[]
                for item in t.terminals:
                    if clade.count(item)==0:
                        outlist+=[item]
                    if (len(clade)>=2 and len(outlist)>=2 and t.groups2label.count([min,max])==0):
                        t.groups2label+=[[min,max]]

## print sa result as tree part 2
    def id_groups(t):
        t.labeledTree="LABELED_"+t.output+".tre"
        output=open(t.labeledTree,"w")
        readTheTrees=open(t.trees,"r")
        countLines=1
        selectedTree=""
        for line in readTheTrees.readlines():
            if(countLines==t.n):
                selectedTree=line
                break
            countLines+=1
        readTheTrees.close()
        countGroups=1
        closeBracketsAndCounter=[]
        for pair in t.groups2label:
            CSVfile=linecache.getline(t.TSVfile,countGroups+2)
            cells=CSVfile.split("\t")
            closeBracketsAndCounter+=[[pair[1],countGroups,cells[3]]]
            countGroups+=1
        closeBracketsAndCounter=sorted(closeBracketsAndCounter,reverse=True)
        for item in closeBracketsAndCounter:
            selectedTree="%s%04d:%s%s"%(selectedTree[:item[0]+1],item[1],item[2],selectedTree[item[0]+1:])
        output.write(selectedTree)
        output.close()

    def svg_sa(t):
        import svgwrite
        block_size=100
        #text_correction=-15
        print("#Printing results of the sensitivity analysis (SVG files)...")
        count_groups=0
        for group in t.sa_results:
            count_groups+=1
            if(t.verbose==1):
                print("-Printing images : %d of %d."%(count_groups,len(t.sa_results)))
            total_wins=[]
            total_fails=[]
            prevalence=[]
            for counter in range(1,len(group)):
                partial_result=group[counter]
                total_wins+=[partial_result[0]]
                total_fails+=[partial_result[1]]
                prevalence+=[(int(partial_result[0])*100.00/(int(partial_result[0])+int(partial_result[1])))]
            count=0
            coord=math.ceil(math.sqrt(len(prevalence)))
            svg_filename="RUG_%04d_%s.svg"%(count_groups,t.output)
            svg_document=svgwrite.Drawing(filename=svg_filename,
                size=(str(int(block_size)*int(coord))+"px",
                str(int(block_size)*int(coord))+"px"))
            for y in range(int(coord)):
                for x in range(int(coord)):
                    if count==len(prevalence):
                        pass
                    else:
                        color_var=int(prevalence[count])
                        if color_var==0:
                            R=G=B=255

# Red
                        elif t.color.lower()=="red":
                            if color_var==100:
                                R=120
                                G=B=0
                            else:
                                R=120+(100-color_var)
                                G=B=(100-color_var)
# Orange
                        elif t.color.lower()=="orange":
                            if color_var==100:
                                R=255
                                G=140
                                B=0
                            else:
                                R=255
                                G=240-color_var
                                B=int(color_var/2)
# Yellow
                        elif t.color.lower()=="yellow":
                            R=G=255
                            if color_var==100:
                                B=0
                            else:
                                B=int(2*(100-color_var))
# Green
                        elif t.color.lower()=="green":
                            if color_var==100:
                                R=B=0
                                G=120
                            else:
                                R=B=(100-color_var)
                                G=120+(100-color_var)
# Blue
                        elif t.color.lower()=="blue":
                            if color_var==100:
                                R=G=0
                                B=120
                            else:
                                R=G=(100-color_var)
                                B=120+(100-color_var)
# Indigo
                        elif t.color.lower()=="indigo":
                            R=75
                            G=2*(100-color_var)
                            B=120
# Violet
                        elif t.color.lower()=="violet":
                            R=148
                            G=2*(100-color_var)
                            B=211
# Black & white
                        elif t.color.lower()=="n":
                            R=G=B=0
# Gray shades
                        else:
                            R=G=B=255*(100-color_var)/100
# Code SVG
                        svg_document.add(svg_document.rect(insert=(x*int(block_size),y*int(block_size)),
                            size=(str(block_size)+"px",str(block_size)+"px"),
                            stroke_width="2",stroke=t.stroke,fill="rgb(%d,%d,%d)" %(R,G,B)))
                        if t.text=="p":
                            if t.color.lower()=="yellow":
                                lcolor=t.stroke
                            elif int(prevalence[count])>=50:
                                lcolor="white"
                            else:
                                lcolor=t.stroke
                            x_axis=((x*int(block_size))+int(block_size)/2)#+int(text_correction)
                            y_axis=(y*int(block_size))+int(block_size)/2
                            svg_document.add(svg_document.text(str(round(float(prevalence[count]),1))+"%",
                                insert=(x_axis,y_axis+args.text_position),fill=lcolor,
                                style="font-size:%dpx;font-family:Arial;font-weight:%s;text-anchor:middle"%(args.font_size,args.font_weight)))
                        elif t.text=="r":
                            ratio=str(total_wins[count])+" : "+str(total_wins[count]+total_fails[count])
                            if t.color.lower()=="yellow":
                                lcolor=t.stroke
                            elif int(prevalence[count])>=50:
                                lcolor="white"
                            else:
                                lcolor=t.stroke
                            x_axis=((x*int(block_size))+int(block_size)/2)#+int(text_correction)
                            y_axis=(y*int(block_size))+int(block_size)/2
                            svg_document.add(svg_document.text(ratio,
                                insert=(x_axis,y_axis+args.text_position),fill=lcolor,
                                style="font-size:%dpx;font-family:Arial;font-weight:%s;text-anchor:middle"%(args.font_size,args.font_weight)))
                        count+=1
# Print SVG and save
            if(t.verbose==1):
                print(svg_document.tostring())
            svg_document.save()
# Print sensitivity map
        count=0
        svg_filename="RUG_map_%s.svg"%t.output
        svg_document=svgwrite.Drawing(filename=svg_filename,
            size=(str(int(block_size)*int(coord))+"px",
            str(int(block_size)*int(coord))+"px"))
        for y in range(int(coord)):
            for x in range(int(coord)):
                if count==len(prevalence):
                    pass
                else:
                    if(count+1>len(t.caption)):
                        break
                    else:
                        caption=t.caption[count]
                    svg_document.add(svg_document.rect(insert=(x*int(block_size),y*int(block_size)),
                        size=(str(block_size)+"px",str(block_size)+"px"),
                        stroke_width="2",stroke=t.stroke,fill="rgb(255,255,255)"))
                    lcolor=t.stroke
                    x_axis=((x*int(block_size))+int(block_size)/2)#+int(text_correction)
                    y_axis=(y*int(block_size))+int(block_size)/2
                    svg_document.add(svg_document.text(caption,
                        insert=(x_axis,y_axis+args.text_position),
                        fill=lcolor,
                        style="font-size:%dpx;font-family:Arial;font-weight:%s;text-anchor:middle"%(args.font_size,args.font_weight)))
                    count+=1
            svg_document.save()

    def close(t):
        if(t.verbose==0):
            print("#Cleaning up...")
            import glob,os
            prefixes=["BRACKETS_*.txt","COMMENTS_*.txt","SPLITS_*.txt","CLADES_*.txt","PRUNED_*.trees","MSDIST_*.txt"]
            for prefix in prefixes:
                files2remove=glob.glob(prefix)
                for file in files2remove:
                    try:
                        os.remove(file)
                    except:
                        print("--Could not find/remove %s"%(prefix))
            print(">Done!")
        exit()


###PARSING CONFIGURATION FILE###
try:
    with open (args.configuration,"r") as config_file:
        print("##Parsing configuration file (%s)..."%(args.configuration))
        config=""
        gaveListOfFiles=0 # If gaveListofFiles remains 0 do FILE and POOLS operations
        treeCount=1
        verbose=0
        for line in config_file.readlines():
            stripedLine=line.strip()
            if not (stripedLine.startswith("#") or stripedLine.startswith("%")):
                if stripedLine.rstrip():
                    stripedLine=re.sub(r"\s*#.*|\s*%.*","",stripedLine)
                    config+=stripedLine+"\n"
        selectedText=re.compile("(>.*=)").findall(config)
        selectedText+=re.compile("(<\s*begin\s+\w+)",re.IGNORECASE).findall(config)
        selectedText+=re.compile("(end\s+\w+\s*>)",re.IGNORECASE).findall(config)
        for text in selectedText:
            config=re.sub(text,text.lower(),config)
        verboseCommand=re.compile("(>\s*verbose)",re.IGNORECASE).findall(config)
        if(verboseCommand)or(args.verbose):
            verbose=1
        projectId=re.compile(">*id *= *(\S*)\W*").findall(config)
        if not projectId:
            projectId=["output"]
            print(">No Id. Default is output.")
        elif(verbose==1):
            print(">id=%s"%projectId[0])
        arg5=re.compile(">*n *= *(\d*)\W*").findall(config)
        nTag=re.compile(">*n *=.*\[(.*)\]").findall(config)
        if((not arg5)or(arg5==[""])):
            arg5=["1"]
            if(verbose==1):
                print(">No tree selected for comparison. The default is Tree No. 1.")
        if((not nTag)or(nTag==[""])):
            nTag=["NoFileWasAttachedToTheSelectedTree"]
        if(verbose==1):
            print(">n=%s[%s]"%(arg5[0],nTag[0]))
        listOfFiles=re.compile("<\s*begin\s*files\s*(.*)\s*end\s*files\s*>",re.DOTALL).findall(config)
        msdistInConfig=re.compile("(>\s*msdist)",re.IGNORECASE).findall(config)
        if(msdistInConfig):
            msdistInConfig=re.compile(">\s*msdist\s*=\s*([^<>=\s]+)\W*",re.IGNORECASE).findall(config)
            if(msdistInConfig):
                msdistInConfig=msdistInConfig[0]
            else:
                msdistInConfig="Msdist/bin"
        else:
            msdistInConfig="empty"
        caption=[]
        if not listOfFiles:
            listOfFiles=["n"]
            captions=["empty"]
        else:
            print("#Pruning trees...")
            if(verbose==1):
                print("<begin files")
            gaveListOfFiles=1
            listOfFiles=re.sub("\s","",listOfFiles[0])
            listOfFiles=listOfFiles.split(";")
#             listOfFiles=filter(None,listOfFiles)
            listOfFiles=[i for i in listOfFiles if i != '']
            fileEntryOrder=[]
            captions=[]
            print("NAILED")
            for fileAndLabel in listOfFiles:
                fileAndLabel=re.split(r"\[(.*)\]",fileAndLabel)
#                 fileAndLabel=filter(None,fileAndLabel)
                fileAndLabel=[i for i in fileAndLabel if i != '']
                fileEntryOrder+=[fileAndLabel[0]]
                if(len(fileAndLabel)==2):
                    captions+=[fileAndLabel[1]]
                else:
                    thisLabel=re.sub(r"\..*","",fileAndLabel[0])
                    thisLabel=re.sub(r".*\/","",thisLabel)
                    thisLabel=re.sub(r".*\\\\","",thisLabel)
                    captions+=[thisLabel]
            concatenatedTreeFile="TREES_"+projectId[0]+".tre"
            output=open(concatenatedTreeFile,"w")
            output.close()
            costsFile="COMMENTS_"+projectId[0]+".txt"
            output=open(costsFile,"w")
            output.close()
            currentPool=""
            pools=[]
            for inputTreeFile in fileEntryOrder:
                if(verbose==1):
                    print("\t%s;"%inputTreeFile)
                with open (inputTreeFile,"r") as input:
                    fileCount=0 # track tree number per file
                    currentPool=str(treeCount)+"-"
                    newCostsLines=""
                    trees=input.read()
                    trees=re.sub(r"[\s*]","",trees)
                    trees=re.sub(r":[^(^)^,^;^\[^\]]+","",trees)
                    trees=trees.replace(");",")[No_Comment];")
                    trees=re.sub(";",r";\n",trees)
                    allComments=re.compile("\[(\S+)").findall(trees)
                    currentTree=1
                    for comments in allComments:
                        fileCount+=1 # +1 tree number in this file
                        if((nTag[0]==inputTreeFile)and(int(arg5[0])==currentTree)):
                            arg5=[str(treeCount)]
                        newCostsLines+="Tree No. "+str(treeCount)+":\t"+re.sub(r"];","",str(comments))+"\t(tree no. "+str(fileCount)+" in file "+inputTreeFile+")"+"\n"
                        treeCount+=1
                        currentTree+=1
                    currentPool+=str(treeCount-1)
                    pools+=[currentPool]
                    output=open(costsFile,"a")
                    output.write(newCostsLines)
                    output.close()
                    trees=re.sub("\[(\S+)","",trees)
                    trees=re.sub("\n",";\n",trees)
                    output=open(concatenatedTreeFile,"a")
                    output.write(trees)
                    output.close()
                    input.close()
            if(verbose==1):
                print("end files>")
            if(verbose==1):
                print("#...A total of %d trees were given.\n#...File %s was created."%(treeCount-1,concatenatedTreeFile))
        try:
            if concatenatedTreeFile:
                treeFile=[concatenatedTreeFile]
        except NameError:
            print(">Error: no input files were given. Add tree files to the configuration file between <begin files and end files>.")
            exit()
        poolData_1=re.compile("< *begin *pools\s*(.*)\s*end *pools *>",re.DOTALL).findall(config)
        if not poolData_1:
            poolData="n"
        else:
            poolData_2=re.sub("\s","",poolData_1[0])
            poolData_3=poolData_2.split(";")
            poolData_3=filter(None,poolData_3)
            countPools=1
            captions=[]
            pools=[]
            for poolLine in poolData_3:
                tempVar=re.compile("(.*)\[").findall(poolLine)
                if tempVar:
                    pools+=tempVar
                    captions+=re.compile("\[(.*)\]").findall(poolLine)
                else:
                    pools+=[poolLine]
                    captions+=[str(countPools)]
                countPools+=1
            poolData=[]
            for i1 in pools:
                templist=[]
                if i1.count(","):
                    i2=i1.split(",")
                else:
                    i2=[i1]
                for i3 in i2:
                    if i3.count("-"):
                        i4=i3.split("-")
                        for i5 in range(int(i4[0]), int(i4[1])+1):
                            if not templist.count([i5]):
                                templist+=[str(i5)]
                    else:
                        if not templist.count([i3]):
                            templist+=[i3]
                if not poolData.count(templist):
                    poolData+=[templist]
        if((gaveListOfFiles==1)and(poolData=="n")):
            poolData=[]
            for i1 in pools:
                tempList=[]
                i2=i1.split("-")
                for i3 in range(int(i2[0]), int(i2[1])+1):
                    if not tempList.count([i3]):
                        tempList+=[str(i3)]
                if not poolData.count(tempList):
                    poolData+=[tempList]
        if not poolData:
            poolData="n"
        listOfClades=re.compile("< *begin *clades\s*(.*)\s*end *clades *>",re.DOTALL).findall(config)
        if not listOfClades:
            listOfClades=[]
        else:
            listOfClades=re.sub("[\s*]|[\(*]|[\)*]|\[.*?\]|:[^(^)^,^;^\[^\]]+","",listOfClades[0]) # Remove labels
            listOfClades=re.sub("[\(*]|[\)*]","",listOfClades)
            listOfClades=listOfClades.split(";")
            listOfClades=filter(None,listOfClades)
            tempList=listOfClades
            listOfClades=[]
            for clade in tempList:
                listOfTerminals=clade.split(",")
                listOfTerminals=filter(None,listOfTerminals)
                listOfTerminals=sorted(listOfTerminals)
                if(listOfClades.count(listOfTerminals)==0):
                    listOfClades+=[listOfTerminals]
            tempList=[]
        listOfTrees=re.compile("< *begin *trees\s*(.*)\s*end *trees *>",re.DOTALL).findall(config)
        if not listOfTrees:
            listOfTrees=[]
        else:
            listOfTrees=re.sub("\s","",listOfTrees[0])
            listOfTrees=listOfTrees.split(";")
            listOfTrees=filter(None,listOfTrees)
            for tree in listOfTrees:
                tree=re.sub("[\s*]||\[.*?\]","",tree) # Remove Unicode white spaces
                tree=re.sub(":[^(^)^,^;^\[^\]]+","",tree) # Remove Split labels
                countOpenBrackets=0
                openBrackets=[]
                closeBrackets=[]
                for character1 in tree:
                    if character1=="(":
                        if(openBrackets.count([countOpenBrackets])==0):
                            openBrackets+=[countOpenBrackets]
                        countCloseBrackets=countOpenBrackets+1
                        countPairs=1
                        for character2 in tree[countOpenBrackets+1:]:
                            if character2=="(":
                                countPairs+=1
                            elif character2==")":
                                countPairs-=1
                                if countPairs==0:
                                    if(closeBrackets.count([countCloseBrackets])==0):
                                        closeBrackets+=[countCloseBrackets]
                                    break
                            countCloseBrackets+=1
                    countOpenBrackets+=1
                for pair in range(len(openBrackets)):
                    try:
                        currentClade=tree[openBrackets[pair]:closeBrackets[pair]]
                    except IndexError:
                        print(">ERROR: Please check the trees provided in the configuration file (possible missing brackets).")
                        break
                    else:
                        currentClade=re.sub("\s|\(|\)","",currentClade)
                        listOfTerminals=currentClade.split(",")
                        listOfTerminals=filter(None,listOfTerminals)
                        listOfTerminals=sorted(listOfTerminals)
                        if(listOfClades.count(listOfTerminals)==0):
                            listOfClades+=[listOfTerminals]
        if(listOfClades==[]):
            listOfClades=["empty"]
        arg2=re.compile(">*root *= *(\S*)\W*").findall(config)
        if not (arg2):
            arg2=["n"]
        elif arg2[0]=="N":
            arg2=["n"]
        arg4=re.compile(">*opt *= *(\S*)\W*").findall(config)
        arg4=[x.lower() for x in arg4]
        if not arg2:
            arg2=["n"]
            if(verbose==1):
                print(">No root. Trees will not be re-rooted.")
        elif(verbose==1):
            print(">root=%s"%arg2[0])
        if not arg4:
            arg4=["n"]
            print(">No option was given for tree comparison.")
        elif(verbose==1):
            print(">opt=%s"%arg4[0])
        arg6=re.compile(">*sa *= *(\S*)\W*").findall(config)
        arg6=[x.lower() for x in arg6]
        if(not arg6):
            arg6=["no"]
        arg7=[""]
        if(arg6[0][:1]=="y"):
            arg6=["yes"]
            if(verbose==1):
                print(">sa=%s"%arg6[0])
            arg7=re.compile(">*rug *= *(\S*)\W*").findall(config)
            arg7=[x.lower() for x in arg7]
        else:
            arg6=["n"]
            if(verbose==1):
                print(">Sensitivity analysis disabled.")
        if arg7==[""]:
            arg7=["n"]
            if(verbose==1):
                print(">Navajo rugs disabled.")
        elif(arg7 and verbose==1):
            print(">rug=%s"%arg7[0])
        if not poolData:
            poolData=["n"]
        elif(verbose==1):
            print("<begin pools")
            poolString=""
            for pool in poolData:
                for tree in pool:
                    poolString+=tree+","
                poolString+=";"
            poolString+="\n"
            poolString=re.sub(",;",";",poolString)
            poolString=re.sub(";\n","\nend pools>",poolString)
            print("   %s"%poolString)
        arg11=re.compile(">*compare *= *(\S*)\W*").findall(config)
        if not arg11:
            arg11=["0"]
        elif not (arg11[0]=="0" or arg11[0]=="1"):
            arg11=["0"]
            if(verbose==1):
                print(">No comparison option given. YBYRA will compare trees using splits.")
        elif(verbose==1):
            print(">compare=%s"%(arg11[0]))
        arg12=re.compile(">*stroke *= *(\S*)\W*").findall(config)
        arg12=[x.lower() for x in arg12]
        if arg12==[""]:
            arg12=["black"]
        elif not arg12:
            arg12=["black"]
        elif(verbose==1):
            print(">stroke=%s"%(arg12[0]))
        arg13=re.compile(">*color *= *(\S*)\W*").findall(config)
        arg13=[x.lower() for x in arg13]
        if arg13==[""]:
            arg13=["black"]
        elif not arg13:
            arg13=["black"]
        elif(verbose==1):
            print(">color=%s"%(arg13[0]))
        arg14=re.compile(">*text *= *(\S*)\W*").findall(config)
        arg14=[x.lower() for x in arg14]
        if arg14==[""]:
            arg14=["p"]
        elif(not arg14):
            arg14=["p"]
        elif(verbose==1):
            print(">text=%s"%(arg14[0]))
except:
    print(">ERROR while reading file %s"%(args.configuration))
    exit()

###EXECUTE FUNCTIONS###
if(treeFile and arg2 and projectId and arg4 and arg5 and arg6 and arg7 and poolData and arg11 and arg12 and arg13 and arg14 and captions and treeCount and listOfClades and msdistInConfig):
    print("##Executing functions...")
    ARGS=[poolData]
    hennig=Tree(treeFile[0],arg2[0],projectId[0],arg5[0],arg6[0],arg7[0],ARGS[0],arg11[0],arg12[0],arg13[0],arg14[0],verbose,captions,treeCount,listOfClades,msdistInConfig)
    if(args.wildcards):
        hennig.msdist_results()
        hennig.close()
        exit()
    if(gaveListOfFiles==0):
        hennig.lines()
    hennig.test_brackets()
    hennig.test_terminals()
    if not arg2==["n"]:
        hennig.roots()
    if(msdistInConfig!="empty"):
        try:
            from Bio import Phylo
        except ImportError:
            print(">ERROR: Could not load Biopyhton module. Will not be able to proceed.\n[Module information: <http://biopython.org/wiki/Main_Page>]")
            exit()
        try:
            import subprocess
        except ImportError:
            print(">ERROR: Could not load subprocess. Will not be able to proceed.")
            exit()
        try:
            import os
        except ImportError:
            print(">ERROR: Could not load os. Will not be able to proceed.")
        if(os.path.isfile("%s/MSdist.jar"%(msdistInConfig))):
            hennig.msdist_prune()
            hennig.msdist_results()
            hennig.close()
        else:
            print(">ERROR: Could not find MSdist.jar in %s. Check configuration file >msdist value."%(msdistInConfig))
        exit()
    if(args.msdist):
        print("##MSdist 0.5 (by Damian Bogdanowicz; available at http://www.kaims.pl/~dambo/msdist)")
        try:
            from Bio import Phylo
        except ImportError:
            print(">ERROR: Could not load Biopyhton module. Will not be able to proceed.\n[Module information: <http://biopython.org/wiki/Main_Page>]")
        else:
            hennig.msdist_prune()
        exit()
    elif arg4==["1"]:
        hennig.list_positions()
        hennig.match()
    elif arg4==["2"]:
        hennig.list_positions()
        if arg11==["0"]:
            hennig.list_splits()
        elif arg11==["1"]:
            hennig.list_clades()
    elif arg4==["3"]:
        hennig.list_positions()
        hennig.matrix()
    elif arg4==["4"]:
        hennig.list_positions()
        if arg11==["0"]:
            hennig.list_splits()
        elif arg11==["1"]:
            hennig.list_clades()
        hennig.matrix()
    if arg6==["yes"]:
        hennig.main_sa()
    hennig.close()

exit()
