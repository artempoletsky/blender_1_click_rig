import bpy
from . import preferences
from . import bone_functions as b_fun
from . import map_bones

oops = bpy.ops.object

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

        mapping = map_bones.load_mapping('rigify_uemannequin', anim = True)
        create_helper_bones(source, rig, mapping)
        create_constraints(source, rig, mapping)

        b_fun.set_ik_fk(rig, 1.0)

        source.select_set(False)
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
