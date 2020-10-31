import bpy


class SetUESceneSettingsOperator(bpy.types.Operator):
    """Set UE scene settings"""
    bl_idname = "object.ocr_set_ue_scene_settings"
    bl_label = "Set UE settings"
    bl_options = {'REGISTER', 'UNDO'}
    #
    # @classmethod
    # def poll(cls, context):
    #     return (context.space_data.type == 'VIEW_3D')

    def execute(self, context):
        context.scene.unit_settings.scale_length = 0.01
        context.scene.render.fps = 30
        return {'FINISHED'}


class OCR_PT_AnimationPanel(bpy.types.Panel):
    """
    Animation panel
    """
    bl_label = '1 click rig. Animation edit'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'POSE'))


    def draw(self, context):
        col = self.layout.column()
        col.operator("anim.ocr_add_keyframe", text = 'Add keyframe')
        col.operator("pose.constraints_clear", text = 'Clear constraints')
        col.operator("nla.bake")
        col.operator_context = 'INVOKE_DEFAULT'



class OCR_PT_OcrPanel(bpy.types.Panel):
    """
    Addon panel
    """
    bl_label = '1 click rig'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Rigify'

    def draw_object(self, col, context):
        # col.separator()

        if context.object.type == 'ARMATURE':
            col.label(text = 'Armature appearance:')
            row = col.row()
            arm = context.object.data
            # row.prop(arm, "show_names", text="Names")
            row.prop(arm, "show_axes", text="Axes")
            row.prop(context.object, "show_in_front", text="In Front")
        col.separator()

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
        # row = col.row()
        col.label(text = 'Active mapping:')
        col.prop(ui, 'active_mapping', text = '')
        col.operator('object.ocr_convert_to_rigify_by_mapping', text = 'Convert char by mapping')

        col.separator()
        row = col.row()
        row.operator("armature.ocr_rename_armature")
        row.prop(ui, 'rename_reverse')
        col.separator()
        row = col.row()
        row.operator("armature.ocr_add_prefix")
        row.operator("armature.ocr_remove_prefix")

        #
        #
        col.separator()
        col.label(text="Converting from Rigify operators:")

        row = col.row()
        row.operator("pose.ocr_pose_character")
        row = col.row()
        row.operator("pose.ocr_apply_pose", text = "Apply pose")
        row = col.row()
        row.operator("object.ocr_add_unreal_skeleton")
        row = col.row()
        row.operator("object.ocr_reset_rigify")
        row = col.row()
        row.operator("object.ocr_apply_scale_rigify")
        # row = col.row()
        # row.operator("armature.ocr_fix_twist_bones")
        # row.operator("armature.ocr_unfix_twist_bones")
        # row = col.row()
        # row.operator("armature.ocr_fix_twist_constraints")


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

    def draw_scene(self, col, context):
        col.label(text = 'Scene settings:')
        row = col.row()
        row.prop(context.scene.unit_settings, "scale_length")
        row.prop(context.scene.render, "fps")
        col.operator('object.ocr_set_ue_scene_settings')

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if not context.object:
            self.draw_scene(col, context)
            return

        mode = context.object.mode
        if mode == 'OBJECT':
            self.draw_scene(col, context)
            self.draw_object(col, context)
        elif mode == 'EDIT':
            self.draw_edit(col, context)
        elif mode == 'POSE':
            self.draw_pose(col, context)
