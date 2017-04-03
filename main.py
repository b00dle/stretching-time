#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua


### import application libraries
from lib.SimpleViewingSetup import SimpleViewingSetup
from lib.AdvancedViewingSetup import StereoViewingSetup
from lib.PointerInput import PointerInput
from lib.Scene import Scene
from lib.game.Game import Game

def start():


    ## create scenegraph
    scenegraph = avango.gua.nodes.SceneGraph(Name = "scenegraph")

    ## init viewing setup
    #viewingSetup = init_simple_viewing_setup(scenegraph)
    viewingSetup = init_advanced_viewing_setup(scenegraph)
    #viewingSetup = SimpleViewingSetup(SCENEGRAPH = scenegraph, STEREO_MODE = "anaglyph")

    ## init input
    pointerInput = init_input_setup(viewingSetup, scenegraph)

    ## init scene
    scene = Scene(PARENT_NODE = scenegraph.Root.value)

    ## init spawner
    game = Game()
    game.my_constructor(
      SCENE_ROOT = scenegraph.Root.value,
      HEAD_NODE = viewingSetup.head_node,
      SCREEN_NODE = viewingSetup.screen_node,
      POINTER_INPUT = pointerInput
    )

    ## init field connections (dependency graph)
    print_graph(scenegraph.Root.value)

    ## start application/render loop
    viewingSetup.run(locals(), globals())


### helper functions ###
def init_simple_viewing_setup(SCENEGRAPH):
  return SimpleViewingSetup(SCENEGRAPH = SCENEGRAPH, STEREO_MODE = "mono")

def init_advanced_viewing_setup(SCENEGRAPH):
  hostname = open('/etc/hostname', 'r').readline()
  hostname = hostname.strip(" \n")
  
  print("wokstation:", hostname)

  viewingSetup = None
  if hostname == "orestes": # Mitsubishi 3D-TV workstation
    _tracking_transmitter_offset = avango.gua.make_trans_mat(-0.98, -(0.58 + 0.975), 0.27 + 3.48) * avango.gua.make_rot_mat(90.0,0,1,0) # transformation into tracking coordinate system 

    viewingSetup = StereoViewingSetup(
        SCENEGRAPH = SCENEGRAPH,
        WINDOW_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        SCREEN_DIMENSIONS = avango.gua.Vec2(1.445, 0.81),
        LEFT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        RIGHT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        STEREO_FLAG = True,
        STEREO_MODE = avango.gua.StereoMode.CHECKERBOARD,
        HEADTRACKING_FLAG = True,
        HEADTRACKING_STATION = "tracking-art-glasses-1", # wired 3D-TV glasses on Mitsubishi 3D-TV workstation
        TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
        )

  elif hostname == "athena": # small powerwall workstation
    _tracking_transmitter_offset = avango.gua.make_trans_mat(0.0,-1.42,1.6) # transformation into tracking coordinate system

    viewingSetup = StereoViewingSetup(
        SCENEGRAPH = SCENEGRAPH,
        WINDOW_RESOLUTION = avango.gua.Vec2ui(1920*2, 1200),
        SCREEN_DIMENSIONS = avango.gua.Vec2(3.0, 2.0),
        LEFT_SCREEN_POSITION = avango.gua.Vec2ui(140, 0),
        LEFT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1780, 1185),
        RIGHT_SCREEN_POSITION = avango.gua.Vec2ui(1920, 0),
        RIGHT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1780, 1185),
        STEREO_FLAG = True,
        STEREO_MODE = avango.gua.StereoMode.SIDE_BY_SIDE,
        HEADTRACKING_FLAG = True,
        HEADTRACKING_STATION = "tracking-art-glasses-2", # small powerwall polarization glasses
        TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
        )

  elif hostname == "kronos": # Samsung 3D-TV workstation
    _tracking_transmitter_offset = avango.gua.make_trans_mat(0.0, -0.5, 0.6) # transformation into tracking coordinate system 

    viewingSetup = StereoViewingSetup(
        SCENEGRAPH = SCENEGRAPH,
        WINDOW_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        SCREEN_DIMENSIONS = avango.gua.Vec2(1.235, 0.7),
        LEFT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        RIGHT_SCREEN_RESOLUTION = avango.gua.Vec2ui(1920, 1080),
        STEREO_FLAG = True,
        STEREO_MODE = avango.gua.StereoMode.CHECKERBOARD,
        HEADTRACKING_FLAG = True,
        HEADTRACKING_STATION = "tracking-pst-glasses-1", # wired 3D-TV glasses on Samsung 3D-TV workstation
        TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
        )
          
  else:
    print("No Viewing Setup available for this workstation")
    quit()

  return viewingSetup

def init_input_setup(VIEWING_SETUP, SCENEGRAPH):
  hostname = open('/etc/hostname', 'r').readline()
  hostname = hostname.strip(" \n")

  pointerInput = None
  if hostname == "athena": # small powerwall workstation
    _tracking_transmitter_offset = avango.gua.make_trans_mat(0.05,-1.43,1.6) # transformation into tracking coordinate system

    pointerInput = PointerInput()
    pointerInput.my_constructor(
        SCENEGRAPH = SCENEGRAPH,
        NAVIGATION_NODE = VIEWING_SETUP.navigation_node,
        POINTER_TRACKING_STATION = "tracking-art-pointer-1",
        TRACKING_TRANSMITTER_OFFSET = _tracking_transmitter_offset,
        POINTER_DEVICE_STATION = "device-pointer-1",
        HEAD_NODE = VIEWING_SETUP.head_node
        )

  return pointerInput

## print the subgraph under a given node to the console
def print_graph(root_node):
  stack = [(root_node, 0)]
  while stack:
    node, level = stack.pop()
    print("│   " * level + "├── {0} <{1}>".format(
      node.Name.value, node.__class__.__name__))
    stack.extend(
      [(child, level + 1) for child in reversed(node.Children.value)])

## print all fields of a fieldcontainer to the console
def print_fields(node, print_values = False):
  for i in range(node.get_num_fields()):
    field = node.get_field(i)
    print("→ {0} <{1}>".format(field._get_name(), field.__class__.__name__))
    if print_values:
      print("  with value '{0}'".format(field.value))


if __name__ == '__main__':
  start()