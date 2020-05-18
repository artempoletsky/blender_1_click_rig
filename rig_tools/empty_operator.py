import bpy
from . import preferences

class EmptyOperator(bpy.types.Operator):
    """Empty operator"""
    bl_idname = "object.empty_operator"
    bl_label = "Empty operator"
    bl_options = {'REGISTER', 'UNDO'}

    example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        self.prefs = preferences.get_prefs()

        self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
