import bpy
import os
from .map_bones import BoneMapping
from . import preferences

from . import bone_functions as b_fun
from . import bl_info

def tag_rig(rig):
    rig.data['one_click_rig'] = bl_info['version']

oops = bpy.ops.object
aops = bpy.ops.armature
pops = bpy.ops.pose

def copy_armature(context, rig, armature):
    context.view_layer.objects.active = armature
    armature.select_set(True)
    rig.select_set(False)
    oops.editmode_toggle();
    saved_bones = []
    for bone in armature.data.edit_bones:
        if bone.name == 'root':
            continue
        saved_bones.append((bone.name,
        bone.head.copy(),
        bone.tail.copy(),
        bone.x_axis.copy(),
        bone.parent.name if bone.parent else None))

    oops.editmode_toggle()

    context.view_layer.objects.active = rig
    armature.select_set(False)
    rig.select_set(True)

    oops.editmode_toggle()

    b_fun.switch_to_layer(rig.data, 24)

    eb = rig.data.edit_bones
    for bone in saved_bones:
        if bone[0] in eb:
            rig_bone = eb[bone[0]]
            rig_bone.name = 'rig.' + rig_bone.name
        new_bone = eb.new(bone[0])
        new_bone.head = bone[1]
        new_bone.tail = bone[2]
        b_fun.align_bone_x_axis(new_bone, bone[3])

    for bone in saved_bones:
        if bone[4]:
            eb[bone[0]].parent = eb[bone[4]]
        else:
            eb[bone[0]].parent = eb['root']

    eb['root'].use_deform = True
    oops.editmode_toggle()

def fix_twist_bones(context, rig):
    oops.mode_set(mode = 'EDIT')

    twist_bones = ['thigh_twist_01_l','thigh_twist_01_r','upperarm_twist_01_l','upperarm_twist_01_r']
    parent_bones = ['DEF-thigh.L','DEF-thigh.R','DEF-upper_arm.L','DEF-upper_arm.R']
    for i, b in enumerate(twist_bones):
        rig.data.edit_bones[b + '.copy'].parent = rig.data.edit_bones[parent_bones[i]]

    oops.mode_set(mode = 'POSE')
    limb_bones = ['thigh_l.copy','thigh_r.copy', 'upperarm_l.copy', 'upperarm_r.copy']

    pose_bones = rig.pose.bones
    for i, b in enumerate(limb_bones):
        constr = pose_bones[b].constraints.new('TRANSFORM')
        constr.map_from = constr.map_to = 'ROTATION'
        constr.target = rig
        constr.subtarget = parent_bones[i]+'.001'
        constr.map_to_x_from = 'Y'
        constr.target_space = constr.owner_space = 'LOCAL'
        if b in ['thigh_l.copy','thigh_r.copy']:
            constr.to_max_x_rot = -1.5708
        else:
            constr.to_max_x_rot = 1.5708
        constr.from_max_y_rot = 1.5708
        constr.use_motion_extrapolate = True
    # oops.mode_set(mode = 'POSE')
    return

def set_ik_follow_bone(context, rig, value):
    # ik_bones = ['ik_hand_l','ik_hand_r','ik_hand_gun',]
    mapping = {
        'ik_hand_l': 'hand_l',
        'ik_hand_r': 'hand_r',
        'ik_hand_gun': 'hand_r',
        'ik_foot_l': 'foot_l',
        'ik_foot_r': 'foot_r',
        'ik_hand_root': 'root',
        'ik_foot_root': 'root',
    }
    pose_bones = rig.pose.bones
    for key, value in mapping.items():
        copy_loc = pose_bones[key].constraints.new('COPY_LOCATION')
        copy_loc.target = rig
        copy_loc.subtarget = value
        copy_rot = pose_bones[key].constraints.new('COPY_ROTATION')
        copy_rot.target = rig
        copy_loc.subtarget = value
    return

