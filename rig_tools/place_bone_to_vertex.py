import bpy
from . import preferences
from functools import cmp_to_key
import bmesh

def find_armature(obj):
    mods = obj.modifiers
    armature = None
    for m in mods:
        if m.type == 'ARMATURE' and m.object:
            armature = m.object
    return armature

def place_bone_to_vert_pair(bone, v1, v2):
    bone.head = v1
    bone.tail = v2

def place_bone_to_vert(bone, vert, orientation = 'NORMAL'):
    return

def bone_distance_to_vert_pair(bone, v1, v2):
    d1 = (bone.head - v1).length
    d2 = (bone.tail - v2).length
    d3 = (bone.head - v2).length
    d4 = (bone.tail - v1).length
    return min(d1 + d2, d3 + d4)

def default_comparator(n1, n2):
    if n1 == n2:
        return 0
    elif n1 > n2:
        return 1
    else:
        return -1

def sort_closest_bones(bones, v1, v2):
    if not v2:
        return bones

    def comparator(b1, b2):
        return default_comparator(bone_distance_to_vert_pair(b1, v1, v2), bone_distance_to_vert_pair(b2, v1, v2))

    return sorted(bones, key = cmp_to_key(comparator), reverse = False)


oops = bpy.ops.object
armops = bpy.ops.armature

class PlaceBoneToVertexOperator(bpy.types.Operator):
    """Place bone to vertex"""
    bl_idname = "mesh.place_bone_to_vertex"
    bl_label = "Place bone to vertex"
    bl_options = {'REGISTER', 'UNDO'}

    example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        is_valid_edit_mode = (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'EDIT')
        if not is_valid_edit_mode:
            return False
        obj = context.view_layer.objects.active
        return bool(find_armature(obj))

    def select_armature(self, context):
        oops.editmode_toggle()
        context.view_layer.objects.active = self.armature
        oops.editmode_toggle()

    def select_object(self, context):
        oops.editmode_toggle()
        context.view_layer.objects.active = self.object
        oops.editmode_toggle()

    def execute(self, context):
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        self.object = obj = context.object
        mesh = obj.data
        armature = self.armature = find_armature(obj)

        bm = bmesh.from_edit_mesh(mesh)
        selected_verts = [v.co for v in bm.verts if v.select]

        if len(selected_verts) == 2:
            v1, v2 = selected_verts
            self.select_armature(context)
            bones = self.armature.data.edit_bones
            sorted_bones = sort_closest_bones(bones, v1, v2)
            bone_name = sorted_bones[0].name
            edit_bones = armature.data.edit_bones
            place_bone_to_vert_pair(edit_bones[bone_name], v1, v2)
            self.select_object(context)
        bm.free()
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
