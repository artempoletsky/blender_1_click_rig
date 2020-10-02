import bpy

pops = bpy.ops.pose
anops = bpy.ops.anim

class AddKeyFrameOperator(bpy.types.Operator):
    """Add keyframe to retargeted animation"""
    bl_idname = "anim.ocr_add_keyframe"
    bl_label = "(OCR) add keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.object.mode == 'POSE')

    def execute(self, context):
        pops.visual_transform_apply()
        anops.keyframe_insert_menu(type = 'LocRotScale')
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
