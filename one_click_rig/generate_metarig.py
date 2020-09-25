import bpy
import os
from . import preferences
from .map_bones import BoneMapping
from mathutils import Vector, Matrix
import math
from . import bone_functions as b_fun

oops = bpy.ops.object
aops = bpy.ops.armature

saved_x_axises = {}
saved_y_axises = {}
saved_z_axises = {}



def get_vertices_in_vgroup(object, vgroup_name, min_weight = 0.01):
    if not vgroup_name in object.vertex_groups:
        return []
    v_group = object.vertex_groups[vgroup_name]
    index = v_group.index
    vertices = []
    for v in object.data.vertices:
        found = False
        for g in v.groups:
            if g.group == index and g.weight > min_weight:
                found = True
                break
        if found:
            vertices.append(v)
    return vertices

def get_foot_end(object, toe_bone_name):
    end = float('inf')
    verts = get_vertices_in_vgroup(object, toe_bone_name)
    for v in verts:
        end = min(end, v.co.y)
    return end

def save_axises(armature):
    oops.editmode_toggle()
    for bone in armature.edit_bones:
        saved_x_axises[bone.name] = bone.x_axis
        saved_y_axises[bone.name] = bone.y_axis
        saved_z_axises[bone.name] = bone.z_axis
    oops.editmode_toggle()


def copy_rotation_from_parent(edit_bone):
    parent = edit_bone.parent
    if not parent.parent:
        return

    q1 = parent.parent.matrix.to_quaternion()
    q2 = parent.matrix.to_quaternion()
    q_diff = q1.rotation_difference(q2)

    edit_bone.matrix =  edit_bone.matrix @ q_diff.to_matrix().to_4x4()


def align_bone_x_axis(edit_bone, new_x_axis):
    """ new_x_axis is a 3D Vector the edit_bone's x-axis will point towards.
    """
    new_x_axis = new_x_axis.cross(edit_bone.y_axis)
    new_x_axis.normalize()
    dot = max(-1.0, min(1.0, edit_bone.z_axis.dot(new_x_axis)))
    angle = math.acos(dot)
    edit_bone.roll += angle
    dot1 = edit_bone.z_axis.dot(new_x_axis)
    edit_bone.roll -= angle * 2.0
    dot2 = edit_bone.z_axis.dot(new_x_axis)
    if dot1 > dot2:
        edit_bone.roll += angle * 2.0

def get_bone(armature, bone_name, mapping = None):
    if mapping:
        bone_name = mapping.get_name(bone_name)
    if not bone_name in armature.bones:
        return None
    return armature.bones[bone_name]

def get_bone_position(armature, bone_name, mapping = None, head = True):
    bone = get_bone(armature, bone_name, mapping)
    if not bone:
        return None
    return Vector(bone.head_local if head else bone.tail_local)


def switch_to_layer(arm, index):
    arm.layers[index] = True
    for i in range(len(arm.layers)):
        if i == index:
            continue
        arm.layers[i] = False
    # armature.layers[3] = armature.layers[5] = armature.layers[7] = armature.layers[10] = True


def set_array_indices(array, indices):
    for i in range(len(array)):
        array[i] = True if i in indices else False

def set_rigify_type(object, bone_name, type, fk_layer, tweak_layer):
    oops.posemode_toggle();
    bone = object.pose.bones[bone_name]
    bone.rigify_type = type

    set_array_indices(bone.rigify_parameters.tweak_layers, [tweak_layer])
    set_array_indices(bone.rigify_parameters.fk_layers, [fk_layer])
    oops.editmode_toggle();
    return bone.rigify_parameters

def create_bone_chain(spine_arr, source_armature, object, layer = 0, parent_name = None):
    # print(spine_arr)
    target_armature = object.data
    # set_array_indices(target_armature.layers, [layer])
    switch_to_layer(target_armature, layer)
    spine_len = len(spine_arr)
    source_bones = source_armature.bones
    target_bones = target_armature.edit_bones

    parent = None
    created_bones = []

    for i in range(spine_len):
        head_bone_name = spine_arr[i]
        head_bone = get_bone(source_armature, head_bone_name)
        if head_bone is None:
            print(spine_arr[i] + ' passed head')
            continue
        head = head_bone.head_local

        q_diff = None


        if i == spine_len - 1:
            y_vec = parent.vector
            y_vec.normalize()
            tail = head + y_vec * head_bone.length

        else:
            tail = get_bone_position(source_armature, spine_arr[i + 1])
            if tail is None:
                print(spine_arr[i + 1] + ' passed tail')
                continue

        target_bone = target_bones.new(spine_arr[i])

        target_bone.head = head
        target_bone.tail = tail

        created_bones.append(target_bone)

        if parent:
            target_bone.parent = parent
            target_bone.use_connect = True
        elif parent_name and parent_name in target_bones:
            target_bone.parent = target_bones[parent_name]
            target_bone.use_connect = False

        parent = target_bone

    return created_bones

