# -*- coding: utf-8 -*-
"""
Created on Sun Feb 25 12:22:01 2016


@author: Evgeny Sorkin,  evg.sorkin@gmail.com
"""

import logging
import logging.handlers
import numpy as np
import sys


logger = logging.getLogger('misc_utils')
logger.addHandler(logging.StreamHandler(sys.stdout))

def isInt(ch):
    """
    checks whether a character is int
    @param ch: string
    @return True/False
    
    """
    try:
        int(ch)
        return True
    except ValueError:
        return False