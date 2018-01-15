# encoding: utf-8

import gvsig
from addons.GeometriesTo2D.geometriesTo2D import TransformGeometriesTo2D

def main(*args):
    selfRegister()
    
def selfRegister(*args):
    process = TransformGeometriesTo2D()
    process.selfregister("Scripting")
    process.updateToolbox()
