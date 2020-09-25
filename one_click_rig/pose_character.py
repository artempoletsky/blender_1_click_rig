import bpy
from . import preferences
from . import map_bones
from . import templates
from . import bone_functions as b_fun
import json
from mathutils import Matrix, Vector

import os

oops = bpy.ops.object
pose_dir = os.path.dirname(os.path.realpath(__file__)) + '/poses/'

def get_pose_file(name):
    return pose_dir + name + '.json'

def save_pose(name, data):
    for key, value in data.items():
        data[key] = templates.serialize_matrix(value)

    with open(get_pose_file(name), 'w') as outfile:
        json.dump(data, outfile)

def load_pose(name):
    with open(get_pose_file(name)) as json_file:
        data = json.load(json_file)

    for key, value in data.items():
        data[key] = Matrix(data[key])
    return data


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
        matrices = load_pose('ue_mannequin')
        affected_bones = [bone for bone in pose_bones if bone.name in matrices]
        # while len(affected_bones):
        #     bone = affected_bones[0]
        #     while bone.parent:
        #         bone = bone.parent
        #     affected_bones.remove(bone)
        #     bone.matrix = matrices[bone.name]
        for bone, matrix in matrices.items():
            t = Matrix.Translation(pose_bones[bone].matrix.to_translation())
            # r = pose_bones[bone].matrix.to_quaternion().to_matrix().to_4x4()
            r = matrix.to_quaternion().to_matrix().to_4x4()
            s = Matrix.Scale(1, 4, pose_bones[bone].matrix.to_scale())
            # print(t)

            pose_bones[bone].matrix = t @ s @ r
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
        mapping = map_bones.load_mapping('rigify_uemannequin', anim = True)

        fk_bones = [fr for fr, to, type in mapping]


        oops.mode_set(mode = 'POSE')

        matrices = {}
        for bone in rig.pose.bones:
            if bone.name in fk_bones:
                matrices[bone.name] = bone.matrix

        save_pose('ue_mannequin', matrices)

        return {'FINISHED'}
