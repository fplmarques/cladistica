#!/usr/bin/python3
# -*- coding: utf-8 -*-
###################################################################
#   This script is used to explore the concept of tree space      #
#   in phylogenetic inference.                                    #
#                                                                 #
#   Usage: python3 tree_space.py                                  #
#                                                                 #
#                      FPL Marques & chatGPT  Feb. 2023           #
#                                                                 #
###################################################################

##
# LIBRARIES
##

import os
import numpy as np
import matplotlib.pyplot as plt
#from scipy.interpolate import interp2d  #DeprecationWarning
from scipy.interpolate import LinearNDInterpolator
from mpl_toolkits.mplot3d import Axes3D
from random import randint
import math

##
# FUNCTIONS
##

def generate_surface_plot_01(x,y,z):
  """
  This function builds the 3D surface plots based on a grid representing all
  binary trees possible given the number of terminals for option 1
  @param x: x coordanate for the tree
  @param y: y coordanate for the tree
  @param z: scores for each tree
  @return: a 3D plot
  """
  x, y = np.meshgrid(x, y)
  z = np.array(z)
  z = np.array(z).reshape(len(y), len(x))
  z_max = np.max(z)
  z_min = np.min(z)
  if z_max == z_min == 1:
    z_max = 2
  colors = (z - z_min) / (z_max - z_min)
  colors = np.asarray(colors)
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.plot_surface(x, y, z, facecolors=plt.cm.viridis(colors))
  ax.set_title(f'Tree space for {ntrees} trees.')
  ax.set_xlabel('tree position in x')
  ax.set_ylabel('tree position in y')
  ax.set_zlabel('Tree scores')
  print(z)
  plt.show()


def generate_surface_plot_02(x,y,z):
  """
  This function builds the 3D surface plots based on a grid representing all
  binary trees possible given the number of terminals for options 2 and 3
  @param x: x coordanate for the tree
  @param y: y coordanate for the tree
  @param z: scores for each tree
  @return: a 3D plot
  """
  z = np.array(z).reshape(len(y), len(x))
  rows, cols = z.shape

  x = np.linspace(0, cols-1, cols)
  y = np.linspace(0, rows-1, rows)
  X, Y = np.meshgrid(x, y)
  points = np.array([X.flatten(), Y.flatten()]).T
  values = z.flatten()

  f = LinearNDInterpolator(points, values)

  x2 = np.linspace(0, cols-1, 30)
  y2 = np.linspace(0, rows-1, 60)
  X2, Y2 = np.meshgrid(x2, y2)
  points2 = np.array([X2.flatten(), Y2.flatten()]).T
  z2 = f(points2)
  z2 = np.reshape(z2, (60, 30))

  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  ax.plot_surface(X2, Y2, z2, cmap='viridis')
  ax.set_title(f'Tree space for {ntrees} trees.')
  ax.set_xlabel('tree position in x')
  ax.set_ylabel('tree position in y')
  ax.set_zlabel('Tree scores')
  ax.set_zlim(np.min(z2), np.max(z2))
  plt.show()


def histogram(scores):
  """
  This function plots a histogram for tree scores.
  @param scores:
  @return: Histogram
  """
  scores = np.array(scores)
  fig, ax = plt.subplots(1, 1)
  ax.hist(scores)
  ax.set_title(f'Scores (number of transformations) for {ntrees} trees')
  ax.set_xlabel('Tree scores')
  ax.set_ylabel('Frequency')
  plt.show()

def axes_list(n_terminals):
  """
  This function calculates the number of all possible binary trees given the number of terminals
  and create tree lists: x and y are coordenates for the trees and z is a list assuming that all
  possible trees have score = 1.
  @param n_terminals: number
  @return: tree lists, which without modification can be passed to generate_surface_plot(x,y,z)
  """
  global ntrees
  ntrees = int(math.factorial(2*n_terminals-4)/(math.factorial(n_terminals-2)*(2**(n_terminals-2))))
  grid_dimension = math.ceil(math.sqrt(ntrees))
  x = []
  y = []
  z = []
  for i in range(1,grid_dimension+1):
    x.append(i)
    y.append(i)
  for score in range(0,int(ntrees)):
    z.append(1)
  while len(z) < len(x)*len(y):  # required to match grid size for 3D plot
    z.append(max(z))
  return [x,y,z]


