#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

class Glumb(avango.script.Script):
    ''' Monkey styled environment prop. '''

    def __init__(self):
        self.super(Glumb).__init__()

        # stores root node
        self.node = None

        # list of geometry nodes
        self._mouth_transform = None
        self._mouth_outside = None
        self._mouth_teeth = None
        self._mouth_black = None

        self._left_eye_transform = None
        self._left_eye_outside = None
        self._left_eye_iris = None
        self._left_eye_pupil = None

        self._right_eye_transform = None
        self._right_eye_outside = None
        self._right_eye_iris = None
        self._right_eye_pupil = None

    def my_constructor(self, PARENT_NODE):
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        _skin_tone = avango.gua.Vec4(198.0/256.0, 134/256.0, 66/256.0, 1.0)
        _teeth_tone = avango.gua.Vec4(255.0/256.0, 255.0/256.0, 240.0/256.0, 1.0)

        self.node = avango.gua.nodes.TransformNode(Name = "glumb_base")
        PARENT_NODE.Children.value.append(self.node)

        # init mouth transform
        self._mouth_transform = avango.gua.nodes.TransformNode(Name = "glumb_mouth")
        self.node.Children.value.append(self._mouth_transform)

        # init mouth outside geometry
        self._mouth_outside = _loader.create_geometry_from_file(
            "mouth_outside_geometry",
            "data/objects/glumb/glumb1.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._mouth_outside.Material.value.set_uniform(
            "Color",
            _skin_tone
        )
        self._mouth_transform.Children.value.append(self._mouth_outside)

        # init mouth teeth geometry
        self._mouth_teeth = _loader.create_geometry_from_file(
            "mouth_teeth_geometry",
            "data/objects/glumb/glumb2.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._mouth_teeth.Material.value.set_uniform(
            "Color",
            _teeth_tone
        )
        self._mouth_transform.Children.value.append(self._mouth_teeth)
        
        # init mouth black geometry
        self._mouth_black = _loader.create_geometry_from_file(
            "mouth_black_geometry",
            "data/objects/glumb/glumb3.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._mouth_black.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0,0.0,0.0,1.0)
        )
        self._mouth_transform.Children.value.append(self._mouth_black)

        # init left eye
        self._left_eye_transform = avango.gua.nodes.TransformNode(Name = "glumb_left_eye")
        self._left_eye_transform.Transform.value = avango.gua.make_trans_mat(-1.0, 1.75, 0.0)
        self.node.Children.value.append(self._left_eye_transform)

        # outside
        self._left_eye_outside = _loader.create_geometry_from_file(
            "left_eye_outside_geometry",
            "data/objects/glumb/glumb_eye1.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._left_eye_outside.Material.value.set_uniform(
            "Color",
            _skin_tone
        )
        self._left_eye_transform.Children.value.append(self._left_eye_outside)

        # iris
        self._left_eye_iris = _loader.create_geometry_from_file(
            "left_eye_iris_geometry",
            "data/objects/glumb/glumb_eye2.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._left_eye_iris.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0, 1.0, 1.0, 1.0)
        )
        self._left_eye_transform.Children.value.append(self._left_eye_iris)

        # pupil
        self._left_eye_pupil = None
        self._left_eye_pupil = _loader.create_geometry_from_file(
            "left_eye_pupil_geometry",
            "data/objects/glumb/glumb_eye3.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._left_eye_pupil.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0, 0.0, 0.0, 1.0)
        )
        self._left_eye_transform.Children.value.append(self._left_eye_pupil)

        # init right eye
        self._right_eye_transform = avango.gua.nodes.TransformNode(Name = "glumb_right_eye")
        self._right_eye_transform.Transform.value = avango.gua.make_trans_mat(1.0, 1.75, 0.0)
        self.node.Children.value.append(self._right_eye_transform)

        # outside
        self._right_eye_outside = _loader.create_geometry_from_file(
            "right_eye_outside_geometry",
            "data/objects/glumb/glumb_eye1.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._right_eye_outside.Material.value.set_uniform(
            "Color",
            _skin_tone
        )
        self._right_eye_transform.Children.value.append(self._right_eye_outside)

        # iris
        self._right_eye_iris = _loader.create_geometry_from_file(
            "right_eye_iris_geometry",
            "data/objects/glumb/glumb_eye2.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._right_eye_iris.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0, 1.0, 1.0, 1.0)
        )
        self._right_eye_transform.Children.value.append(self._right_eye_iris)

        # pupil
        self._right_eye_pupil = None
        self._right_eye_pupil = _loader.create_geometry_from_file(
            "right_eye_pupil_geometry",
            "data/objects/glumb/glumb_eye3.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self._right_eye_pupil.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0, 0.0, 0.0, 1.0)
        )        
        self._right_eye_transform.Children.value.append(self._right_eye_pupil)