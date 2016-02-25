# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 12:24:08 2016

@author: Evgeny Sorkin,  evg.sorkin@gmail.com
"""

import logging
import logging.handlers
import numpy as np
import sys
logger = logging.getLogger('Ising tree')
logger.addHandler(logging.StreamHandler(sys.stdout))


class Node(object):
    """
    A simple class to hold tree nodes 
    """
    def __init__(self, index, h = 0, J = 0, spin = -1, parent = None):
        """
        @param index: int, index i of the node 
        @param spin: +1 or -1
        @param weights: list of tuples [(j,val)], where j is the index of a node (including self) 
        """

        self.index = index
                
        if None is not spin and not np.abs(spin) == 1:
            logger.error('wrong value of spin {}, must be +1 or -1'.format(spin))
            return
        self.spin = spin       
        self.h = h    
        self.J = J
        self.children = []     
        self.parent = parent
        
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)   
     
    def isRoot(self): return not self.parent       
    def hasChildren(self): return len(self.children)>0    
    def isLeaf(self): return not self.hasChildren() 
    def getChild(self,index):
        """
        Look for children with index 
        @param index: int
        @return: child
        """
        try:
            for child in self.children:
                if index == child.index: 
                    return child                   
        except KeyError:
            pass
        return None
            

class IsingTree(object):
    """
    A class to build/store/traverse Ising model on trees
    """
    def __init__(self):
        self.root = None
        self.size = 0
        self.__spinStates =[1,-1] #allowed spin states
    

    def length(self):
        return self.size

    def __len__(self):
        return self.size

    def __iter__(self):
        return self.root.__iter__()
    
   
    def get(self,index):
        """
        gets the node with index, if it exists 
        @param index: int
        @return Node() object with index, or None if not 
    
        """

        if self.root and index<self.length():
            res = self._get(index,self.root)
            if res:
                return res
            else:
                print ('not found')
                return None
        else:
            return None

    def _get(self,index,currentNode):
        """ a recursive getter""" 
        if not currentNode:
            return None
        elif currentNode.index == index:
            return currentNode
        else:
            for child in currentNode.children:
                x = self._get(index,child)
                if x: return x
                    
    
    def __getitem__(self,index):
        return self.get(index)            
        
    def put(self, index, new_node ):
        """
        Appends a new_node at the node with index, appends at root if no index found 
        """
        node = self.get(index)           
        if not node:
            self.root  = new_node
        else:
            new_node.parent = node
            node.children.append(new_node)
        self.size += 1
        
    def _walk_tree(self, node = None):
        """
        The chief method to traverse the tree        
        
        Iterate tree in pre-order depth-first search order
        starting from node 
        
        Note: it is recursive and has speed O(n log n)
        
        @return: iterator
        """        
        yield node
        for child in node.children:
            for n in self._walk_tree(child):
                yield n

         
    def print_tree(self, node = None):
        """
        prints the entire tree in pre-order depth-first search order
        """
        start_node = node
        if not node:
            start_node = self.root            
        for x in self._walk_tree(start_node):
           print ('node index {}, spin {}, h {}, J {} , children {}, parent {}'.
                    format(x.index, x.spin, x.h, x.J, [c.index for c in x.children],
                           x.parent.index if x.parent else None))
    def numOfNodes(self, node = None):
        """
        returns number of nodes of subtree at node
        """
        start_node = node
        if not node:
            return self.length()            
        N = 0     
        for x in self._walk_tree(start_node):
            N+=1
        return N    
                       
    def setS(self,S, node = None):
        """
        Inserts spin state S=[s1,s2,....,sn] to the tree
        @param S: list
        @return: True/False
        """
        start_node = node
        if not node:
            start_node = self.root
        N = self.numOfNodes(start_node)
        
        if N != len(S):
            logger.warning('wrong size of spin vector S, must be {}'.format(N))
            return False
        
        for i,x in enumerate(self._walk_tree(start_node))  : 
            #Note:  in general should be checking if S[x.index] in self.__spinStates     
            x.spin = S[x.index]
 
        return True 
        
    def getS(self, node = None):
        """
        returns spin state of a subtree rooted at node
        """
        start_node = node
        if not node:
            start_node = self.root
        S=[]
        for x in self._walk_tree(start_node):
           S.append(x.spin)
        return S    
        
    def getE(self, node = None):
        """
        returns energy of a subtree rooted at node
        """
        start_node = node
        if not node:
            start_node = self.root 
            
        E = 0 
        for x in self._walk_tree(start_node):
           E += x.spin*(x.h + sum([ch.J*ch.spin for ch in x.children]))
        return E
        
        
def buildTree(model_dict):
    """
    Build Ising Tree, based on model_dict
    @param model_dict: dict of shape { i: (i,h),(j,J_ij),..., }
    @return: root to the resulting tree
    
    """
    #  model_dict  ={0:[(0,-1),(1,1)], 1:[(1,-1),(2,1),(3,1)], 2:[(2,-1)]}

    T = IsingTree() # new tree
  
    for k, links in model_dict.items():
        node=T[k] #get/create current node with index k
        if not node:
            node = Node(k)
            T.put(k, node)
        for l in links: 
            j = l[0]  # index of all conected spin
            if j==k:  # update self-interation
                node.h=l[1]
            else: # update the children
                child = T[j]
                if not child:
                    child = Node(j, J = l[1], parent = node)
                    T.put(k,child)
    return T
    
