import bpy
from . import preferences
import chardet

aops = bpy.ops.armature
oops = bpy.ops.object

def merge_vgroups(object, vg_from, vg_to):
    # print(object.vertex_groups.get(vg_to))
    if not object.vertex_groups.get(vg_from) or not object.vertex_groups.get(vg_to):
        return
    mods = object.modifiers
    mod = mods.new('VertexWeightMix', 'VERTEX_WEIGHT_MIX')
    mod.vertex_group_b = vg_from
    mod.vertex_group_a = vg_to
    mod.mix_mode = 'ADD'
    mod.mix_set = 'ALL'

    oops.modifier_apply(modifier = mod.name)

    vg = object.vertex_groups.get(vg_from)
    object.vertex_groups.remove(vg)
    print('group {} succesfully deleted'.format(vg_from))


class MergeBonesOperator(bpy.types.Operator):
    """Merge bones"""
    bl_idname = "armature.ocr_merge_bones_with_vgroups"
    bl_label = "Merge bones with vertex groups"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and context.object.mode in ['EDIT', 'POSE'])

    def execute(self, context):
        armature = context.object
        mode = context.object.mode
        oops.mode_set(mode = 'EDIT')
        bones = context.object.data.edit_bones

        selected_bones = [bone for bone in context.selected_bones]
        active_bone = context.active_bone

        active_vgroup_name = str(active_bone.name)
        selected_bones.remove(active_bone)
        children = context.object.children

        oops.editmode_toggle()
        armature.select_set(False)
        for child in children:
            context.view_layer.objects.active = child
            child.select_set(True)
            active_vg = child.vertex_groups.get(active_vgroup_name)
            if not active_vg:
                child.vertex_groups.new(name = active_vgroup_name)
            for b in selected_bones:
                try:
                    merge_vgroups(child, b.name, active_vgroup_name)
                except Exception as e:
                    # merge_vgroups(child, b.name, active_vgroup_name)
                    print(e)
                # c_name =

            child.select_set(False)

        armature.select_set(True)
        context.view_layer.objects.active = armature
        oops.editmode_toggle()
        active_bone = context.active_bone
        active_bone.select = False
        active_bone.select_head = False
        active_bone.select_tail = False
        aops.delete()
        active_bone.select = True
        active_bone.select_head = True
        active_bone.select_tail = True

        # self.prefs = preferences.get_prefs()
        oops.mode_set(mode = 'POSE')

        # self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
