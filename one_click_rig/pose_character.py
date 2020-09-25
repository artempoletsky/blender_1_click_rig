import bpy
from . import preferences
from . import map_bones

class PoseCharacterOperator(bpy.types.Operator):
    """Empty operator"""
    bl_idname = "pose.ocr_pose_character"
    bl_label = "Pose character to mannequin pose"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.view_layer.objects.active.type == 'ARMATURE'
            )

    def execute(self, context):
        rig = context.view_layer.objects.active
        mapping = map_bones.load_mapping('rigify_uemannequin', anim = True)
        
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
