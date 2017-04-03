#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.GameObject import GameObject

class SwordDyrion(GameObject):
    ''' a little support dude that fights for justice and survival. '''

    sf_sword_mat = avango.gua.SFMatrix4()

    def __init__(self):
        self.super(SwordDyrion).__init__()

        self._offset_mat = avango.gua.make_identity_mat()
        
        self.always_evaluate(False)

    def evaluate(self):
        pass

    def my_constructor(self,
                       PARENT_NODE = None,
                       GEOMETRY_SIZE = 1.0):
        self._offset_mat = avango.gua.make_scale_mat(GEOMETRY_SIZE, GEOMETRY_SIZE, GEOMETRY_SIZE)
        
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.geometry = _loader.create_geometry_from_file(
            "sword_dyrion_geometry_GOID_"+str(self.game_object_id),
            "data/objects/plunger_op.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.geometry.Transform.value = self._offset_mat

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)

        self.hit_box = _loader.create_geometry_from_file(
            "sword_hit_geometry_GOID_"+str(self.game_object_id),
            "data/objects/cube.obj",
            avango.gua.LoaderFlags.DEFAULTS
        )
        self.hit_box.Transform.value = avango.gua.make_trans_mat(0,0,-0.95) * avango.gua.make_scale_mat(0.18,0.18,0.08)
        self.hit_box.Tags.value = ["invisible"]
        self.geometry.Children.value.append(self.hit_box)

    def get_bounding_box(self):
        ''' BC override to returns hit box of hit_box geometry. '''
        return self.hit_box.BoundingBox.value

    def setGeometrySize(self, SIZE):
        ''' sets the size of the sword geometry. '''
        self._offset_mat = avango.gua.make_scale_mat(SIZE, SIZE, SIZE)
        self.sf_sword_mat_changed()

    @field_has_changed(sf_sword_mat)
    def sf_sword_mat_changed(self):
        t = self.sf_sword_mat.value.get_translate() * 0.5
        t.z = min(0.0, t.z-1.0)
        m_t = avango.gua.make_trans_mat(t)
        m_r = avango.gua.make_rot_mat(self.sf_sword_mat.value.get_rotate())
        m = m_t * m_r
        self.geometry.Transform.value = m * self._offset_mat