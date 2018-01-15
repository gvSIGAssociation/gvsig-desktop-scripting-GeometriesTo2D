# encoding: utf-8

import gvsig
import os
from gvsig import geom
from org.gvsig.fmap.geom import Geometry
from org.gvsig.fmap.geom import GeometryLocator
from org.gvsig.fmap.geom.aggregate import MultiPrimitive
from org.gvsig.fmap.geom.primitive import Polygon, Point
# Con geometrias normales se quedaria con el getGeometryType()
from es.unex.sextante.dataObjects import IVectorLayer
from gvsig.libs.toolbox import ToolboxProcess
from es.unex.sextante.gui import core
from es.unex.sextante.gui.core import NameAndIcon
#from es.unex.sextante.parameters import ParameterDataObject
#from es.unex.sextante.exceptions import WrongParameterTypeException
from es.unex.sextante.additionalInfo import AdditionalInfoVectorLayer
#from gvsig import logger
#from gvsig import LOGGER_WARN
#from es.unex.sextante.additionalInfo import AdditionalInfo
from org.gvsig.geoprocess.lib.api import GeoProcessLocator


class TransformGeometriesTo2D(ToolboxProcess):
  def defineCharacteristics(self):
    self.setName("Transformar geometrias a 2D")
    self.setGroup("Transformar")
    params = self.getParameters()
    self.setUserCanDefineAnalysisExtent(False)
    params.addInputVectorLayer("studyAreaNameVector","Capa a transformar", AdditionalInfoVectorLayer.SHAPE_TYPE_ANY,True)
    params.addFilepath("outputFilePath","Capa de salida",False,False,True,[".shp"])

  def processAlgorithm(self):
    params = self.getParameters()
    studyAreaNameVector = params.getParameterValueAsVectorLayer("studyAreaNameVector").getFeatureStore()
    outputFilePath = params.getParameterValueAsString("outputFilePath")
    if outputFilePath == "":
        outputFilePath = gvsig.getTempFile("result_geometries",".shp")
    elif not outputFilePath.endswith('.shp'):
        outputFilePath = outputFilePath+".shp"
    process(self, studyAreaNameVector,outputFilePath)
    return True
    
    
def transformPointTo2D(iVertex,nv=None):
    if nv is None:
        nv = GeometryLocator.getGeometryManager().create(iVertex.getGeometryType().getType(),Geometry.SUBTYPES.GEOM2D)
    #print "Ivertex: ", iVertex
    for d in range(0,iVertex.getDimension()):
        try:
            nv.setCoordinateAt(d,iVertex.getCoordinateAt(d))
        except:
            pass
    #print "NV: ", nv, " from ", iVertex
    return nv
    
def process(selfStatus,store,outputFilePath=None):
    # SELECT METHOD TO TRANSFORM POINTS
    method = "transformPointTo2D" #None
    
    geomManager = GeometryLocator.getGeometryManager()

    fset = store.getFeatureSet()
    nsch = gvsig.createFeatureType(store.getDefaultFeatureType())
    
    if method == "transformPointTo2D":
        transformMethod = transformPointTo2D
        subtype = geom.D2
    else:
        transformMethod = None
        subtype = nsch.get("GEOMETRY").getGeometrySubType()
        
    nsch.get("GEOMETRY").setGeometryType(nsch.get("GEOMETRY").getGeometryType(), subtype)
    if outputFilePath is None:
        outputFilePath = gvsig.getTempFile("result_geometries",".shp")
    ns = gvsig.createShape(nsch,outputFilePath)
    ns.edit()
    store = ns.getFeatureStore()
    selfStatus.setRangeOfValues(0,fset.getSize())
    for f in fset:
        selfStatus.next()
        fg = f.getDefaultGeometry()
        #print "Default geometry: ", fg,
        if subtype == None: 
            subtype =  fg.getGeometryType().getSubType()
        nm = geomManager.create(fg.getGeometryType().getType(), subtype)
        #print "to: ", nm
        if isinstance(fg,MultiPrimitive):
            for i in range(0,fg.getPrimitivesNumber()):
                iPol = fg.getPrimitiveAt(i)
                np = geomManager.create(iPol.getGeometryType().getType(), subtype)
                insertVertexFromGeometryInGeometry(iPol, np, transformMethod)
                nm.addPrimitive(np)
        else:
            insertVertexFromGeometryInGeometry(fg, nm,transformMethod)
        nf = store.createNewFeature(f)
        nf.set("GEOMETRY", nm)
        store.insert(nf)
        if selfStatus.isCanceled() == True:
            ns.finishEditing()
            return True
    ns.finishEditing()
    gvsig.currentView().addLayer(ns)
    
def insertVertexFromGeometryInGeometry(iPol,np,transformMethod=None):
    geomManager = GeometryLocator.getGeometryManager()
    if isinstance(iPol, Point):
        if transformMethod is None:
            for d in range(0,iPol.getDimension()):
                np.setCoordinateAt(d,iPol.getCoordinateAt(d))
            return
        else:
            transformMethod(iPol,np)
            return
    
    for v in range(0, iPol.getNumVertices()):
        iVertex = iPol.getVertex(v)
        if transformMethod is None:
            nv = geomManager.create(iVertex.getGeometryType().getType(),iVertex.getGeometryType().getSubType())
            for d in range(0,iVertex.getDimension()):
                nv.setCoordinateAt(d,iVertex.getCoordinateAt(d))
        else:
            nv = transformMethod(iVertex)
        np.addVertex(nv)
    
    if isinstance(iPol, Polygon):
        for r in range(0, iPol.getNumInteriorRings()):
            iRing = iPol.getInteriorRing(r)
            nr = geomManager.create(iRing.getGeometryType().getType(),iRing.getGeometryType().getSubType())
            insertVertexFromGeometryInGeometry(iRing, nr,transformMethod)
            np.addInteriorRing(nr)

def main(*args):
    process = TransformGeometriesTo2D()
    process.selfregister("Scripting")
    #gm = GeoProcessLocator.getGeoProcessManager()

    # Actualizamos el interface de usuario de la Toolbox
    process.updateToolbox()
    #store = gvsig.currentLayer().getFeatureStore()
    #process(store)
    