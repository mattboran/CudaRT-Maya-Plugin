import json
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

kPluginCmdName = "exportCamera"
outputPath = "/home/matt/Documents/CudaRT/camera/camera.json"

class exportCamera(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        
    def doIt(self,args):
        cameras = cmds.ls(type=('camera'), l=True)
        startupCameras = [camera for camera in cameras if cmds.camera(cmds.listRelatives(camera, parent=True)[0], startupCamera=True, q=True)]
        nonStartupCameras = list(set(cameras) - set(startupCameras))
        cameras = nonStartupCameras
        for camera in cameras:
            transform = cmds.listRelatives(camera, p=True)[0]
            offset = cmds.getAttr(transform+".translate")[0]
            print 'transform: ' + str(transform)
            cam = OpenMaya.MFnCamera(self.getDagNode(camera))
            if cam.isOrtho():
                return
            if cam.name() == "main":
                with open(outputPath, "w") as file:
                    file.write(str(self.cameraJson(cam, offset)))
                break
        
    def getDagNode (self, xform):
        selectionList = OpenMaya.MSelectionList()
        try:
            selectionList.add( xform )
        except:
            return None
        dagPath = OpenMaya.MDagPath()
        selectionList.getDagPath( 0, dagPath )
        return dagPath
        
    def cameraJson(self, camera, offset):
        def listify(val, o=(0,0,0)):
            return [val.x+o[0], val.y+o[1], val.z+o[2]]
        eye = camera.eyePoint()
        view = camera.viewDirection()
        up = camera.upDirection()
        rt = camera.rightDirection()
        fov = float(cmds.camera(camera.name(), q=True, horizontalFieldOfView=True))
        ret = {'name': camera.name(),
                'fieldOfView': fov,
                'eye': listify(eye, offset),
                'viewDirection': listify(view),
                'upDirection': listify(up),
                'rightDirection': listify(rt)}
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