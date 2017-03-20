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

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "player_geometry_GOID_"+str(self.get_num_game_objects()),
            "data/objects/sphere.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = OFFSET_MAT
        self.geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(1.0,0.0,0.0,1.0)
        )

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)

    @field_has_changed(sf_mat)
    def sf_mat_changed(self):
       ''' update transformation '''
       self.geometry.Transform.value = sf_mat.value * OFFSET_MAT