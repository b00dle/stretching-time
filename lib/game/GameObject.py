import avango
import avango.gua
import avango.script

class GameObject(avango.script.Script):
    ''' Defines base interface for all visualizable objects in the game. '''

    instance_count = 0

    def __init__(self):
        self.super(GameObject).__init__()

        # stores an avango.gua.nodes.TrimeshNode to visualize instance 
        self.geometry = None
        
        # stores a reference id to this instance
        self.game_object_id = GameObject.instance_count

        GameObject.instance_count += 1

        # flag stating whether the object has just been spawned
        # solves bug of intersecting just spawned objects,
        # which do not have their transformation applied yet
        self._just_spawned = True 

        # flag stating whether this instance can trigger collision
        self.can_trigger_collision = True

        self.always_evaluate(True)

    def evaluate(self):
        ''' Frame based update function. '''
        if self._just_spawned:
            self._just_spawned = False

    def get_just_spawned(self):
        ''' getter for self._just_spawned. '''
        return self._just_spawned 

    def get_bounding_box(self):
        ''' returns the bounding box of the game object geometry. '''
        return self.geometry.BoundingBox.value

    def is_collision_trigger(self):
        ''' returns true if can_trigger_collision == True,
            and self._just_spawned == False. '''
        return self.can_trigger_collision and not self._just_spawned

    def intersects(self, BOUNDING_BOX):
        ''' Checks if given bounding box intersects 
            the player geometries bounding box. '''
        return self.get_bounding_box().intersects(BOUNDING_BOX)

    def get_num_game_objects(self):
        return GameObject.instance_count