def align_bone_to_vector(edit_bone, vector):
    vector.normalize()
    edit_bone.tail = edit_bone.head + vector * edit_bone.length

def align_bone_to_point(edit_bone, point):
    vector = point - edit_bone.head
    align_bone_to_vector(edit_bone, vector)

def add_single_bone(name, parent_name, source_armature, object, direction_bone_name = None, layer = 0, fk_layer_offset = 1, tweak_layer_offset = 1, direction_vector = None):
    target_armature = object.data
    switch_to_layer(target_armature, layer)
    source_bone = get_bone(source_armature, name)
    if not source_bone:
        print(name + ' passed')
        return

    bone = target_armature.edit_bones.new(name)
    bone.head = source_bone.head_local
    bone.tail = source_bone.tail_local

    if direction_bone_name:
        align_bone_to_point(bone, get_bone_position(source_armature, direction_bone_name))
    else:
        if not direction_vector:
            direction_vector = saved_x_axises[name]
        align_bone_to_vector(bone, direction_vector)

    parent = None
    if parent_name:
        if parent_name in target_armature.edit_bones:
            bone.parent = target_armature.edit_bones[parent_name]

    b_fun.align_bone_x_axis(bone, saved_y_axises[name])

    rigify_parameters = set_rigify_type(object, bone.name, 'basic.super_copy', layer + fk_layer_offset, layer + tweak_layer_offset)

    return bone, rigify_parameters

def create_spine(source_armature, object):
    spine = ['pelvis', 'spine_01', 'spine_02', 'spine_03']
    bones = create_bone_chain(spine, source_armature, object, layer = 3)
    neck_position = get_bone_position(source_armature, 'neck_01')
    bones[-1].tail = neck_position

    set_rigify_type(object, 'pelvis', 'spines.basic_spine', 4, 4)

def create_head(source_armature, object):
    bones = ['neck_01', 'head']
    bones = create_bone_chain(bones, source_armature, object, layer = 3, parent_name = 'spine_03')
    align_bone_to_vector(bones[-1], Vector((0, 0, 1)))
    set_rigify_type(object, 'neck_01', 'spines.super_head', 4, 4)

def get_finger_end_point(object, vgroup_name, bone_head):
    verts = get_vertices_in_vgroup(object, vgroup_name)
    v_group = object.vertex_groups[vgroup_name]
    coord = bone_head.copy()
    max_d = 0

    for v in verts:
        max_d = max(max_d, (v.co - bone_head).length)

    for v in verts:
        dir = v.co - bone_head
        # print(v_group.weight(v.index))
        # print(dir.length / max_d)
        coord += dir * v_group.weight(v.index) * pow(dir.length / max_d, 10)
        # coord += v.co * v_group.weight(v.index) * (v.co - bone_head).length / max_d
    # coord = coord / len(verts)
    return coord

def get_finger_axis(armature, finger, suffix):
    f_name = finger.name.rstrip(suffix)
    if f_name == 'index_01_':
        neigbour = 'middle_01_' + suffix
    elif f_name == 'middle_01_':
        neigbour = 'ring_01_' + suffix
    elif f_name == 'ring_01_':
        neigbour = 'pinky_01_' + suffix
    elif f_name == 'pinky_01_':
        neigbour = 'ring_01_' + suffix
    elif f_name == 'thumb_01_':
        neigbour = 'index_01_' + suffix

    n_pos = get_bone_position(armature, neigbour)
    axis = n_pos - finger.head
    if f_name == 'pinky_01_':
        axis = -axis
    # v1 = n_pos - finger.head
    # v2 = finger.vector

    return axis


