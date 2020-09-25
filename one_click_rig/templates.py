import bpy
import json
import os
from mathutils import Matrix, Vector

oops = bpy.ops.object

templates_dir = dir_path = os.path.dirname(os.path.realpath(__file__)) + '/templates/'

def get_template_file(name):
    return templates_dir + name + '.json'

def load_template(name):
    with open(get_template_file(name)) as json_file:
        data = json.load(json_file)

    for key, value in data['matrices'].items():
        data['matrices'][key] = Matrix(data['matrices'][key])

    for ik in data['iks']:
        ik['head'] = Vector(ik['head'])
        ik['tail'] = Vector(ik['tail'])
    return data

def serialize_matrix(mat):
    result = []
    for i in range(len(mat)):
        result.append(list(mat[i][0:4]))
    return result

def save_template(name, data):
    matrices = data['matrices']
    for key, value in matrices.items():
        matrices[key] = serialize_matrix(value)
    data['matrices'] = matrices

    iks = data['iks']
    for ik in iks:
        ik['head'] = list(ik['head'][0:3])
        ik['tail'] = list(ik['tail'][0:3])
    data['iks'] = iks

    with open(get_template_file(name), 'w') as outfile:
        json.dump(data, outfile)

def get_matrices(ue_skeleton):
    result = {}
    for bone in ue_skeleton.data.edit_bones:
        result[bone.name] = bone.matrix.copy()
    return result


def get_iks(ue_skeleton):
    result = []
    for bone in ue_skeleton.data.edit_bones:
        if bone.name.startswith('ik'):
            result.append({
                'name': bone.name,
                'head': bone.head.copy(),
                'tail': bone.tail.copy(),
            })
    return result

def get_parents(ue_skeleton):
    result = {}
    for bone in ue_skeleton.data.edit_bones:
        result[bone.name] = bone.parent.name if bone.parent else 'root'
    return result


class SaveSkeletonDataOperator(bpy.types.Operator):
    """Save skeleton data to template"""
    bl_idname = "object.ocr_save_skeleton_data"
    bl_label = "Save skeleton template"
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
        ue_skeleton = context.view_layer.objects.active
        oops.mode_set(mode = 'EDIT')
        matrices = get_matrices(ue_skeleton)
        iks = get_iks(ue_skeleton)
        parents = get_parents(ue_skeleton)

        save_template('ue_mannequin', {
            'matrices': matrices,
            'iks': iks,
            'parents': parents
        })

        oops.mode_set(mode = 'OBJECT')
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
