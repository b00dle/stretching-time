import avango
import avango.gua
import avango.script
from avango.script import field_has_changed 

from lib.game.GameObject import GameObject
import lib.game.Globals
import time

from lib.game.misc.Heart import Heart
from lib.game.misc.Ammo import Ammo

class Player(GameObject):
    ''' Defines game logicfor the player '''

    sf_mat = avango.gua.SFMatrix4()

    def __init__(self):
        self.super(Player).__init__()

    def my_constructor(self, PARENT_NODE=None, OFFSET_MAT=avango.gua.make_identity_mat(), MAX_LIFE_COUNT=1):
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # store offset mat, so that transformation update will factor it in
        self._offset_mat = OFFSET_MAT

        # create transform node positioned by sf_mat
        self.node = avango.gua.nodes.TransformNode(Name = "pointer_node")
        self.node.Transform.connect_from(self.sf_mat)
        # append to parent
        PARENT_NODE.Children.value.append(self.node)

        # add life visualizations
        if MAX_LIFE_COUNT <= 0:
            MAX_LIFE_COUNT = 1

        self._life_list = []
        for i in range(0, MAX_LIFE_COUNT):
            h = Heart()
            h.my_constructor(PARENT_NODE=self.node, NAME="life_"+str(i))
            x_step = 0.07
            h.node.Transform.value = avango.gua.make_trans_mat(-0.1+i*x_step, 0.15, 0) * \
                avango.gua.make_scale_mat(0.03,0.03,0.03)
            self._life_list.append(h)

        self._ammo_list = []

        # create geometry
        self.bounding_geometry = _loader.create_geometry_from_file(
            "player_geometry_GOID_"+str(self.get_num_game_objects()),
            "data/objects/frame.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.bounding_geometry.Transform.value = OFFSET_MAT
        self.bounding_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0,1.0,0.0,1.0)
        )
        # append to parent
        self.node.Children.value.append(self.bounding_geometry)

        self.sf_mat.value = avango.gua.make_identity_mat()

        self.name = 'Plunger Boy'

    def subtract_life(self):
        ''' subtracts a life from the player. 
            Returns False if player has no more lives to subtract.
            True otherwise. '''
        for h in self._life_list:
            if not h.is_dead():
                h.set_dead()
                return True
        return False

    def add_life(self):
        ''' subtracts a life from the player. 
            Returns False if player has no more lives to subtract.
            True otherwise. '''
        for h in reversed(self._life_list):
            if h.is_dead():
                h.set_dead(False)
                return True
        return False

    def has_max_life(self):
        for h in self._life_list:
            if h.is_dead():
                return False
        return True

    def add_ammo(self, COUNT=1):
        for i in range(len(self._ammo_list), len(self._ammo_list)+COUNT):
            a = Ammo()
            a.my_constructor(PARENT_NODE=self.node, NAME="ammo_"+str(i))
            x_step = 0.07
            a.node.Transform.value = avango.gua.make_trans_mat(-0.1+i*x_step, -0.15, 0) * \
                avango.gua.make_scale_mat(0.03,0.03,0.03)
            self._ammo_list.append(a)

    def subtract_ammo(self):
        ''' subtracts a pice of ammo from the player.
            Returns False if player has no more ammo to subtract.
            True otheriwse. '''
        if len(self._ammo_list) == 0:
            return False
        a = self._ammo_list[-1]
        a.node.Parent.value.Children.value.remove(a.node)
        self._ammo_list.remove(a)
        del a
        a = None
        return True

    def get_ammo(self):
        return len(self._ammo_list)

    def is_dead(self):
        ''' Returns True if all lives of the player have been used. '''
        for h in self._life_list:
            if not h.is_dead():
                return False
        return True

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
       pass#self.bounding_geometry.Transform.value = self.sf_mat.value * self._offset_mat