#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed
import avango.daemon

class PointerInput(avango.script.Script):

    ## input fields
    sf_button = avango.SFBool()

    def __init__(self):
        self.super(PointerInput).__init__() 

    def my_constructor(self, 
        SCENEGRAPH,
        NAVIGATION_NODE,
        POINTER_TRACKING_STATION,
        TRACKING_TRANSMITTER_OFFSET,
        POINTER_DEVICE_STATION, HEAD_NODE):

        ### external references ###
        self.SCENEGRAPH = SCENEGRAPH
            
        ### resources ###
    
        ## init sensors
        self.pointer_tracking_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_tracking_sensor.Station.value = POINTER_TRACKING_STATION
        self.pointer_tracking_sensor.TransmitterOffset.value = TRACKING_TRANSMITTER_OFFSET
            
        self.pointer_device_sensor = avango.daemon.nodes.DeviceSensor(DeviceService = avango.daemon.DeviceService())
        self.pointer_device_sensor.Station.value = POINTER_DEVICE_STATION

        ## init field connections
        self.sf_button.connect_from(self.pointer_device_sensor.Button0)


        ## init nodes
        self.pointer_node = avango.gua.nodes.TransformNode(Name = "pointer_node")
        self.pointer_node.Transform.connect_from(self.pointer_tracking_sensor.Matrix)
        NAVIGATION_NODE.Children.value.append(self.pointer_node)

        ### further resources ###
        _loader = avango.gua.nodes.TriMeshLoader()
        
        self.hand_geometry = _loader.create_geometry_from_file("debug_hand_geometry",
                                                               "data/objects/sword.obj",
                                                               avango.gua.LoaderFlags.DEFAULTS)
        self.hand_geometry.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 0.0) * avango.gua.make_scale_mat(0.7,0.7,0.7)
        #self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.91,0.70,0.54,1.0))
        self.hand_geometry.Material.value.set_uniform("Color", avango.gua.Vec4(0.0,0.0,0.0,1.0))
        #self.hand_geometry.Tags.value = ["invisible"]
        self.pointer_node.Children.value.append(self.hand_geometry)

        self.always_evaluate(True)

    ## implement base class function
    def evaluate(self):
        pass#print(self.pointer_node.WorldTransform.value)

    def showDebugGeometry(self, ENABLED=True):
        ''' switches on and of debug geometry for pointer visualization. '''
        if ENABLED:
            self.hand_geometry.Tags.value = []
        else:
            self.hand_geometry.Tags.value = ["invisible"] 

    @field_has_changed(sf_button)
    def sf_button_changed(self):
        pass#print(self.sf_button.value)

