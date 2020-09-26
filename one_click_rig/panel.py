import bpy

class OCR_PT_OcrPanel(bpy.types.Panel):
    """
    Addon panel
    """
    bl_label = '1 click rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rigify'

    def draw_object(self, col, context):
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
        ui = context.window_manager.one_click_rig_ui
        col.separator()
        row = col.row()
        row.prop(ui, 'active_mapping', text = '')
        row.operator('object.ocr_convert_to_rigify_by_mapping', text = 'Convert char by mapping')

        #
        #
        col.separator()
        col.label(text="Converting from Rigify operators:")

        row = col.row()
        row.operator("pose.ocr_pose_character")
        row = col.row()
        row.operator("object.ocr_add_unreal_skeleton")
        row = col.row()
        row.operator("object.ocr_reset_rigify")

        col.label(text = "Animation")

        row = col.row()
        row.operator("object.ocr_retarget_animation", text = 'Retarget animation')

    def draw_edit(self, col, context):
        col.label(text="Armature editing operators:")
        row = col.row()
        row.operator("armature.ocr_arrange_bones")

        row = col.row()
        row.operator("armature.ocr_clear_empty_bones")

        row = col.row()
        row.operator("armature.ocr_swap_bones_weights")

        row = col.row()
        row.operator("armature.ocr_merge_bones_with_vgroups")

    def draw_pose(self, col, context):
        col.label(text="Armature editing operators:")

        row = col.row()
        row.operator("armature.ocr_swap_bones_weights")

        row = col.row()
        row.operator("armature.ocr_merge_bones_with_vgroups")

    def draw(self, context):
        if not context.object:
            return
        layout = self.layout
        col = layout.column()
        mode = context.object.mode
        if mode == 'OBJECT':
            self.draw_object(col, context)
        elif mode == 'EDIT':
            self.draw_edit(col, context)
        elif mode == 'POSE':
            self.draw_pose(col, context)
