# encoding: utf-8

import gvsig
from addons.GeometriesTo2D.geometriesTo2D import TransformGeometriesTo2D
from org.gvsig.tools import ToolsLocator
from java.io import File

def main(*args):
    selfRegister()
    
def selfRegister(*args):
    i18nManager = ToolsLocator.getI18nManager()
    i18nManager.addResourceFamily("text",File(gvsig.getResource(__file__,"i18n")))
    
    process = TransformGeometriesTo2D()
    process.selfregister("Scripting")
    process.updateToolbox()

    