def tnt_random(n_characters,n_terminals):
  """
  This function executes three tasks based on provided numbers of terminals and
  characters desired by the user:
    1. creates a dictionary (matrix) for terminals and a list of binary random character states;
    2. writes a TNT formated file with the matrix and commands to enumerate all trees and compute the scores;
    3. execute TNT.
  @param n_characters:
  @param n_terminals:
  @return: the execution of TNT renders an output file containing tree scores (tnt.out).
  """
  matrix = {}
  for t in range(0,n_terminals):
    matrix[f'Terminal_{t}'] = []
    for c in range(0,n_characters):
      matrix[f'Terminal_{t}'].append(randint(0,1))
  with open("random.tnt", "w") as out_file:
    out_file.write(f'mxram 1024\n')
    out_file.write(f'xread\n')
    out_file.write(f'{n_characters} {n_terminals}\n')
    for k, v in matrix.items():
      out_file.write(f"{k} {''.join(map(str,v))}\n")
    out_file.write(f';\n')
    out_file.write(f'hold 100000;\n')
    out_file.write(f'cc] .;\n')  #inactivates characters
    out_file.write(f'collapse 0;\n')
    out_file.write(f'ie;\n')
    out_file.write(f'cc[ .;\n') #inactivates characters
    out_file.write(f'log tnt.out;\n')
    out_file.write(f'scores;\n')
    out_file.write(f'log/;\n')
    out_file.write(f'zzz;\n')
    out_file.write(f'proc-/;\n')
  os.system('tnt proc random.tnt')
  os.system('rm random.tnt')


def parse_scores(tnt_scores_output):
  """
  This function parses  the output file "tnt.out", which are returns from functions
  tnt_random() and structured_tnt_matrix_scores().
  @param tnt_scores_output: the output file "tnt.out"
  @return: a list containing the tree scores computed by TNT
  """
  with open(tnt_scores_output, 'r') as file:
    scores = []
    lines = file.readlines()
    for line in lines[4:]:
      line_values = line.strip().split()
      scores.extend([int(val) for val in line_values[1:]])
    #print(f'These are the scores: {scores}')
  return scores


def generate_random_tree(n_terminals, prefix, current_leaf):
  """
  This function generates a random binary tree given the number of terminals. Terminals are
  names as 'terminal_1', 'terminal_2', 'terminal_3', etc.
  @param n_terminals: number of leafs for the tree
  @param prefix: by default 'terminal_'
  @param current_leaf: start at 1
  @return: random binary tree in newick format
  """
  if n_terminals == 1:
    return f"{prefix}{current_leaf}"
  left_size = randint(1, n_terminals - 1)
  right_size = n_terminals - left_size
  left_tree = generate_random_tree(left_size, prefix, current_leaf)
  right_tree = generate_random_tree(right_size, prefix, current_leaf + left_size)
  
  return f"({left_tree},{right_tree})"


def structured_tnt_matrix_scores(n_terminals,tree_file):
  """
  This function executes the following procedures:
    1. Given the number of characters, it will write a TNT input file containing n terminals
    and a single character, with the commands to read the random tree in TNT (tread) format
    modified from the output of generate_random_tree() and write a representation matrix of
    the tree into the file mrp.tnt;
    2. The file mrp.tnt is edited to remove ROOT and add headings and instructions for TNT
    to generate tree scores for all possible binary trees;
    3. TNT is executed.
  The rational here is that the representation matrix emulates a character set with no conflic,
  that is no homoplasy. That matrix then is evaluated in all possible trees.

  @param n_terminals: number of leaves
  @param tree_file: tree file in TNT tread format
  @return: The file tnt.out containing tree scores
  """
  with open("dummy.tnt", "w") as out_file:
    out_file.write(f'mxram 1024\n')
    out_file.write(f'xread\n')
    out_file.write(f'1 {n_terminals}\n')
    for n in range(1, n_terminals+1):
      out_file.write(f'terminal_{n}\t1\n')
    out_file.write(f';\n')
    out_file.write(f'taxname=;\n')
    out_file.write(f'hold 100000;\n')
    out_file.write(f'proc {tree_file};\n')
    out_file.write(f'mrp;\n')
    out_file.write(f'log mrp.tnt;\n')
    out_file.write(f'xread!;\n')
    out_file.write(f'log/;\n')
    out_file.write(f'zzz;\n')
    out_file.write(f'proc-/;\n')
  os.system('tnt proc dummy.tnt')
  with open('mrp.tnt', 'r') as file:
    content = []
    n_characters = 0
    for line in file:
      if line.startswith("terminal"):
        content.append(line)
      elif line.startswith("ROOT"):
        n_characters = line.count("0")
  with open('mrp.tnt', 'w') as file:
    file.write('mxram 1024\n')
    file.write('xread\n')
    file.write(f'{n_characters} {n_terminals}\n')
    for item in content:
      file.write(item)
    file.write(';\n')
    file.write('hold 100000;\n')
    file.write('taxname=;\n')
    #file.write(f'proc {tree_file};\n')
    file.write(f'cc] .;\n')  #inactivates characters
    file.write(f'collapse 0;\n')
    file.write(f'ie;\n')
    file.write(f'cc[ .;\n') #inactivates characters
    file.write(f'log tnt.out;\n')
    file.write(f'scores;\n')
    file.write(f'log/;\n')
    file.write(f'zzz;\n')
    file.write('proc-/;\n')
  os.system('tnt proc mrp.tnt')
  os.system('rm mrp.tnt')

