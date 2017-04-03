#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.GameObject import GameObject
from lib.game.controller.RadialSpawner import RadialSpawner

class PewPewGun(GameObject):
    ''' a little support dude that fights for justice and survival. '''

    sf_gun_mat = avango.gua.SFMatrix4()
    sf_gun_trigger = avango.SFBool()

    def __init__(self):
        self.super(PewPewGun).__init__()

        self._offset_mat = avango.gua.make_identity_mat()
        
        self.always_evaluate(False)

    def evaluate(self):
        pass

    def my_constructor(self,
                       PARENT_NODE,
                       SPAWN_PARENT,
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
        self.geometry.Tags.value = ["invisible"]

        self._barrel_exit_node = avango.gua.nodes.TransformNode(
            Name = "pewpew_barrel_exit_GOID_"+str(self.game_object_id)
        )
        self._barrel_exit_node.Transform.value = avango.gua.make_trans_mat(0,0,-1.0)
        self.geometry.Children.value.append(self._barrel_exit_node)

        # append to parent
        PARENT_NODE.Children.value.append(self.geometry)

        self.projectile_spawner = RadialSpawner()
        self.projectile_spawner.spawn_scale = 0.05
        self.projectile_spawner.my_constructor(
            PARENT_NODE = SPAWN_PARENT,
            VANISH_DISTANCE = 10.0
        )
        
    def setGeometrySize(self, SIZE):
        ''' sets the size of the sword geometry. '''
        self._offset_mat = avango.gua.make_scale_mat(SIZE, SIZE, SIZE)
        self.sf_sword_mat_changed()

    def shoot(self):
        ''' spawns shooting projectile. '''
        spawn_pos = self.geometry.WorldTransform.value.get_translate()
        exit_pos = self._barrel_exit_node.WorldTransform.value.get_translate()
        movement_dir = exit_pos - spawn_pos
        movement_dir.normalize()
        self.projectile_spawner.spawn(
            SPAWN_POS = spawn_pos,
            MOVEMENT_SPEED = 0.1,
            MOVEMENT_DIR = movement_dir
        )

    @field_has_changed(sf_gun_mat)
    def sf_sword_mat_changed(self):
        t = self.sf_gun_mat.value.get_translate() * 0.5
        t.z = min(0.0, t.z-1.0)
        m_t = avango.gua.make_trans_mat(t)
        m_r = avango.gua.make_rot_mat(self.sf_gun_mat.value.get_rotate())
        m = m_t * m_r
        self.geometry.Transform.value = m * self._offset_mat

    @field_has_changed(sf_gun_trigger)
    def sf_gun_trigger_changed(self):
        if self.sf_gun_trigger.value:
            self.shoot()