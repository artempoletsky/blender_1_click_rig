import bpy
from . import preferences

oops = bpy.ops.object
pops = bpy.ops.pose

class ConvertToRigifyOperator(bpy.types.Operator):
    """Convert character to rigify"""
    bl_idname = "object.convert_to_rigify"
    bl_label = "Convert UE character to rigify"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'OBJECT'))

    def execute(self, context):
        armature_object = context.object
        parent = armature_object.parent
        mesh_object = armature_object.children[0]
        if parent:
            parent.select_set(True)
        mesh_object.select_set(True)

        oops.transform_apply(location = True, rotation = True, scale = True)
        if parent:
            parent.select_set(False)
        mesh_object.select_set(False)
        oops.ap_rig_tools_generate_metarig()
        metarig = context.object
        oops.mode_set(mode = 'OBJECT')
        pops.rigify_generate()
        armature_object.select_set(True)
        oops.bind_rigify_to_armature()

        objs = bpy.data.objects

        objs.remove(armature_object)
        objs.remove(metarig)
        if parent:
            objs.remove(parent)
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
