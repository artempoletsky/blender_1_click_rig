import bpy
from . import preferences

ANTONYMS = {
    'Add': 'Subtract',
    'Lighten': 'Darken',
}

for key, value in list(ANTONYMS.items()):
    ANTONYMS[value] = key

class WeightPaintToggleOperator(bpy.types.Operator):
    """Empty operator"""
    bl_idname = "paint.toggle_weight_paint"
    bl_label = "Toggle weight paint"
    # bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.mode == 'WEIGHT_PAINT')

    def execute(self, context):
        settings = context.scene.tool_settings.unified_paint_settings
        brush = context.scene.tool_settings.weight_paint.brush
        if brush.name in ANTONYMS:
            context.scene.tool_settings.weight_paint.brush = bpy.data.brushes[ANTONYMS[brush.name]]
        else:
            settings.weight = 1 - settings.weight
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
