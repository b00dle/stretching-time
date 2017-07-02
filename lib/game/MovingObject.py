#!/usr/bin/python

# import guacamole libraries
import avango
import avango.gua
import avango.script

from lib.game.GameObject import GameObject
import lib.game.Globals
import time

class MovingObject(GameObject):
    ''' Defines base interface for all GameObjects which automatically move. '''

    def __init__(self):
        self.super(MovingObject).__init__()

        # stores a direction for movement animation
        self.movement_dir = avango.gua.Vec3(0,0,1)

        # stores a rotation axis for rotation animation
        self.rotation_axis = avango.gua.Vec3(0,1,0)

        # stores speed factor for movement (direction units per second)
        self.movement_speed = 1.0

        # stores a speed factor for rotation animation
        self.rotation_speed = 1.0

        # flag stating whether this instance can move or not
        self.can_move = True

        # time since last update
        self._lf_time = None
        self._elapsed = None

    def evaluate(self):
        ''' Frame based update function. '''
        self.super(MovingObject).evaluate()

        self._calc_frame_times()
        
        if self.bounding_geometry == None:
            return

        if self.can_move:
            self._move()

    def _move(self):
        ''' calculates movement update. '''
        # compute translation
        t = self.movement_dir * \
            self.movement_speed * \
            lib.game.Globals.TIME_FACTOR * \
            self._get_fps_scale()

        # compute rotation angle
        a = self.rotation_speed * \
            lib.game.Globals.TIME_FACTOR * \
            self._get_fps_scale()

        # create transformation matrix (global)
        m = avango.gua.make_trans_mat(t.x, t.y, t.z) * \
            self.bounding_geometry.WorldTransform.value * \
            avango.gua.make_rot_mat(a, self.rotation_axis.x, self.rotation_axis.y, self.rotation_axis.z)
        
        # apply transformation update (transformation update - local)
        if self.bounding_geometry.Parent.value != None:
            self.bounding_geometry.Transform.value = avango.gua.make_inverse_mat(self.bounding_geometry.Parent.value.WorldTransform.value) * m

    def setScale(self, SCALE):
        ''' applies given uniform scale factor to geometry. '''
        t = self.bounding_geometry.Transform.value.get_translate()
        r = self.bounding_geometry.Transform.value.get_rotate()
        self.bounding_geometry.Transform.value = avango.gua.make_trans_mat(t.x, t.y, t.z) * \
            avango.gua.make_scale_mat(SCALE, SCALE, SCALE) * \
            avango.gua.make_rot_mat(r)

    def get_scale(self):
        ''' returns the scale component of the boudning_geometries Transform property. '''
        return self.bounding_geometry.Transform.value.get_scale()

    def _get_fps_scale(self):
        ''' returns a scale factor based on time elapsed since last frame. '''
        return self._elapsed / (1.0/60.0)

    def _calc_frame_times(self):
        ''' calculates elapsed time and stores time of frame. '''
        if self._elapsed == None or self._lf_time == None:
            self._elapsed = 0.0
            self._lf_time = time.time()
        else:
            curr_time = time.time()
            self._elapsed = curr_time - self._lf_time
            self._lf_time = curr_time
