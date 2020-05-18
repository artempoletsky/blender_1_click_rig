bl_info = {
    "name": "Rig tools",
    "author": "Artem Poletsky",
    "version": (1, 0, 0),
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

else:
    from . import preferences
    from .weight_paint_toggle import WeightPaintToggleOperator

import bpy

classes = (
    # preferences.RigToolsPreferences,
    # preferences.BoilerplatePreferencesAddKeymapOperator,
    WeightPaintToggleOperator,
)

def menu_func(self, context):
    layout = self.layout
    layout.separator()
    layout.operator_context = "INVOKE_DEFAULT"
    layout.operator(WeightPaintToggleOperator.bl_idname, text = WeightPaintToggleOperator.bl_label)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    preferences.register_keymaps()
    # bpy.types.VIEW3D_MT_object_context_menu.append(menu_func)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    # bpy.types.VIEW3D_MT_object_context_menu.remove(menu_func)

    preferences.unregister_keymaps()

if __name__ == "__main__":
    register()
