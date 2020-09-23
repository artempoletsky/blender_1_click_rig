import bpy
from . import preferences

def is_vgroup_empty(object, vg_name, check_vertices, delete_if_empty):
    v_group = object.vertex_groups.get(vg_name)
    if not v_group:
        return True
    if not check_vertices:
        return False

    me = object.data
    is_empty = v_group.index in ([g.group for g in v.groups] for v in me.vertices)

    # print(is_empty)
    if is_empty and delete_if_empty:
        object.vertex_groups.remove(v_group)

    return is_empty

class ClearEmptyBonesOperator(bpy.types.Operator):
    """Clear empty bones"""
    bl_idname = "armature.ocr_clear_empty_bones"
    bl_label = "Clear empty bones"
    bl_options = {'REGISTER', 'UNDO'}

    selected_only: bpy.props.BoolProperty(name="Selected only", default=False)
    remove_empty_groups: bpy.props.BoolProperty(name="Remove bones with empty vertex groups", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and context.object.mode == 'EDIT')

    def execute(self, context):
        # self.prefs = preferences.get_prefs()

        #

        bones = context.selected_bones if self.selected_only else context.object.data.edit_bones
        empty_bones = []
        for bone in bones:
            is_empty = True
            for child in context.object.children:
                if not is_vgroup_empty(child, bone.name, self.remove_empty_groups, self.remove_empty_groups):
                    is_empty = False
                    break

            if is_empty:
                empty_bones.append(bone)
        self.report({'INFO'}, 'Found {} empty bones'.format(len(empty_bones)))
        for bone in empty_bones:
            context.object.data.edit_bones.remove(bone)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
