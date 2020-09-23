import bpy
from . import preferences
from . import bone_functions as b_fun

oops = bpy.ops.object

mapping = [
    ('thigh_fk.L', 'thigh_l', 'rot'),
    ('thigh_fk.R', 'thigh_r', 'rot'),
    ('shin_fk.L', 'calf_l', 'rot'),
    ('shin_fk.R', 'calf_r', 'rot'),
    ('foot_fk.L', 'foot_l', 'rot'),
    ('foot_fk.R', 'foot_r', 'rot'),
    ('toe.L', 'ball_l', 'rot'),
    ('toe.R', 'ball_r', 'rot'),
    ('shoulder.L', 'clavicle_l', 'rot'),
    ('shoulder.R', 'clavicle_r', 'rot'),
    ('upper_arm_fk.L', 'upperarm_l', 'rot'),
    ('upper_arm_fk.R', 'upperarm_r', 'rot'),
    ('forearm_fk.L', 'lowerarm_l', 'rot'),
    ('forearm_fk.R', 'lowerarm_r', 'rot'),
    ('hand_fk.L', 'hand_l', 'rot'),
    ('hand_fk.R', 'hand_r', 'rot'),

    ('neck', 'neck_01', 'rot'),
    ('rig.head', 'head', 'rot'),


    ('thumb.01.L', 'thumb_01_l', 'rot'),
    ('thumb.02.L', 'thumb_02_l', 'rot'),
    ('thumb.03.L', 'thumb_03_l', 'rot'),
    ('thumb.01.R', 'thumb_01_r', 'rot'),
    ('thumb.02.R', 'thumb_02_r', 'rot'),
    ('thumb.03.R', 'thumb_03_r', 'rot'),
    ('f_index.01.L', 'index_01_l', 'rot'),
    ('f_index.02.L', 'index_02_l', 'rot'),
    ('f_index.03.L', 'index_03_l', 'rot'),
    ('f_index.01.R', 'index_01_r', 'rot'),
    ('f_index.02.R', 'index_02_r', 'rot'),
    ('f_index.03.R', 'index_03_r', 'rot'),
    ('f_middle.01.L', 'middle_01_l', 'rot'),
    ('f_middle.02.L', 'middle_02_l', 'rot'),
    ('f_middle.03.L', 'middle_03_l', 'rot'),
    ('f_middle.01.R', 'middle_01_r', 'rot'),
    ('f_middle.02.R', 'middle_02_r', 'rot'),
    ('f_middle.03.R', 'middle_03_r', 'rot'),
    ('f_ring.01.L', 'ring_01_l', 'rot'),
    ('f_ring.02.L', 'ring_02_l', 'rot'),
    ('f_ring.03.L', 'ring_03_l', 'rot'),
    ('f_ring.01.R', 'ring_01_r', 'rot'),
    ('f_ring.02.R', 'ring_02_r', 'rot'),
    ('f_ring.03.R', 'ring_03_r', 'rot'),
    ('f_pinky.01.L', 'pinky_01_l', 'rot'),
    ('f_pinky.02.L', 'pinky_02_l', 'rot'),
    ('f_pinky.03.L', 'pinky_03_l', 'rot'),
    ('f_pinky.01.R', 'pinky_01_r', 'rot'),
    ('f_pinky.02.R', 'pinky_02_r', 'rot'),
    ('f_pinky.03.R', 'pinky_03_r', 'rot'),

    ('spine_fk', 'pelvis', 'rot'),
    ('spine_fk.001', 'spine_01', 'rot'),
    ('spine_fk.002', 'spine_02', 'rot'),
    ('spine_fk.003', 'spine_03', 'rot'),

    ('torso', 'pelvis', 'rot_loc'),
]

def create_helper_bones(source_armature, rig, mapping):
    oops.mode_set(mode = 'EDIT')
    matrices = {}
    vectors = {}
    for trg, src, type in mapping:
        matrices[trg] = rig.data.edit_bones[trg].matrix.copy()
        vectors[trg] = rig.data.edit_bones[trg].vector.copy()

    eb = source_armature.data.edit_bones
    for trg, src, type in mapping:
        parent_bone = eb[src]
        copy_name = trg + '.copy'
        if copy_name in eb:
            bone = eb[copy_name]
        else:
            bone = eb.new(copy_name)

        bone.matrix = matrices[trg]
        bone.head = parent_bone.head
        bone.tail = bone.head + vectors[trg]
        bone.parent = parent_bone



    return

# def create_rotation_constraint(source_armature, rig, source_bone, rig_bone):
    # return
ik_prop_bones = ['thigh_parent.L', 'thigh_parent.R', 'upper_arm_parent.L', 'upper_arm_parent.R']
def set_ik_fk(rig, value):
    for n in ik_prop_bones:
        rig.pose.bones[n]['IK_FK'] = value

def clear_constraints(bone):
    while len(bone.constraints) > 0:
        bone.constraints.remove(bone.constraints[0])

def create_constraints(source_armature, rig, mapping):
    oops.mode_set(mode = 'POSE')

    for trg, src, type in mapping:
        target_bone = rig.pose.bones[trg]
        clear_constraints(target_bone)
        constr = target_bone.constraints.new('COPY_ROTATION')
        constr.target = source_armature
        constr.subtarget = trg + '.copy'
        constr.target_space = constr.owner_space = 'LOCAL_WITH_PARENT'

        if type == 'rot_loc':
            constr = target_bone.constraints.new('COPY_LOCATION')
            constr.target = source_armature
            constr.subtarget = trg + '.copy'
            constr.target_space = constr.owner_space = 'LOCAL_WITH_PARENT'

class RetargetAnimationOperator(bpy.types.Operator):
    """Select imported skeleton with animation and rigify rig. Operator will retarget animation to rig"""
    bl_idname = "object.ocr_retarget_animation"
    bl_label = "(OCR) retarget animation"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and len(context.selected_objects) == 2
            and context.view_layer.objects.active
            and context.object.mode == 'OBJECT')

    def execute(self, context):
        selected = context.selected_objects
        rig, source = b_fun.get_rig_and_armature(context)

        create_helper_bones(source, rig, mapping)
        create_constraints(source, rig, mapping)

        set_ik_fk(rig, 1.0)

        source.select_set(False)
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
