import bpy
from . import preferences
from . import bone_functions as b_fun

class SwapBonesWeightsOperator(bpy.types.Operator):
    """Swap bones weights"""
    bl_idname = "armature.ocr_swap_bones_weights"
    bl_label = "Swap bones weights"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        mode = context.object.mode
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and mode == 'EDIT' and len(context.selected_bones) == 2 or mode == 'POSE' and len(context.selected_pose_bones) == 2
            )

    def execute(self, context):
        bones = context.selected_bones if context.object.mode  == 'EDIT' else context.selected_pose_bones
        # print(bones)
        b_fun.swap_childrens_vgroups_names(context.object, bones[0].name, bones[1].name)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
