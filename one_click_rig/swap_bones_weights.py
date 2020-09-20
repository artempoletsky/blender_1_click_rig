import bpy
from . import preferences
def swap_vertex_groups_names(object, name1, name2):
    v_group1 = object.vertex_groups.get(name1)
    v_group2 = object.vertex_groups.get(name2)
    if not v_group1 and not v_group2:
        return
    if not v_group2:
        v_group1.name = name2
    if not v_group1:
        v_group2.name = name1

    v_group1.name = 'temp_renaming_vgroup_name'
    v_group2.name = name1
    v_group1.name = name2

class SwapBonesWeightsOperator(bpy.types.Operator):
    """Swap bones weights"""
    bl_idname = "armature.swap_bones_weights"
    bl_label = "Swap bones weights"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'EDIT')
            and len(context.selected_bones) == 2)

    def execute(self, context):
        bones = context.selected_bones
        print(bones)
        children = context.object.children

        for child in children:
            swap_vertex_groups_names(child, bones[0].name, bones[1].name)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