def create_finger(name, suffix, source_object, object):
    source_armature = source_object.data
    spine = [name + '_01_' + suffix, name + '_02_' + suffix, name + '_03_' + suffix]
    bones = create_bone_chain(spine, source_armature, object, layer = 5, parent_name = 'hand_' + suffix)
    # copy_rotation_from_parent(bones[-1])
    # vec = get_finger_end_point(source_object.children[0], name + '_03_' +, bones[-1].head)
    # print(vec)
    # bones[-1].tail = vec
    # align_bone_to_point(bones[-1], vec)
    # axis = get_finger_axis(source_object.data, bones[0], suffix)
    align_bone_x_axis(bones[0], saved_z_axises[bones[0].name])
    align_bone_x_axis(bones[1], saved_z_axises[bones[1].name])
    align_bone_x_axis(bones[2], saved_z_axises[bones[2].name])


    params = set_rigify_type(object, name + '_01_' + suffix, 'limbs.super_finger', 6, 6)
    params.primary_rotation_axis = 'X'


def create_leg(suffix, source_object, object, layer = 0):
    source_armature = source_object.data
    spine = ['thigh_' + suffix, 'calf_' + suffix, 'foot_' + suffix, 'ball_' + suffix]
    bones = create_bone_chain(spine, source_armature, object, layer = layer, parent_name = 'pelvis')

    heel_width = 0.05
    heel_x = bones[1].tail.x
    heel_y = bones[1].tail.y
    heel_x = heel_x - heel_width if suffix == 'l' else heel_x + heel_width
    heel_width = heel_width * 2 if suffix == 'l' else -2 * heel_width

    heel = object.data.edit_bones.new('heel.'+suffix.upper())
    heel.use_connect = False
    heel.parent = bones[2]
    heel.head = Vector((heel_x, heel_y, 0))
    heel.tail = Vector((heel_x + heel_width, heel_y, 0))

    align_bone_x_axis(bones[0], Vector((1, 0, 0)))
    align_bone_x_axis(bones[1], Vector((1, 0, 0)))

    foot_end = get_foot_end(source_object.children[0], 'ball_' + suffix)
    if foot_end == float('inf'):
        foot_end = bones[-1].head.y - 0.1
    bones[-1].tail.y = foot_end
    bones[-1].tail.z = bones[-1].head.z
    # print(foot_end)
    params = set_rigify_type(object, 'thigh_' + suffix, 'limbs.super_limb', layer + 1, layer + 2)
    params.limb_type = 'leg'
    params.rotation_axis = 'x'

def create_arm(suffix, source_armature, object, layer = 0):
    spine = ['upperarm_' + suffix, 'lowerarm_' + suffix, 'hand_' + suffix]
    bones = create_bone_chain(spine, source_armature, object, layer = layer, parent_name = 'clavicle_' + suffix)
    # align_bone_to_vector(bones[-1], saved_x_axises['hand_' + suffix])
    align_bone_x_axis(bones[-1], saved_y_axises['hand_' + suffix])
    align_bone_x_axis(bones[1], -saved_z_axises[bones[1].name])
    align_bone_x_axis(bones[0], -saved_z_axises[bones[0].name])
    set_rigify_type(object, 'upperarm_' + suffix, 'limbs.super_limb', layer + 1, layer + 2)


class GenerateMetarigOperator(bpy.types.Operator):
    """Select an armature. Operator will create new metarig from the armature."""
    bl_idname = "object.ocr_generate_metarig"
    bl_label = "Generate metarig from armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            # and len(context.selected_objects) > 0
            and context.view_layer.objects.active
            and context.object.type == 'ARMATURE'
            and (context.object.mode == 'OBJECT'))

    def execute(self, context):
        mapping = BoneMapping('rigify_uemannequin', True)
        # mapping = None
        location = context.object.location
        source_object = context.object
        source_armature = context.object.data


        save_axises(source_armature)

        oops.select_all(action = 'DESELECT')
        oops.armature_add(enter_editmode = True, align='WORLD', location = location)
        aops.select_all(action = 'SELECT')
        aops.delete()

        context.object.show_in_front = True
        context.object.name = 'metarig'
        context.object.data.show_axes = True

        bpy.ops.pose.rigify_layer_init()
        bpy.ops.armature.rigify_add_bone_groups()
        create_layers(context.object.data)

        create_spine(source_armature, context.object)
        create_head(source_armature, context.object)

        bone, params = add_single_bone('clavicle_l', 'spine_03', source_armature, context.object, direction_bone_name = 'upperarm_l', layer = 3)
        params.make_widget = False
        bone, params = add_single_bone('clavicle_r', 'spine_03', source_armature, context.object, direction_bone_name = 'upperarm_r', layer = 3)
        params.make_widget = False

        add_single_bone('breast_l', 'spine_02', source_armature, context.object, layer = 3)
        add_single_bone('breast_r', 'spine_02', source_armature, context.object, layer = 3)

        create_arm('l', source_armature, context.object, layer = 7)

        create_arm('r', source_armature, context.object, layer = 10)

        create_finger('thumb', 'l', source_object, context.object)
        create_finger('index', 'l', source_object, context.object)
        create_finger('middle', 'l', source_object, context.object)
        create_finger('ring', 'l', source_object, context.object)
        create_finger('pinky', 'l', source_object, context.object)

        create_finger('thumb', 'r', source_object, context.object)
        create_finger('index', 'r', source_object, context.object)
        create_finger('middle', 'r', source_object, context.object)
        create_finger('ring', 'r', source_object, context.object)
        create_finger('pinky', 'r', source_object, context.object)

        create_leg('l', source_object, context.object, layer = 13)
        create_leg('r', source_object, context.object, layer = 16)

        for bone in source_armature.bones:
            if not mapping.get_name(bone.name, safe = False) and not bone.name.startswith('ik') and not bone.name == 'root':
                parent_name = bone.parent.name if bone.parent else None
                add_single_bone(bone.name, parent_name, source_armature, context.object, layer = 3)

        set_array_indices(context.object.data.layers, [0, 3, 5, 7, 10, 13, 16])
        mapping.rename_armature(context.object.data)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

