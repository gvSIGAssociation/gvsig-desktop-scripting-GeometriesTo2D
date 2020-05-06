# encoding: utf-8

import gvsig
from org.gvsig.tools import ToolsLocator
from java.io import File

try:
  from addons.GeometriesTo2D.geometriesTo2D import TransformGeometriesTo2D
except:
  import sys
  ex = sys.exc_info()[1]
  gvsig.logger("Can't load module 'TransformGeometriesTo2D'. " + str(ex), gvsig.LOGGER_WARN)#, ex)
  TransformGeometriesTo2D = None


def selfRegister(*args):
    i18nManager = ToolsLocator.getI18nManager()
    i18nManager.addResourceFamily("text",File(gvsig.getResource(__file__,"i18n")))
    
    process = TransformGeometriesTo2D()
    process.selfregister("Scripting")
    process.updateToolbox()

def main(*args):
    if TransformGeometriesTo2D== None:
      return
    selfRegister()
    
    