ik_prop_bones = ['thigh_parent.L', 'thigh_parent.R', 'upper_arm_parent.L', 'upper_arm_parent.R']
# ik_bones = [
#     '["thigh_ik.L", "MCH-shin_ik.L", "MCH-thigh_ik_target.L"]',
#     '["thigh_ik.R", "MCH-shin_ik.R", "MCH-thigh_ik_target.R"]',
#     '["upper_arm_ik.L", "MCH-forearm_ik.L", "MCH-upper_arm_ik_target.L"]',
#     '["upper_arm_ik.R", "MCH-forearm_ik.R", "MCH-upper_arm_ik_target.R"]',
# ]
# ctrl_bones = [
#     '["thigh_ik.L", "foot_ik.L", "thigh_ik_target.L"]',
#     '["thigh_ik.R", "foot_ik.R", "thigh_ik_target.R"]',
#     '["upper_arm_ik.L", "hand_ik.L", "upper_arm_ik_target.L"]',
#     '["upper_arm_ik.R", "hand_ik.R", "upper_arm_ik_target.R"]',
# ]
# extra_ctrls = [
#     '["foot_heel_ik.L", "foot_spin_ik.L"]',
#     '["foot_heel_ik.R", "foot_spin_ik.R"]',
#     '[]',
#     '[]',
# ]
def fix_poles(context, rig):
    # rig_id = rig.data['rig_id']
    # toggle_pole_fn = 'rigify_limb_toggle_pole_' + rig_id
    # bones = rig.pose.bones
    # pops.select_all(action = 'DESELECT')
    # # ik_bones = ['foot_ik.L', 'foot_ik.R']
    # last_bone = None
    # for i, b in enumerate(ik_prop_bones):
    #     if last_bone:
    #         last_bone.select = last_bone.select_tail = last_bone.select_head = False
    #     bone = rig.data.bones[b]
    #     bone.select = bone.select_tail = bone.select_head = True
    #     last_bone = bone
    #     rig.data.bones.active = bone
    #     getattr(pops, toggle_pole_fn)(prop_bone = b, ik_bones = ik_bones[i], ctrl_bones = ctrl_bones[i], extra_ctrls = extra_ctrls[i])
    #     rig.pose.bones[b]["pole_vector"] = 1
    oops.mode_set(mode = 'EDIT')
    eb = rig.data.edit_bones
    poles = ['thigh_ik_target.L', 'thigh_ik_target.R', 'upper_arm_ik_target.R', 'upper_arm_ik_target.R']
    ik_bones = ['thigh_ik.L', 'thigh_ik.R', 'upper_arm_ik.R', 'upper_arm_ik.R']
    for i, b in enumerate(poles):
        pole = eb[b]
        ik = eb[ik_bones[i]]
        vec = -ik.z_axis
        vec.normalize()
        d = (ik.tail - pole.head).length
        len = pole.length
        pole.head = ik.tail + d * vec
        pole.tail = pole.head - len * vec
    oops.mode_set(mode = 'POSE')

    return

def disable_stretch(context, rig):
    for b in ik_prop_bones:
        rig.pose.bones[b]['IK_Stretch'] = 0
    return


def create_copy_bones(context, rig):

    mapping = BoneMapping('uemannequin_rigify', False)

    oops.mode_set(mode = 'EDIT')
    aops.select_all(action = 'SELECT')

    bone_names = []
    for bone in context.selected_bones:
        if bone.name.startswith('ik'):
            bone.select = False
            bone.select_tail = False
            bone.select_head = False
        else:
            bone_names.append(bone.name)

    aops.duplicate()
    eb = rig.data.edit_bones
    for bone in context.selected_bones:
        bone.name = bone.name.replace('001', 'copy')
        bone.use_deform = False
        # if bone.name in bones_mapping:
        #     bone.parent = eb[bones_mapping[bone.name]]
        # else:
        #     bone.parent = None

    for bone_name in bone_names:
        copy_bone = eb[bone_name + '.copy']
        mapped_bone_name = mapping.get_name(bone_name, safe = False)
        if mapped_bone_name:
            copy_bone.parent = eb['DEF-' + mapped_bone_name]
        elif 'DEF-' + bone_name in eb:
            copy_bone.parent = eb['DEF-' + bone_name]


    oops.posemode_toggle()

    pose_bones = rig.pose.bones
    for bone_name in bone_names:
        constr = pose_bones[bone_name].constraints.new('COPY_TRANSFORMS')
        constr.target = rig
        constr.subtarget = bone_name + '.copy'
        # constr.target_space = 'LOCAL'
        # constr.owner_space = 'LOCAL'

    oops.posemode_toggle()

    tag_rig(rig)

    return

class BindRigifyToArmatureOperator(bpy.types.Operator):
    """Select an armature and a rigify rig. Operator will copy the armature to the rig and binds them"""
    bl_idname = "object.ocr_bind_rigify_to_armature"
    bl_label = "Bind rigify rig to armature"
    bl_options = {'REGISTER', 'UNDO'}

    animation_ready: bpy.props.BoolProperty(name="Animation ready", default=True)

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        return (context.space_data.type == 'VIEW_3D'
            and len(selected) == 2
            and selected[0].type == 'ARMATURE'
            and selected[1].type == 'ARMATURE'
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        rig, armature = b_fun.get_rig_and_armature(context)

        rig.name = 'Armature'
        rig.show_in_front = True

        copy_armature(context, rig, armature)
        create_copy_bones(context, rig)
        fix_twist_bones(context, rig)

        mesh = armature.children[0]
        mesh.select_set(True)
        oops.parent_set(type = 'ARMATURE')
        mesh.select_set(False)
        oops.mode_set(mode = 'POSE')



        if self.animation_ready:
            disable_stretch(context, rig)
        b_fun.show_layers(rig, self.animation_ready)

        b_fun.set_def_bones_deform(rig, False)
        fix_poles(context, rig)
        set_ik_follow_bone(context, rig, True)

        # rig.pose.ik_solver = 'ITASC'
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
