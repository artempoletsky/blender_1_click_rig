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
