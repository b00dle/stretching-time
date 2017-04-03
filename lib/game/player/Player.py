import avango
import avango.gua
import avango.script
from avango.script import field_has_changed 

from lib.game.GameObject import GameObject
import lib.game.Globals
import time

class Player(GameObject):
    ''' Defines game logicfor the player '''

    sf_mat = avango.gua.SFMatrix4()

    def __init__(self):
        self.super(Player).__init__()

    def my_constructor(self, PARENT_NODE=None, OFFSET_MAT=avango.gua.make_identity_mat()):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # store offset mat, so that transformation update will factor it in
        self._offset_mat = OFFSET_MAT

        # create transform node positioned by sf_mat
        self.node = avango.gua.nodes.TransformNode(Name = "pointer_node")
        self.node.Transform.connect_from(self.sf_mat)
        # append to parent
        PARENT_NODE.Children.value.append(self.node)

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "player_geometry_GOID_"+str(self.get_num_game_objects()),
            "data/objects/frame.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = OFFSET_MAT
        self.geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0,0.0,0.0,1.0)
        )
        # append to parent
        self.node.Children.value.append(self.geometry)

        self.sf_mat.value = avango.gua.make_identity_mat()

    def move(self, TRANSLATE):
        ''' moves the player by defined traslation. '''
        self.sf_mat.value = avango.gua.make_trans_mat(TRANSLATE) * \
            self.sf_mat.value

    def set_position(self, POS):
        ''' Sets position of player according to given position. '''
        old_m = self.sf_mat.value
        rot = old_m.get_rotate()
        sca = old_m.get_scale()
        self.sf_mat.value = avango.gua.make_trans_mat(POS) * \
            avango.gua.make_rot_mat(rot) * \
            avango.gua.make_scale_mat(sca)
        
    def set_rotate(self, ROT):
        ''' Sets rotation of player to given rotation. '''
        old_m = self.sf_mat.value
        pos = old_m.get_translate()
        sca = old_m.get_scale()
        self.sf_mat.value = avango.gua.make_trans_mat(pos) * \
            avango.gua.make_rot_mat(ROT) * \
            avango.gua.make_scale_mat(sca)

    def set_scale(self, SCA):
        ''' Sets scale of player to given scale. '''
        old_m = self.sf_mat.value
        pos = old_m.get_translate()
        rot = old_m.get_rotate()
        self.sf_mat.value = avango.gua.make_trans_mat(pos) * \
            avango.gua.make_rot_mat(rot) * \
            avango.gua.make_scale_mat(SCA)

    def set_transform(self, POS, ROT=None, SCA=None):
        ''' Sets transformation according to given position, rotation and scale. '''
        sca = SCA
        if sca == None:
            sca = self.sf_mat.value.get_scale()
        rot = ROT
        if rot == None:
            rot = self.sf_mat.value.get_rotate()

        self.sf_mat.value = avango.gua.make_trans_mat(POS) * \
            avango.gua.make_rot_mat(rot) * \
            avango.gua.make_scale_mat(sca)

    @field_has_changed(sf_mat)
    def sf_mat_changed(self):
       ''' update transformation '''
       pass#self.geometry.Transform.value = self.sf_mat.value * self._offset_mat