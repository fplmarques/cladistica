#!/usr/bin/R
##
# Cálculo de valor de bootstrap para vétice V, com r caracteres de suporte dentre os n caracteres da matriz assumindo que não haja incompatibilidade.
##  
n <- 8
r <- 2
VBt <- 1-(1-r/n)^n
VBt
