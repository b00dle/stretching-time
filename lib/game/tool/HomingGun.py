#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.GameObject import GameObject
from lib.game.controller.RadialSpawner import RadialSpawner
from lib.game.tool.HomingProjectile import HomingProjectile

import math

class HomingGun(GameObject):
    ''' a little support dude that fights for justice and survival. '''

    sf_gun_mat = avango.gua.SFMatrix4()
    sf_gun_trigger = avango.SFBool()

    def __init__(self):
        self.super(HomingGun).__init__()

        self._offset_mat = avango.gua.make_identity_mat()

        # ray used for picking homing target
        self.pick_ray = avango.gua.nodes.Ray()

        # length of picking target selection
        self.pick_length = 1.0

        # result of picking
        self.pick_result = None

        # tolerance distance for pick
        self.pick_angle_tolerance = 5.0

        # spawner spawning pickable objects
        self.target_spawner = None

        # geometry for visualizing picked object
        self.selection_geometry = None

        self.always_evaluate(True)

    def evaluate(self):
        self._calc_pick_result()
        if self.pick_result != None: # intersection found
            parent = self.selection_geometry.Parent.value
            if len(self.selection_geometry.Tags.value) == 0 and parent != self.pick_result.bounding_geometry:
                self.selection_geometry.Parent.value.Children.value.remove(self.selection_geometry)
            elif len(self.selection_geometry.Tags.value) != 0:
                self.selection_geometry.Tags.value = []
                self.pick_result.bounding_geometry.Children.value.append(self.selection_geometry)
        elif self.selection_geometry != None:
            parent = self.selection_geometry.Parent.value
            if parent != None:
                self.selection_geometry.Parent.value.Children.value.remove(self.selection_geometry)
                self.selection_geometry.Tags.value = ["invisible"]
        
        kill_bullets = []
        if self.projectile_spawner != None:
            for bullet_id in self.projectile_spawner.spawns_dict:
                bullet = self.projectile_spawner.spawns_dict[bullet_id]
                if bullet.target_missed:
                    kill_bullets.append(bullet_id)

        if len(kill_bullets) > 0:
            self.projectile_spawner.remove_spawns(kill_bullets) 

    def cleanup(self):
        ''' BC override. '''
        if self._barrel_exit_node != None:
            self._barrel_exit_node.Parent.value.Children.value.remove(self._barrel_exit_node)

        if self.selection_geometry != None:
            if self.selection_geometry.Parent.value != None:
                self.selection_geometry.Parent.value.Children.value.remove(self.selection_geometry)

        self.projectile_spawner.cleanup()

        sf_gun_mat.disconnect()
        sf_gun_trigger.disconnect()

        self.super(SwordDyrion).cleanup()

    def my_constructor(self,
                       PARENT_NODE,
                       SPAWN_PARENT,
                       TARGET_SPAWNER,
                       GEOMETRY_SIZE = 1.0):
        self.target_spawner = TARGET_SPAWNER

        t = avango.gua.Vec3(0.1,0,0)

        self._offset_mat = avango.gua.make_trans_mat(t) *\
            avango.gua.make_scale_mat(GEOMETRY_SIZE, GEOMETRY_SIZE, GEOMETRY_SIZE)
        
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.bounding_geometry = _loader.create_geometry_from_file(
            "homing_geometry_GOID_"+str(self.game_object_id),
            "data/objects/launcher/launcher.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS
        )
        self.bounding_geometry.Transform.value = self._offset_mat
        #self.bounding_geometry.Tags.value = ["invisible"]

        self._barrel_exit_node = avango.gua.nodes.TransformNode(
            Name = "homing_barrel_exit_GOID_"+str(self.game_object_id)
        )
        self._barrel_exit_node.Transform.value = avango.gua.make_trans_mat(0,0,-1.0)
        self.bounding_geometry.Children.value.append(self._barrel_exit_node)

        self.selection_geometry =  _loader.create_geometry_from_file(
            "homing_selection_geometry_GOID_"+str(self.game_object_id),
            "data/objects/frame.obj",
            avango.gua.LoaderFlags.DEFAULTS
        ) 
        self.selection_geometry.Material.value.set_uniform(
            "Color",
            avango.gua.Vec4(0.0,1.0,0.0,1.0)
        )
        self.selection_geometry.Tags.value = ["invisible"]

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)

        self.projectile_spawner = RadialSpawner()
        self.projectile_spawner.spawn_scale = 0.35
        self.projectile_spawner.my_constructor(
            PARENT_NODE = SPAWN_PARENT,
            VANISH_DISTANCE = 50.0
        )
        self.projectile_spawner.spawn_root.Transform.value = avango.gua.make_trans_mat(t)

    def _calc_pick_result(self):
        ''' selects homing target. '''
        if self.target_spawner == None:
            return None

        self.pick_result = None
        min_angle = 0
        tool_pos = self.bounding_geometry.WorldTransform.value.get_translate()
        for spawn_id in self.target_spawner.spawns_dict:
            spawn = self.target_spawner.spawns_dict[spawn_id]
            pos = spawn.bounding_geometry.WorldTransform.value.get_translate()
            dist = (pos - tool_pos).length()
            temp_angle = self._angle_to_ray(pos)
            if dist < self.pick_length and temp_angle < self.pick_angle_tolerance:
                if self.pick_result == None or temp_angle < min_angle:
                    min_angle = temp_angle
                    self.pick_result = spawn

    def _angle_to_ray(self, POS):
        ''' calculates the angle between vector of of pos to origin and direction of pointing. '''
        start = self.bounding_geometry.WorldTransform.value.get_translate()
        end = self._barrel_exit_node.WorldTransform.value.get_translate()
        direction = end - start
        direction.normalize()

        start_to_pos = POS - start
        start_to_pos.normalize()

        angle = math.degrees(math.acos(direction.dot(start_to_pos)))
        
        return angle

    def setGeometrySize(self, SIZE):
        ''' sets the size of the sword geometry. '''
        self._offset_mat = avango.gua.make_scale_mat(SIZE, SIZE, SIZE)
        self.sf_sword_mat_changed()

    def shoot(self):
        ''' spawns shooting projectile. '''
        if self.pick_result != None:
            spawn_pos = self.bounding_geometry.WorldTransform.value.get_translate()
            exit_pos = self._barrel_exit_node.WorldTransform.value.get_translate()
            movement_dir = exit_pos - spawn_pos
            movement_dir.normalize()

            projectile = HomingProjectile()
            projectile.my_constructor(
                PARENT_NODE = self.projectile_spawner.spawn_root,
                TARGET = self.pick_result,
                SPAWN_TRANSFORM = avango.gua.make_trans_mat(spawn_pos)
            )

            self.projectile_spawner.spawn(
                SPAWN_POS = spawn_pos,
                MOVEMENT_SPEED = 0.1,
                MOVEMENT_DIR = movement_dir,
                SPAWN_OBJ = projectile,
                AUTO_ROTATE = False
            )

    @field_has_changed(sf_gun_mat)
    def sf_sword_mat_changed(self):
        t = self.sf_gun_mat.value.get_translate() * 0.5
        t.z = min(0.0, t.z-1.0)
        m_t = avango.gua.make_trans_mat(t)
        m_r = avango.gua.make_rot_mat(self.sf_gun_mat.value.get_rotate())
        m = m_t * m_r
        self.bounding_geometry.Transform.value = m * self._offset_mat

    @field_has_changed(sf_gun_trigger)
    def sf_gun_trigger_changed(self):
        if self.sf_gun_trigger.value:
            self.shoot()