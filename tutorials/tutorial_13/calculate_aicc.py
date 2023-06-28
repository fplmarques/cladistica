#!/usr/bin/env python3
#
## F. Marques, June 2023
#
n = int(input('Inserir número de caracteres [n]: '))
k = int(input('Inserir número de parâmetros livres [k]: '))
L = float(input('Inserir Likelihood Score da topologia [lnL]: '))
if L > 0:
    print(f'lnL deveria ser um número negativo!')
    print(f'Transformando {L} em negativo ...')
    L = L*-1
#
## calculating AIC
#
AIC = -2*L+2*k;
#
## calculating AICc
#
AICc = AIC+(2*k*(k-1)/(n-k-1));
#
## Printing results
#
print(f'Considerando {n} caracteres, {k} parâmetros livres e um lnL = {L}:')
print(f'')
print(f'AIC = {AIC:.4f}')
print(f'')
print(f'AICc = {AICc:.4f}')
