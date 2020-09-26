bl_info = {
    "name": "1 click rig",
    "author": "Artem Poletsky",
    "version": (1, 3, 1),
    "blender": (2, 82, 0),
    "location": "",
    "description": "A collection of rig operators",
    "warning": "",
    "wiki_url": "",
    "category": "Rigging",
}

if "bpy" in locals():
    import importlib
    importlib.reload(preferences)
    importlib.reload(weight_paint_toggle)
    importlib.reload(place_bone_to_vertex)
    importlib.reload(merge_bones_with_vgroups)
    importlib.reload(clear_empty_bones)
    importlib.reload(arrange_bones)
    importlib.reload(swap_bones_weights)
    importlib.reload(generate_metarig)
    importlib.reload(bind_rig_to_armature)
    importlib.reload(convert_to_rigify)
    importlib.reload(retarget_animation)
    importlib.reload(reset_rigify)
    importlib.reload(add_unreal_skeleton)
    importlib.reload(panel)
    importlib.reload(mapping_editor)
    importlib.reload(pose_character)
    importlib.reload(templates)

else:
    from . import preferences
    from . import weight_paint_toggle
    from . import place_bone_to_vertex
    from . import merge_bones_with_vgroups
    from . import clear_empty_bones
    from . import arrange_bones
    from . import swap_bones_weights
    from . import generate_metarig
    from . import bind_rig_to_armature
    from . import convert_to_rigify
    from . import retarget_animation
    from . import reset_rigify
    from . import add_unreal_skeleton
    from . import panel
    from . import mapping_editor
    from . import pose_character
    from . import templates

import bpy

classes = (
    # preferences.RigToolsPreferences,
    # preferences.BoilerplatePreferencesAddKeymapOperator,
    weight_paint_toggle.WeightPaintToggleOperator,
    place_bone_to_vertex.PlaceBoneToVertexOperator,
    merge_bones_with_vgroups.MergeBonesOperator,
    clear_empty_bones.ClearEmptyBonesOperator,
    arrange_bones.ArrangeBonesOperator,
    swap_bones_weights.SwapBonesWeightsOperator,
    generate_metarig.GenerateMetarigOperator,
    bind_rig_to_armature.BindRigifyToArmatureOperator,
    convert_to_rigify.ConvertToRigifyOperator,
    convert_to_rigify.ConvertToRigifyByMappingOperator,
    retarget_animation.RetargetAnimationOperator,
    reset_rigify.ResetRigifyOperator,
    add_unreal_skeleton.AddUnrealSkeletonOperator,
    templates.SaveSkeletonDataOperator,
    panel.OCR_PT_OcrPanel,
    mapping_editor.MappingEntry,
    mapping_editor.CreateMappingOperator,
    mapping_editor.OCR_PT_BoneMappingsPanel,
    mapping_editor.OCRMappingPanelProps,
    mapping_editor.MappingRemoveEntryOperator,
    mapping_editor.MappingAddEntryOperator,
    mapping_editor.SaveMappingOperator,
    mapping_editor.RemoveMappingOperator,
    mapping_editor.RenameArmatureOperator,
    mapping_editor.AddPrefixOperator,
    mapping_editor.RemovePrefixOperator,
    pose_character.PoseCharacterOperator,
    pose_character.SavePoseOperator,

)

def vertex_menu_draw(self, context):
    layout = self.layout
    if PlaceBoneToVertexOperator.poll(context):
        layout.separator()
        layout.operator_context = "INVOKE_DEFAULT"
        layout.operator(PlaceBoneToVertexOperator.bl_idname, text = PlaceBoneToVertexOperator.bl_label)

def vertext_context_menu_func(self, context):
    if tuple(context.scene.tool_settings.mesh_select_mode) != (True, False, False):
        return
    vertex_menu_draw(self, context)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # version = ".".join(str(x) for x in bl_info["version"])

    bpy.types.WindowManager.one_click_rig_ui = bpy.props.PointerProperty(type = mapping_editor.OCRMappingPanelProps)
    preferences.register_keymaps()
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(vertex_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(vertext_context_menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(vertex_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(vertext_context_menu_func)

    del bpy.types.WindowManager.one_click_rig_version
    preferences.unregister_keymaps()

if __name__ == "__main__":
    register()
