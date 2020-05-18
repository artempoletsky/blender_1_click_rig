import bpy
from . import preferences

def find_armature(obj):
    mods = obj.modifiers
    armature = None
    for m in mods:
        if m.type == 'ARMATURE' and m.object:
            armature = m.object
    return armature

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

    def execute(self, context):
        self.prefs = preferences.get_prefs()

        self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
