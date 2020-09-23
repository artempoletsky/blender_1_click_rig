import bpy

class OCR_PT_OcrPanel(bpy.types.Panel):
    """
    Addon panel
    """
    bl_label = '1 click rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rigify'

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Converting to Rigify operators:")
        row = col.row()
        row.operator("object.ocr_convert_to_rigify")

        col.separator()
        row = col.row()
        row.operator("object.ocr_generate_metarig")
        row = col.row()
        row.operator("pose.rigify_generate", text="Generate Rig", icon='POSE_HLT')
        row = col.row()
        row.operator("object.ocr_bind_rigify_to_armature")
        #
        #
        col.label(text="Converting from Rigify operators:")

        row = col.row()
        row.operator("object.ocr_add_unreal_skeleton")
        row = col.row()
        row.operator("object.ocr_reset_rigify")

        col.label(text = "Animation")

        row = col.row()
        row.operator("object.ocr_retarget_animation", text = 'Retarget animation')