def create_layers(arm):
    arm.rigify_layers[0].name = 'Face'
    arm.rigify_layers[0].row = 1
    arm.rigify_layers[0].group = 5

    arm.rigify_layers[1].name = 'Face (Primary)'
    arm.rigify_layers[1].row = 2
    arm.rigify_layers[1].group = 2

    arm.rigify_layers[2].name = 'Face (Secondary)'
    arm.rigify_layers[2].row = 2
    arm.rigify_layers[2].group = 3


    arm.rigify_layers[3].name = 'Torso'
    arm.rigify_layers[3].row = 3
    arm.rigify_layers[3].group = 3

    arm.rigify_layers[4].name = 'Torso (Tweak)'
    arm.rigify_layers[4].row = 4
    arm.rigify_layers[4].group = 4

    arm.rigify_layers[5].name = 'Fingers'
    arm.rigify_layers[5].row = 5
    arm.rigify_layers[5].group = 6

    arm.rigify_layers[6].name = 'Fingers (Detail)'
    arm.rigify_layers[6].row = 6
    arm.rigify_layers[6].group = 5

    arm.rigify_layers[7].name = 'Arm.L (IK)'
    arm.rigify_layers[7].row = 7
    arm.rigify_layers[7].group = 2
    arm.rigify_layers[8].name = 'Arm.L (FK)'
    arm.rigify_layers[8].row = 8
    arm.rigify_layers[8].group = 5
    arm.rigify_layers[9].name = 'Arm.L (Tweak)'
    arm.rigify_layers[9].row = 9
    arm.rigify_layers[9].group = 4

    arm.rigify_layers[10].name = 'Arm.R (IK)'
    arm.rigify_layers[10].row = 7
    arm.rigify_layers[10].group = 2
    arm.rigify_layers[11].name = 'Arm.R (FK)'
    arm.rigify_layers[11].row = 8
    arm.rigify_layers[11].group = 5
    arm.rigify_layers[12].name = 'Arm.R (Tweak)'
    arm.rigify_layers[12].row = 9
    arm.rigify_layers[12].group = 4

    arm.rigify_layers[13].name = 'Leg.L (IK)'
    arm.rigify_layers[13].row = 10
    arm.rigify_layers[13].group = 2
    arm.rigify_layers[14].name = 'Leg.L (FK)'
    arm.rigify_layers[14].row = 11
    arm.rigify_layers[14].group = 5
    arm.rigify_layers[15].name = 'Leg.L (Tweak)'
    arm.rigify_layers[15].row = 12
    arm.rigify_layers[15].group = 4

    arm.rigify_layers[16].name = 'Leg.R (IK)'
    arm.rigify_layers[16].row = 10
    arm.rigify_layers[16].group = 2
    arm.rigify_layers[17].name = 'Leg.R (FK)'
    arm.rigify_layers[17].row = 11
    arm.rigify_layers[17].group = 5
    arm.rigify_layers[18].name = 'Leg.R (Tweak)'
    arm.rigify_layers[18].row = 12
    arm.rigify_layers[18].group = 4
    return
