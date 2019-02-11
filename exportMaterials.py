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
kBaseOutputMaterials = "/home/matt/Documents/CudaRT/meshes/%s"

kNameLambert = "LAMBERT"
kNameSpecular = "SPECULAR"
kNameDiffspec = "DIFFSPEC"
kNameGlossy = "MICROFACET"
kNameRefractive = "REFRACTIVE"

class exportMaterials(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self, args):
        outName = self.parseArguments(args)
        fileData = None
        # TODO: Try except, with the following command
        # cmds.file(force=True, options="groups=0;ptgroups=0;materials=1;smoothing=1;normals=1", type="OBJexport", pr=True, ea=(baseOutputMaterials % (outName+".obj")))
        with open(kBaseOutputMaterials % ("%s.mtl" % outName)) as f:
            fileData = f.read()
        materials = fileData.split('newmtl ')[1:]
        print "Got n=%s materials" % len(materials)
        newProps = []
        for material in materials:
            props = material.split('\n')
            if not props[0].endswith('SG'):
                continue
            sgName = props[0]
            name = cmds.defaultNavigation(defaultTraversal=True, destination="%s.surfaceShader" % sgName)[0]
            type = self.getMaterialType(name)
            print "Material %s has type %s" % (name, type)
            
        
    def getMaterialType(self, name):
        matlType = cmds.objectType(name)
        type = "NoneType"
        if "lambert" in matlType:
            return kNameLambert
        if cmds.getAttr("%s.refractions" % name) == 1 and cmds.getAttr("%s.refractiveIndex" % name) != 1.0:
            return kNameRefractive
        ks = cmds.getAttr("%s.specularColor" % name)[0]
        kd = cmds.getAttr("%s.color" % name)[0]
        if kd == (0.0, 0.0, 0.0):
            try:
                if cmds.getAttr("%s.roughness" % name) > 0.0:
                    return kNameGlossy
            except ValueError:
                pass
            return kNameSpecular
        return kNameDiffspec
        
            
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