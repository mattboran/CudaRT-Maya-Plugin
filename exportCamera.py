import json
import math
import sys
import maya.OpenMaya as OpenMaya
import maya.api.OpenMaya as OpenMayaApi
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginCmdName = "exportCamera"
outputPath = "/home/matt/Documents/CudaRT/settings/camera.json"

class exportCamera(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self,args):
        def lengthOfVector(v):
            return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        cameras = cmds.ls(type=('camera'), l=True)
        startupCameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
        nonStartupCameras = list(set(cameras) - set(startupCameras))
        cameras = nonStartupCameras
        mainCamXform = [cam for cam in cameras if 'main' in cam][0]
        mainCam = mainCamXform.split('|')[2]
        rotMatrix = OpenMayaApi.MMatrix(cmds.xform(mainCam, q=True, r=True, matrix=True))
        translate = OpenMayaApi.MVector(cmds.xform(mainCam, q=True, t=True))
        up = OpenMayaApi.MVector(0,1,0) * rotMatrix
        cam = OpenMaya.MFnCamera(self.getDagNode(mainCamXform))
        aim = cmds.xform('%s_aim.rotatePivot' % mainCam, q=True, t=True)
        eye = cam.eyePoint()
        dir = [aim[0]-translate[0], aim[1]-translate[1], aim[2]-translate[2]]
        lenDir = lengthOfVector(dir)
        look = OpenMayaApi.MVector(0,0,1) * rotMatrix
        print 'dir = %s of length %s' % (dir, lenDir)
        print 'look = %s' % look
        with open(outputPath, "w") as file:
            file.write(json.dumps(self.cameraJson(cam, up, look, translate)))
        
    def getDagNode (self, xform):
        selectionList = OpenMaya.MSelectionList()
        try:
            selectionList.add( xform )
        except:
            return None
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath( 0, dagPath )
        return dagPath
        
    def cameraJson(self, camera, up, look, translate):
        def listify(val, offset=[0,0,0]):
            return [val.x+offset[0], val.y+offset[1], val.z+offset[2]]
        print "Saving camera %s" % camera.name()
        eye = camera.eyePoint()
        fov = float(cmds.camera(camera.name(), q=True, horizontalFieldOfView=True))
        focalLength = float(cmds.camera(camera.name(), q=True, focalLength=True))
        fstop = float(cmds.camera(camera.name(), q=True, fStop=True))
        useDepthOfField = 1 if bool(cmds.camera(camera.name(), q=True, depthOfField=True)) else 0
        ret = {'name': camera.name(),
                'fieldOfView': fov,
                'eye': listify(eye, translate),
                'viewDirection': listify(look, translate),
                'upDirection': listify(up),
                'focalLength': focalLength * 0.001,
                'fStop': fstop,
                'depthOfField': useDepthOfField}
        return ret
        
# Creator
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( exportCamera() )
    
# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator )
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