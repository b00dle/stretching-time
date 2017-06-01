#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script
from avango.script import field_has_changed

from lib.game.GameObject import GameObject

class Hand(GameObject):
    ''' a little support dude that fights for justice and survival. '''

    sf_hand_mat = avango.gua.SFMatrix4()
    sf_grab_trigger = avango.SFBool()
    sf_object_grabbed = avango.SFBool()

    def __init__(self):
        self.super(Hand).__init__()

        self._offset_mat = avango.gua.make_identity_mat()

        self.sf_object_grabbed.value = False

        # spawner spawning pickable objects
        self.target_spawner = None
        
        self.always_evaluate(False)

    def evaluate(self):
        pass

    def cleanup(self):
        ''' BC override. '''
        sf_hand_mat.disconnect()

        self.super(Hand).cleanup()

    def my_constructor(self,
                       PARENT_NODE,
                       TARGET_SPAWNER,
                       GEOMETRY_SIZE = 1.0):
        self._offset_mat = avango.gua.make_scale_mat(GEOMETRY_SIZE, GEOMETRY_SIZE, GEOMETRY_SIZE)
        self.target_spawner = TARGET_SPAWNER
        
        # get trimesh loader to load external tri-meshes
        _loader = avango.gua.nodes.TriMeshLoader()

        # create geometry
        self.bounding_geometry = _loader.create_geometry_from_file(
            "hand_geometry_GOID_"+str(self.game_object_id),
            "data/objects/hand.obj",
            avango.gua.LoaderFlags.DEFAULTS | avango.gua.LoaderFlags.LOAD_MATERIALS 
        )
        self.bounding_geometry.Transform.value = self._offset_mat

        # append to parent
        PARENT_NODE.Children.value.append(self.bounding_geometry)

    def _calc_pick_result(self):
        ''' selects homing target. '''
        self.pick_result = None
        
        if self.target_spawner == None:
            return None

        min_angle = 0
        for spawn_id in self.target_spawner.spawns_dict:
            spawn = self.target_spawner.spawns_dict[spawn_id]
            if self.intersects(spawn.get_bounding_box()):
                self.pick_result = spawn_id
                return

    def grab(self):
        ''' intersects bounding box with objects in scene. '''
        self._calc_pick_result()
        if self.pick_result != None:
            self.sf_object_grabbed.value = True
            print ("grabbed object GOID" + str(self.pick_result))

    def setGeometrySize(self, SIZE):
        ''' sets the size of the sword geometry. '''
        self._offset_mat = avango.gua.make_scale_mat(SIZE, SIZE, SIZE)
        self.sf_hand_mat_changed()

    @field_has_changed(sf_hand_mat)
    def sf_hand_mat_changed(self):
        t = self.sf_hand_mat.value.get_translate() * 0.5
        t.z = min(0.0, t.z-1.0)
        m_t = avango.gua.make_trans_mat(t)
        m_r = avango.gua.make_rot_mat(self.sf_hand_mat.value.get_rotate())
        m = m_t * m_r
        self.bounding_geometry.Transform.value = m * self._offset_mat

    @field_has_changed(sf_grab_trigger)
    def sf_grab_trigger_changed(self):
        if self.sf_grab_trigger.value:
            self.grab()
            self.set_active(False)
        else:
            self.set_active(True)