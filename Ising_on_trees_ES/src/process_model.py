# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 14:52:28 2016


@author: Evgeny Sorkin,  evg.sorkin@gmail.com
"""

import logging
import logging.handlers
import numpy as np
import sys

logger = logging.getLogger('process model')
logger.addHandler(logging.StreamHandler(sys.stdout))

def minimize(T, S, E, n, i):
    print '====',i,E,S[i]
    if i == n:
        return E
    else:      
        node = T[i]
        Ep = 0
        if node.parent:
            Ep =  node.parent.spin*node.spin*node.J # parent edge contribution to the energy
        En = node.h*node.spin # self interaction
        #E_old = Ep+T.getE(node)
        node.spin  = - node.spin   # flip the spin  
        dE =  -2*(Ep +En) # change in the energy 
        E_new = minimize(T,S,E + dE,n,i+1)

        S[i]= node.spin if E_new<E else -node.spin
        node.spin = S[i]
        return min(E,E_new)
        #print S[i],E,Ei,node.index



def main(argv):
    """
    
    """   
    import os
    import tree
    import ising_io as io
        
    if len(sys.argv) !=2 :
        raise ValueError("The script takes exactly 1 arguments, {} are given. Stopping...".
            format(str(len(argv))+'\n'))
    
    params_fn = sys.argv[1]
    params_fn = '/home/evgeny/Documents/personal/D-Wave/Ising_on_trees_ES/data/test01.txt'
    
    logger.info('Getting model input info... \n')
    dataHandler = io.InputReader(params_fn)
    if not dataHandler.valid():
        logger.error('cannot read data file, exiting...')
        return
    testName, nS, nW = \
        dataHandler.testName, dataHandler.nS,dataHandler.nW
    #model_dict = {0:[(0,-1),(1,1)], 1:[(1,-1),(2,1),(3,1)], 2:[(2,-1)]} 
    model_dict = dataHandler.make_dict()
    
    logger.info('Building the tree... \n')
    T = tree.buildTree(model_dict)
    n=T.length()
    #check consistancy of the tree
    if n!=nS:
        logger.error('wrong number of spins, perhaps wrong data file. Exiting...')
        return
        
    S = map(int,np.ones(T.length()))
    T.setS(S) 
    
    logger.info('Find min energy state... \n')
    E = minimize(T,S,T.getE(),n-1,0)
    
    logger.info('Save the results ... \n')
    import ntpath 
    folder, fn = ntpath.split(params_fn)
    fn = str(testName)+'_OUT.txt'
    io.save2file(folder,fn, E, S)
    logger.info(' Done. \n')
    

if __name__ == "__main__":
    #import pdb; pdb.set_trace() 
    import sys
    main(sys.argv[1:])