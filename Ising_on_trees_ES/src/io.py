# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 09:45:28 2016


@author: Evgeny Sorkin,  evg.sorkin@gmail.com
"""

import logging
import logging.handlers
import numpy as np
import sys
import os

logger = logging.getLogger('io')
logger.addHandler(logging.StreamHandler(sys.stdout))

class InputReader(object):
    """
    A simple class to read the input from a file
    """
    
    def __init__(self,filename, **kwargs):
        
        self.fileName = filename
        
        self.__commentLn = 'c'   # comments lines
        self.__problemLn = 'p'   # problem lines
        self.__delimiter = ' '   # delimier of data fields
        
        self.__valid = False
        
        self.testName = ''
        self.nS = 0
        self.nW = 0
        self.weights =[]
        
        self.__valid = self._readFile()
        
        
        
    def valid(self): return self.__valid    
        
  

    def _readFile(self):
        """
        reads the text file and checks if the input is valid
        """
        import misc_utils
        lines =[]
        try:
            with open(self.fileName, "r") as f:
                lines=f.readlines() 
        except IOError:
            logger.error('could not open file {}. Skipping'.format(self.fileName))
            return False

        #remove lines with comments and empty lines. Remove  eol characters and extra spaces :
        lines = [self.__delimiter.join(l.rstrip('\n').split()) for l in lines 
                    if l[0] not in [self.__commentLn, '\n']]
         
        # check that problem lines appear before data lines                   
        plines = [(i,l) for i,l in enumerate(lines) if l[0]==self.__problemLn]
        dlines = [(i,l) for i,l in enumerate(lines) if l[0]!=self.__problemLn]
        max_pln = max(plines, key=lambda item:item[0])[0]
        min_dln = min(dlines, key=lambda item:item[0])[0]
        if min_dln<max_pln:
            logger.error('File {} has wrong format'.format(self.fileName))
            return False
        
        # check problem lines, has to be of form ['p test01 4 6']
        valid_plines = [ p[1] for p in plines if len(p[1].split(self.__delimiter)) == 4 and
                         p[1].split(self.__delimiter)[0] == self.__problemLn and
                         p[1].split(self.__delimiter)[2].isdigit() and
                         p[1].split(self.__delimiter)[3].isdigit()]
        
        if len(valid_plines) != 1:
            logger.error('File {} has wrong format, wrong problem lines'.format(self.fileName))
            return False
         
        testName, nS, nW  = valid_plines[0].split(self.__delimiter)[1:]
        nS,nW = int(nS),int(nW)
        
        #check val of data lines and number of weights:
        dlines = [d[1] for d in dlines]
        if nW != len(dlines) :
            logger.error('File {} has wrong format, wrong number of weights'.format(self.fileName))
            return False   
        
        #check validity of data format
        
        if 3*nW != len([ch  for l in dlines for ch in 
            l.split(self.__delimiter) if misc_utils.isInt(ch)]):
            logger.error('File {} has wrong format, bad weights'.format(self.fileName))
            return False 
  
        self.testName, self.nS, self.nW  = testName, nS, nW
        self.weights = dlines
        
        logger.info('Loaded data')
        
        return True 
    
    def make_dict(self, bSort = True):
        """
        creates dict to be passed to the IsingTree contsructor in case all data input was correct
        sorts by spin is bSort is True
        @return dict
        """
        data_dict = None
        if self.valid():
            data_dict = self._make_dict()
            if bSort:
                #sort by spin  
                for k in data_dict.keys():    
                    data_dict[k].sort( key = lambda x: x[0])  
        return data_dict
        
    def _make_dict(self):
        """
        creates dict to be passed to the IsingTree contsructor
        @return dict
        """     
        import collections
        dd = collections.defaultdict(list)
        
        for d in self.weights:
            dw = d.split(self.__delimiter)
            dd[int(dw[0])].append((int(dw[1]),int(dw[2])))
  
        return dict(dd)     
        
def save2file(folder, fn, E, S):
    """
    Saves output of the model to file
    
    @param folder: str, where tor save the data
    @param filename: str, where tor save the output filename
    @param E: float, energy 
    @param S: list, spin state
     
    """
    Sout = ''.join(['+' if s>0 else '-' for s in S]) #format spin state
    #import pdb; pdb.set_trace()
    if not os.path.exists(folder): # create the folder if it doesn't excist
            os.makedirs(folder)
    fn0 = os.path.join(folder,fn)        
           
    with open(fn0, "w") as f:
        try:
            f.write((str(E)+u'\n').encode('unicode-escape'))
            f.write((Sout+u'\n').encode('unicode-escape'))
        except Exception as e:
            logger.error('Failed to write file, exception {}'.format(type(e)))
            return False 
      
    return True    