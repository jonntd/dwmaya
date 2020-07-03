__author__ = 'Olivier Evers'
__copyright__ = 'DreamWall'
__license__ = 'MIT'


import time
from functools import partial
from contextlib import contextmanager
import maya.cmds as mc
from dwmaya.qt import get_screen_size


DEFAULT_MODEL_EDITOR_ARGS = dict(
    displayAppearance='smoothShaded',
    shadows=False,
    displayTextures=True,

    fogging=False,
    fogColor=[1, 1, 1, 1],
    fogDensity=1,
    fogStart=0,
    fogEnd=100,
    fogMode='linear',
    fogSource='fragment',

    useDefaultMaterial=False,
    nurbsSurfaces=True,
    subdivSurfaces=True,
    polymeshes=True,
    planes=True,
    imagePlane=True,
    textures=True,
    pluginShapes=True,
    selectionHiliteDisplay=False,
    nurbsCurves=False,
    controlVertices=False,
    hulls=False,
    lights=False,
    cameras=False,
    ikHandles=False,
    deformers=False,
    dynamics=False,
    particleInstancers=False,
    fluids=False,
    hairSystems=False,
    follicles=False,
    nCloths=False,
    nParticles=False,
    nRigids=False,
    dynamicConstraints=False,
    locators=False,
    dimensions=False,
    pivots=False,
    handles=False,
    strokes=False,
    motionTrails=False,
    clipGhosts=False,
    greasePencils=False,
    joints=False,
    wireframeOnShaded=False)

AO_SETTINGS = dict(
    ssaoRadius=1,
    ssaoFilterRadius=1,
    ssaoAmount=1,
    ssaoEnable=1,
    ssaoSamples=32,
    multiSampleEnable=1)


def create_tearoff_viewport(
        camera, title=None, size=None, model_editor_args=None, position=None):
    tearoff_window = mc.window(title=title)

    _model_editor_args = model_editor_args or dict()
    model_editor_args = DEFAULT_MODEL_EDITOR_ARGS.copy()
    model_editor_args.update(_model_editor_args)
    model_editor_args['camera'] = camera

    if size is None:
        try:
            w, h = get_screen_size()
            size = w * .6, h * .6
        except BaseException:
            size = [1280, 720]
    mc.window(tearoff_window, edit=True, widthHeight=size)

    if position is None:
        position = [w / 10, h / 10]
    mc.window(tearoff_window, edit=True, topLeftCorner=position)

    mc.paneLayout()
    panel = mc.modelPanel()
    mc.timePort(height=30, snap=True)
    mc.showWindow(tearoff_window)
    editor = mc.modelPanel(panel, query=True, modelEditor=True)
    mc.modelEditor(editor, edit=True, **model_editor_args)
    mc.refresh()
    mc.modelEditor(editor, edit=True, activeView=True)
    return editor, panel, tearoff_window


def delete_tearoff_viewport(window):
    if mc.window(window, query=True, exists=True):
        mc.evalDeferred(partial(mc.deleteUI, window))


@contextmanager
def temp_tearoff_viewport(camera, model_editor_args=None, size=None):
    editor, panel, window = create_tearoff_viewport(
        camera, title='%s_tearoff' % camera,
        model_editor_args=model_editor_args)
    try:
        yield editor, panel, window
    finally:
        delete_tearoff_viewport(window)


@contextmanager
def temp_ambient_occlusion(camera):
    # Setup VP2 settings
    old_values = dict()
    for attr, value in AO_SETTINGS.items():
        old_values[attr] = mc.getAttr('hardwareRenderingGlobals.' + attr)
        mc.setAttr('hardwareRenderingGlobals.' + attr, AO_SETTINGS[attr])
    # Create lights
    directional = mc.directionalLight(intensity=-.4)
    ambient = mc.ambientLight(intensity=1)
    transforms = []
    for light in [directional, ambient]:
        transform = mc.listRelatives(light, parent=True)[0]
        transforms.append(transform)
        mc.parent(light, camera)
        mc.rotate(0, 0, 0, transform, objectSpace=True)
        mc.move(0, 0, 0, transform, objectSpace=True)
    try:
        yield None
    finally:
        mc.delete(transforms)
        # Reset VP2
        for attr, value in AO_SETTINGS.items():
            mc.setAttr('hardwareRenderingGlobals.' + attr, old_values[attr])


@contextmanager
def dummy_context(camera):
    yield None


if __name__ == '__main__':
    model_editor_args = dict(useDefaultMaterial=True, displayLights='all')
    with temp_tearoff_viewport(
            'persp', model_editor_args=model_editor_args) as (
            editor, panel, window):
        print(editor)
        time.sleep(1)
