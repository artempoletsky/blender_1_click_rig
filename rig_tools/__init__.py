bl_info = {
    "name": "Rig tools",
    "author": "Artem Poletsky",
    "version": (1, 1, 1),
    "blender": (2, 82, 0),
    "location": "",
    "description": "The collection of rig operators",
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

else:
    from . import preferences
    from .weight_paint_toggle import WeightPaintToggleOperator
    from .place_bone_to_vertex import PlaceBoneToVertexOperator
    from .merge_bones_with_vgroups import MergeBonesOperator
    from .clear_empty_bones import ClearEmptyBonesOperator
    from .rename_bones import RenameBonesOperator
    from .arrange_bones import ArrangeBonesOperator
    from .swap_bones_weights import SwapBonesWeightsOperator

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

    preferences.register_keymaps()
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(vertex_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(vertext_context_menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(vertex_menu_draw)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(vertext_context_menu_func)

    preferences.unregister_keymaps()

if __name__ == "__main__":
    register()
