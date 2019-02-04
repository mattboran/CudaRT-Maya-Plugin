import json
import math
import sys
import os
import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as OpenMayaApi
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginCmdName = "exportCamera"
kShortOutputFlagName = '-o'
kLongOutputFlagName = '-output'
baseOutputPath = "/home/matt/Documents/CudaRT/settings/"

class exportCamera(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self,args):
        def lengthOfVector(v):
            return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        cameras = cmds.ls(type='camera', l=True)
        startupCameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
        nonStartupCameras = list(set(cameras) - set(startupCameras))
        cameras = nonStartupCameras
        mainCamXform = [cam for cam in cameras if 'main' in cam][0]
        mainCam = mainCamXform.split('|')[2]
        print("Main cam xform %s" % mainCamXform)
        print("Main cam name: %s" % mainCam)
        rotMatrix = OpenMayaApi.MMatrix(cmds.xform(mainCam, q=True, r=True, matrix=True))
        translate = OpenMayaApi.MVector(cmds.xform(mainCam, q=True, t=True))
        up = OpenMayaApi.MVector(0,1,0) * rotMatrix
        cam = OpenMaya.MFnCamera(self.getDagNode(mainCamXform))
        aim = cmds.xform('%s_aim' % mainCam, q=True, t=True)
        dir = [aim[0]-translate[0], aim[1]-translate[1], aim[2]-translate[2]]
        lenDir = lengthOfVector(dir)
        look = OpenMayaApi.MVector(0,0,-lenDir) * rotMatrix
        outName = self.parseArguments(args)
        outputPath = '%s%s-camera.json' % (baseOutputPath, outName)
        print 'Saving to output path %s ' % outputPath
        with open(outputPath, "w") as file:
            file.write(json.dumps(self.cameraJson(cam.name(), up, look, translate, lenDir)))
    
    def parseArguments(self, args):
        argData = OpenMaya.MArgParser(self.syntax(), args)
        filepath = cmds.file(q=True, sn=True)
        filename = os.path.basename(filepath)
        output, extension = os.path.splitext(filename)
        if argData.isFlagSet(kShortOutputFlagName):
            output = argData.flagArgumentString(kShortOutputFlagName, 0)
        return output
    
    def getDagNode (self, xform):
        selectionList = OpenMaya.MSelectionList()
        try:
            selectionList.add( xform )
        except:
            return None
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath( 0, dagPath )
        return dagPath
        
    def cameraJson(self, camName, up, look, translate, focusDistance):
        def listify(val):
            return [val.x, val.y, val.z]
        print "Saving camera %s" % camName
        fov = float(cmds.camera(camName, q=True, horizontalFieldOfView=True))
        focalLength = float(cmds.camera(camName, q=True, focalLength=True))
        fstop = float(cmds.camera(camName, q=True, fStop=True))
        useDepthOfField = 1 if bool(cmds.camera(camName, q=True, depthOfField=True)) else 0
        ret = {'name': camName,
                'fieldOfView': fov,
                'eye': listify(translate),
                'viewDirection': listify(look),
                'upDirection': listify(up),
                'focalLength': focalLength * 0.001,
                'fStop': fstop,
                'depthOfField': useDepthOfField,
                'focusDistance': focusDistance}
        return ret
        
# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( exportCamera() )

def syntaxCreator():
    syntax = OpenMaya.MSyntax()
    print 'Creating syntax'
    syntax.addFlag(kShortOutputFlagName, kLongOutputFlagName, OpenMaya.MSyntax.kString)
    print ("created syntax!")
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
