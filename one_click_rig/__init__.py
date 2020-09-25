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
    WeightPaintToggleOperator = weight_paint_toggle.WeightPaintToggleOperator
    importlib.reload(place_bone_to_vertex)
    PlaceBoneToVertexOperator = place_bone_to_vertex.PlaceBoneToVertexOperator
    importlib.reload(merge_bones_with_vgroups)
    MergeBonesOperator = merge_bones_with_vgroups.MergeBonesOperator
    importlib.reload(clear_empty_bones)
    ClearEmptyBonesOperator = clear_empty_bones.ClearEmptyBonesOperator
    importlib.reload(rename_bones)
    RenameBonesOperator = rename_bones.RenameBonesOperator
    importlib.reload(arrange_bones)
    ArrangeBonesOperator = arrange_bones.ArrangeBonesOperator
    importlib.reload(swap_bones_weights)
    SwapBonesWeightsOperator = swap_bones_weights.SwapBonesWeightsOperator
    importlib.reload(generate_metarig)
    GenerateMetarigOperator = generate_metarig.GenerateMetarigOperator
    importlib.reload(bind_rig_to_armature)
    BindRigifyToArmatureOperator = bind_rig_to_armature.BindRigifyToArmatureOperator
    importlib.reload(convert_to_rigify)
    ConvertToRigifyOperator = convert_to_rigify.ConvertToRigifyOperator
    importlib.reload(retarget_animation)
    RetargetAnimationOperator = retarget_animation.RetargetAnimationOperator
    importlib.reload(reset_rigify)
    ResetRigifyOperator = reset_rigify.ResetRigifyOperator
    importlib.reload(add_unreal_skeleton)
    AddUnrealSkeletonOperator = add_unreal_skeleton.AddUnrealSkeletonOperator
    SaveSkeletonDataOperator = add_unreal_skeleton.SaveSkeletonDataOperator
    importlib.reload(panel)
    importlib.reload(mapping_editor)

else:
    from . import preferences
    from .weight_paint_toggle import WeightPaintToggleOperator
    from .place_bone_to_vertex import PlaceBoneToVertexOperator
    from .merge_bones_with_vgroups import MergeBonesOperator
    from .clear_empty_bones import ClearEmptyBonesOperator
    from .rename_bones import RenameBonesOperator
    from .arrange_bones import ArrangeBonesOperator
    from .swap_bones_weights import SwapBonesWeightsOperator
    from .generate_metarig import GenerateMetarigOperator
    from .bind_rig_to_armature import BindRigifyToArmatureOperator
    from .convert_to_rigify import ConvertToRigifyOperator
    from .retarget_animation import RetargetAnimationOperator
    from .reset_rigify import ResetRigifyOperator
    from .add_unreal_skeleton import AddUnrealSkeletonOperator, SaveSkeletonDataOperator
    from . import panel
    from . import mapping_editor

import bpy

classes = (
    # preferences.RigToolsPreferences,
    # preferences.BoilerplatePreferencesAddKeymapOperator,
    WeightPaintToggleOperator,
    PlaceBoneToVertexOperator,
    MergeBonesOperator,
    ClearEmptyBonesOperator,
    RenameBonesOperator,
    ArrangeBonesOperator,
    SwapBonesWeightsOperator,
    GenerateMetarigOperator,
    BindRigifyToArmatureOperator,
    ConvertToRigifyOperator,
    RetargetAnimationOperator,
    ResetRigifyOperator,
    AddUnrealSkeletonOperator,
    SaveSkeletonDataOperator,
    panel.OCR_PT_OcrPanel,
    mapping_editor.MappingEntry,
    mapping_editor.MappingEditorOperator,
    mapping_editor.OCR_PT_BoneMappingsPanel,
    mapping_editor.OCRMappingPanelProps,
    mapping_editor.MappingRemoveEntryOperator,
    mapping_editor.MappingAddEntryOperator,
    mapping_editor.SaveMappingOperator,
    mapping_editor.RemoveMappingOperator,
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
