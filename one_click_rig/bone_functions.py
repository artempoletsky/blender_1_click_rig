import math

def set_array_indices(array, indices):
    for i in range(len(array)):
        array[i] = True if i in indices else False

def switch_to_layer(arm, index):
    arm.layers[index] = True
    for i in range(len(arm.layers)):
        if i == index:
            continue
        arm.layers[i] = False

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

def set_def_bones_deform(rig, value):
    for b in rig.data.bones:
        if b.name.startswith('DEF'):
            print(b.name)
            b.use_deform = value


def rename_v_group(object, name, new_name):
    v_group = object.vertex_groups.get(name)
    # print(v_group)
    if not v_group:
        return
    v_group.name = new_name

def rename_childs_v_group(rig, name, new_name):
    for c in rig.children:
        rename_v_group(c, name, new_name)


def show_layers(rig, animation_ready):
    layers = rig.data.layers
    visible_layers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18, 28]
    if animation_ready:
        visible_layers = [0, 3, 5, 7, 10, 13, 16, 28]
    set_array_indices(layers, visible_layers)
    return


def get_rig_and_armature(context):
    selected = context.selected_objects
    if 'rig_id' in selected[0].data:
        rig = selected[0]
        source = selected[1]
    else:
        rig = selected[1]
        source = selected[0]
    return rig, source


ik_prop_bones = ['thigh_parent.L', 'thigh_parent.R', 'upper_arm_parent.L', 'upper_arm_parent.R']
def set_ik_fk(rig, value):
    for n in ik_prop_bones:
        rig.pose.bones[n]['IK_FK'] = value

def snap_ik_to_fk(rig):
    return

def snap_fk_to_ik(rig):
    return
