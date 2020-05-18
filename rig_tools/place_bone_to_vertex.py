import bpy
from . import preferences

class PlaceBoneToVertexOperator(bpy.types.Operator):
    """Place bone to vertex"""
    bl_idname = "mesh.place_bone_to_vertex"
    bl_label = "Place bone to vertex"
    bl_options = {'REGISTER', 'UNDO'}

    example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'EDIT')

    def execute(self, context):
        self.prefs = preferences.get_prefs()

        self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
