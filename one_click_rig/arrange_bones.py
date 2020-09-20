import bpy
from . import preferences

class ArrangeBonesOperator(bpy.types.Operator):
    """Tail to head"""
    bl_idname = "armature.arrange_bones"
    bl_label = "Arrange bones"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and context.object.mode == 'EDIT')

    def execute(self, context):
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        bones = context.selected_bones
        for bone in bones:
            parent = bone.parent
            if not parent:
                continue
            if len(parent.children) != 1:
                continue
            parent.tail = bone.head
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