def center_text(text, width=80, color="\033[0m"):
  spaces = (width - len(text)) // 2
  return f"{color} {' ' * spaces}{text}\033[0m"


def main():
  os.system('clear')
  #
  ## User selection
  #
  print(center_text("          ##########################################################", width=40, color="\033[33m"))
  print(center_text("          #   This script will help you to understand tree space   #", width=40, color="\033[33m"))
  print(center_text("          ##########################################################", width=40, color="\033[33m"))
  #
  print()
  #
  print(f'Those are the options you can evaluate:')
  print(f'')
  print(f'     1 - Tree space for a given number of terminals in the absence of character information.')
  print(f'     2 - Tree space considering a given number binary random caracters.')
  print(f'     3 - Tree space considering a given number binary characters')
  print(f'         with non-conflicting cladistic structure (no homoplasy).')
  print(f'     0 - To exit.')
  print(f'\n\n')
  permited_options = [0, 1, 2, 3]
  selection = int(input('Select your option [1|2|3|0]: '))
  if selection not in permited_options:
    print()
    print(f'     What is your problem?')
    print(f'     Cannot read instructions?')
    print(f'     Try again. Bye.')
    exit()
  if selection == 0:
    print(f'Tchau!')
    exit()
  print()
  print(f'Define de dimension of your matrix:')
  n_terminals = int(input('    How many terminals: '))
  print()
  x, y, z = axes_list(n_terminals)
  if selection == 1:
    print(f'You selected {selection}')
    #x, y, z = axes_list(n_terminals)
    generate_surface_plot_01(x,y,z)
    histogram(z)
  elif selection == 2:
    n_characters = int(input('How many characters: '))
    tnt_random(n_characters,n_terminals)
    z = parse_scores('tnt.out')
    original_scores = z # keeping original scores before adding below
    while len(z) < len(x)*len(y):  # required to match grid size for 3D plot
      z.append(max(z))
    generate_surface_plot_02(x,y,z)
    histogram(original_scores)
  elif selection == 3:
    #n_characters = int(input('     How many characters: '))
    # generating random tree
    prefix = "terminal_"
    current_leaf = 1
    random_tree = generate_random_tree(n_terminals, prefix, current_leaf)
    print(f'Random tree: {random_tree}\n')
    random_tree = random_tree.replace(",", " ")
    print(f'Random tree (tread): {random_tree}\n')
    # writing tread file
    with open("random.tre", "w") as out_file:
      out_file.write(f'tread\n')
      out_file.write(f'{random_tree};\n')
      out_file.write(f'proc-/;\n')
    # running TNT to get scores for all trees
    structured_tnt_matrix_scores(n_terminals, 'random.tre')
    z = parse_scores('tnt.out')
    original_scores = z # keeping original scores before adding below
    while len(z) < len(x)*len(y):  # required to match grid size for 3D plot
      z.append(max(z))
    generate_surface_plot_02(x,y,z)
    histogram(original_scores)

##
# INITIALIZATION
##

if __name__ == "__main__":
  main()

exit()




