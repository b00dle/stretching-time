#!/usr/bin/python

### import guacamole libraries
import avango
import avango.gua

from lib.game.misc.Glumb import Glumb

class Scene:

    ## constructor
    def __init__(self,
        PARENT_NODE = None,
        ):

        ### variables ###
        self.box_list = []

        ### resources ###

        ## init scene light
        self.scene_light = avango.gua.nodes.LightNode(Name = "scene_light", Type = avango.gua.LightType.POINT)
        self.scene_light.Color.value = avango.gua.Color(0.9, 0.9, 0.9)
        self.scene_light.Brightness.value = 15.0
        self.scene_light.Falloff.value = 1.0 # exponent
        self.scene_light.EnableShadows.value = True
        self.scene_light.ShadowMapSize.value = 1024
        self.scene_light.Transform.value = \
            avango.gua.make_trans_mat(0.0, 0.5, 0.0) * \
            avango.gua.make_rot_mat(-90.0, 1, 0, 0) * \
            avango.gua.make_scale_mat(1.0)
        self.scene_light.ShadowNearClippingInSunDirection.value = 0.1
        PARENT_NODE.Children.value.append(self.scene_light)


        ## init scene geometries       
        _loader = avango.gua.nodes.TriMeshLoader() # get trimesh loader to load external meshes

        '''
        self.glumb_mouth = _loader.create_geometry_from_file(
            "glumb_mouth_geometry",
            "data/objects/glumb/basti.fbx",
            avango.gua.LoaderFlags.DEFAULTS
        )

        #self.glumb_mouth.Children.value[1].Material.value.set_uniform(
        #    "ColorMap", "data/objects/glumb/Thing_Eyes.png"
        #)

        
        self.glumb_mouth.Transform.value = avango.gua.make_trans_mat(0,0,-70) * \
            avango.gua.make_rot_mat(0,0,1,0) * \
            avango.gua.make_scale_mat(5,5,5)
        '''

        self.glumb = Glumb()
        self.glumb.my_constructor(PARENT_NODE)
        self.glumb.node.Transform.value = avango.gua.make_trans_mat(0,0,-30) * \
            avango.gua.make_scale_mat(5,5,5)

        '''
        ## init ground
        self.ground_geometry = _loader.create_geometry_from_file("ground_geometry", "data/objects/cube.obj", avango.gua.LoaderFlags.DEFAULTS)
        self.ground_geometry.Transform.value = \
            avango.gua.make_trans_mat(0.0, -0.105, 0.0) * \
            avango.gua.make_scale_mat(0.5, 0.01, 0.5)
        self.ground_geometry.Material.value.set_uniform("ColorMap", "data/textures/ground/bricks_diffuse.jpg")
        self.ground_geometry.Material.value.set_uniform("NormalMap", "data/textures/ground/bricks_normal.jpg")
        PARENT_NODE.Children.value.append(self.ground_geometry)
        '''