import bpy
import os
import json
from . import preferences
from . import bone_functions as b_fun
from . import bind_rig_to_armature as bind
from .map_bones import BoneMapping
from . import templates
import re

oops = bpy.ops.object
pops = bpy.ops.pose
aops = bpy.ops.armature

def ue_roll_bone(bone, matrices):
    bone.use_connect = False
    if bone.name in matrices:
        head = bone.head.copy()
        bone.matrix = matrices[bone.name]
        bone.translate(head - bone.head)

def add_ik_bones(rig, bones, matrices):
    eb = rig.data.edit_bones
    for b in bones:
        bone = eb.new(b['name'])
        bone.head = b['head']
        bone.tail = b['tail']
        bone.matrix = matrices[b['name']]


def apply_ik_bones(rig, bones):
    b_fun.select_bones(rig, [b['name'] for b in bones])
    pops.visual_transform_apply()
    pops.armature_apply(selected = True)

def link_parents(rig, bones, parents, rig_parents):
    eb = rig.data.edit_bones
    for b in bones:
        if b.name in parents:
            b.parent = eb[parents[b.name]]
        elif b.name in rig_parents:
            parent_name = rig_parents[b.name]
            if parent_name in eb:
                b.parent = eb[parent_name]
            else:
                print(parent_name)

def count_spine_len(rig):
    l = 0
    for bone in rig.data.bones:
        if bone.name.startswith('ORG-spine'):
                l += 1
    return l

class AddUnrealSkeletonOperator(bpy.types.Operator):
    """Add unreal skeleton to rigify rig"""
    bl_idname = "object.ocr_add_unreal_skeleton"
    bl_label = "Add unreal skeleton to rig"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'OBJECT'))

    def execute(self, context):


        rig = context.view_layer.objects.active

        spine_len = count_spine_len(rig)
        # print(spine_len)
        if spine_len == 6:
            mapping = BoneMapping('uemannequin_rigify', True)
            reverse_mapping = BoneMapping('uemannequin_rigify', False)
            template = templates.load_template('ue_mannequin')
        elif spine_len == 7:
            mapping = BoneMapping('uemannequin_neck2_rigify', True)
            reverse_mapping = BoneMapping('uemannequin_neck2_rigify', False)
            template = templates.load_template('ue_mannequin_neck2')
        else:
            self.report({'ERROR'}, 'Only spine length of 6 or 7 is supported')
            return {'FINISHED'}

        rig.name = 'Armature'

        if 'one_click_rig' in rig.data:
            self.report({'ERROR'}, 'Rig is already contains unreal skeleton')
            return {'FINISHED'}
        oops.mode_set(mode = 'EDIT')

        b_fun.switch_to_layer(rig.data, 24)

        eb = rig.data.edit_bones

        def_prefix = 'DEF-'
        org_prefix = 'ORG-'
        def_bones = [b for b in eb if b.name.startswith(def_prefix)]

        rig_parents = {}
        for b in def_bones:
            name = mapping.get_name(b.name.strip(def_prefix))
            if name in eb:
                eb[name].name = 'rig.' + name
            b_fun.rename_childs_v_group(rig, b.name, name)
            parent_name = b.parent.name if b.parent else None
            if parent_name:
                # print(b.name, parent_name)
                if parent_name.startswith(def_prefix):
                    parent_name = mapping.get_name(re.sub('^' + def_prefix, '', parent_name))
                    rig_parents[name] = parent_name
                else:
                    parent_name = b.parent.parent.name if b.parent.parent else None

                    if parent_name:
                        parent_name = mapping.get_name(re.sub('^' + org_prefix, '', re.sub('^' + def_prefix, '', parent_name)))
                        rig_parents[name] = parent_name
                # print(parent_name)

            bone = eb.new(name)
            bone.head = b.head
            bone.tail = b.tail
            bone.matrix = b.matrix.copy()
            ue_roll_bone(bone, template['matrices'])

        add_ik_bones(rig, template['iks'], template['matrices'])

        aops.select_all(action = 'SELECT')

        link_parents(rig, context.selected_editable_bones, template['parents'], rig_parents)

        bind.create_copy_bones(context, rig, reverse_mapping)
        bind.fix_twist_bones(context, rig, swap_vgroups = True)

        oops.mode_set(mode = 'POSE')
        bind.set_ik_follow_bone(context, rig, True)
        apply_ik_bones(rig, template['iks'])

        b_fun.show_layers(rig, True)
        rig.data.bones['root'].use_deform = True
        b_fun.set_def_bones_deform(rig, False)



        bind.tag_rig(rig)

        self.report({'INFO'}, 'Unreal skeleton sucessfully added')

        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
