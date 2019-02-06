import json
import math
import sys
import os
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

kPluginCmdName = "exportMaterials"
kShortOutputFlagName = '-o'
kLongOutputFlagName = '-output'
baseOutputPath = "/home/matt/Documents/CudaRT/settings/"

class exportMaterials(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self, args):
        matls = cmds.ls(mat=1)
        materials = []
        for mat in matls:
            specs = {'name': mat}
            specs['ka'] = self.getAttributeOrDefault(mat, "ambientColor", [0,0,0])
            specs['kd'] = self.getAttributeOrDefault(mat, "color", [0.5,0.5,0.5])
            specs['diffuse'] = self.getAttributeOrDefault(mat, "diffuse", 1.0)
            specs['roughness'] = self.getAttributeOrDefault(mat, "roughness", 0.0)
            specs['ks'] = self.getAttributeOrDefault(mat, "specularColor", [0.5, 0.5, 0.5])
            specs['ni'] = self.getAttributeOrDefault(mat, "refractiveIndex", 1.0)
            materials.append(specs)
        output = {'materials': materials}
        outName = self.parseArguments(args)
        outputPath = '%s%s-materials.json' % (baseOutputPath, outName)
        with open(outputPath, 'w') as f:
            f.write(json.dumps(output))
            
    def parseArguments(self, args):
        argData = OpenMaya.MArgParser(self.syntax(), args)
        filepath = cmds.file(q=True, sn=True)
        filename = os.path.basename(filepath)
        output, extension = os.path.splitext(filename)
        if argData.isFlagSet(kShortOutputFlagName):
            output = argData.flagArgumentString(kShortOutputFlagName, 0)
        return output
            
    def getAttributeOrDefault(self, node, attr, default):
        if cmds.attributeQuery(attr, node=node, exists=True):
            val = cmds.getAttr("%s.%s" % (node, attr))
            if isinstance(val, list):
                return list(val[0])
            return val
        return default  
# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( exportMaterials() )
    
def syntaxCreator():
    syntax = OpenMaya.MSyntax()
    syntax.addFlag(kShortOutputFlagName, kLongOutputFlagName, OpenMaya.MSyntax.kString)
    return syntax
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:  
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )  