import bpy
from . import preferences
from . import map_bones
from . import templates
from . import bone_functions as b_fun
import json
from mathutils import Matrix, Vector
import re
import os

oops = bpy.ops.object
pose_dir = os.path.dirname(os.path.realpath(__file__)) + '/poses/'

def get_pose_file(name):
    return pose_dir + name + '.json'

def save_pose(name, data):
    fks = data['fks']
    for key, value in fks.items():
        fks[key] = templates.serialize_matrix(value)
    data['fks'] = fks

    data['torso'] = list(data['torso'][0:3])

    with open(get_pose_file(name), 'w') as outfile:
        json.dump(data, outfile)

def load_pose(name):
    with open(get_pose_file(name)) as json_file:
        data = json.load(json_file)
    fks = data['fks']
    for key, value in fks.items():
        fks[key] = Matrix(fks[key])
    data['fks'] = fks
    data['torso'] = Vector(data['torso'])
    return data

bones_to_pose = ['spine_fk','spine_fk.001','spine_fk.002','spine_fk.003','neck','head',
'shoulder.L','upper_arm_fk.L','forearm_fk.L','hand_fk.L',
'thumb.01.L','thumb.02.L','thumb.03.L',
'f_index.01.L','f_index.02.L','f_index.03.L',
'f_middle.01.L','f_middle.02.L','f_middle.03.L',
'f_ring.01.L','f_ring.02.L','f_ring.03.L',
'f_pinky.01.L','f_pinky.02.L','f_pinky.03.L',
'shoulder.R','upper_arm_fk.R','forearm_fk.R','hand_fk.R',
'thumb.01.R','thumb.02.R','thumb.03.R',
'f_index.01.R','f_index.02.R','f_index.03.R',
'f_middle.01.R','f_middle.02.R','f_middle.03.R',
'f_ring.01.R','f_ring.02.R','f_ring.03.R',
'f_pinky.01.R','f_pinky.02.R','f_pinky.03.R',
'thigh_fk.L','shin_fk.L',
'thigh_fk.R','shin_fk.R',
]
class PoseCharacterOperator(bpy.types.Operator):
    """Pose character to mannequin pose"""
    bl_idname = "pose.ocr_pose_character"
    bl_label = "Pose character to mannequin pose"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.view_layer.objects.active.type == 'ARMATURE'
            )

    def execute(self, context):
        rig = context.view_layer.objects.active
        oops.mode_set(mode = 'POSE')
        pose_bones = rig.pose.bones
        b_fun.set_ik_fk(rig, 1.0)
        data = load_pose('ue_mannequin')
        matrices = data['fks']
        torso = data['torso']

        for bone_name in bones_to_pose:
            if bone_name in pose_bones:
                bone = pose_bones[bone_name]
            elif 'rig.' + bone_name in pose_bones:
                bone = pose_bones['rig.' + bone_name]
            else:
                continue
            if not bone_name in matrices:
                continue
            t = Matrix.Translation(bone.matrix.to_translation())
            # r = pose_bones[bone].matrix.to_quaternion().to_matrix().to_4x4()
            r = matrices[bone_name].to_quaternion().to_matrix().to_4x4()
            s = Matrix.Scale(1, 4, bone.matrix.to_scale())
            # print(t)

            bone.matrix = t @ s @ r
            oops.posemode_toggle()
            oops.posemode_toggle()
        torso_bone = pose_bones['torso']
        head = torso_bone.head.copy()
        head.y = torso.y
        t = Matrix.Translation(head - torso_bone.head)
        torso_bone.matrix = torso_bone.matrix @ t

#         pose_ops = bpy.ops.pose
#
#         pose_ops['rigify_limb_ik2fk_' + rig_id]()
# props = group1.operator('pose.rigify_limb_ik2fk_tm2w8d4817ffd6f5', text='IK->FK (hand.L)', icon='SNAP_ON')
# props.prop_bone = 'upper_arm_parent.L'
# props.fk_bones = '["upper_arm_fk.L", "forearm_fk.L", "hand_fk.L"]'
# props.ik_bones = '["upper_arm_ik.L", "MCH-forearm_ik.L", "MCH-upper_arm_ik_target.L"]'
# props.ctrl_bones = '["upper_arm_ik.L", "hand_ik.L", "upper_arm_ik_target.L"]'
# props.extra_ctrls = '[]'
        return {'FINISHED'}


class SavePoseOperator(bpy.types.Operator):
    """Save pose"""
    bl_idname = "pose.ocr_save_pose"
    bl_label = "Save pose"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.view_layer.objects.active.type == 'ARMATURE'
            )

    def execute(self, context):
        rig = context.view_layer.objects.active
        
        oops.mode_set(mode = 'POSE')
        pose_bones = rig.pose.bones
        fks = {}
        for bone_name in bones_to_pose:
            if bone_name in pose_bones:
                bone = pose_bones[bone_name]
                fks[bone_name] = bone.matrix.copy()
            elif 'rig.' + bone_name in pose_bones:
                bone = pose_bones['rig.' + bone_name]
                fks[bone_name] = bone.matrix.copy()

        torso = pose_bones['torso'].head.copy()

        save_pose('ue_mannequin', {
            'fks': fks,
            'torso': torso
        })

        return {'FINISHED'}
