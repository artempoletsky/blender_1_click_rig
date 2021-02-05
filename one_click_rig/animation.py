import bpy
from . import bone_functions as bf

poseOps = bpy.ops.pose
animOps = bpy.ops.anim
nlaOps = bpy.ops.nla
armOps = bpy.ops.armature
objOps = bpy.ops.object

class AddKeyFrameOperator(bpy.types.Operator):
    """Add keyframe to retargeted animation"""
    bl_idname = "anim.ocr_add_keyframe"
    bl_label = "(OCR) add keyframe"
    bl_options = {'REGISTER', 'UNDO'}

    # example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.object.mode == 'POSE')

    def execute(self, context):
        poseOps.visual_transform_apply()
        animOps.keyframe_insert_menu(type = 'LocRotScale')
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class BakeAnimationOperator(bpy.types.Operator):
    """Bake whole animation before export"""
    bl_idname = "anim.ocr_bake_animation"
    bl_label = "Bake animation for deform bones"
    bl_options = {'REGISTER', 'UNDO'}

    #example_prop: bpy.props.BoolProperty(name="Example prop", default=False)

    @classmethod
    def poll(cls, context):
        return (context.space_data.type == 'VIEW_3D'
            and context.view_layer.objects.active
            and context.object.mode == 'POSE')

    def execute(self, context):
        rig = context.object;

        objOps.mode_set(mode='OBJECT')
        objOps.select_all(action='DESELECT')
        rig.select_set(True);
        bf.show_all_layers(rig)
        objOps.mode_set(mode='POSE')

        deform_bones = [];
        non_deform_bones = [];
        for b in rig.data.bones:
            if b.use_deform:
                deform_bones.append(b.name)
            else:
                non_deform_bones.append(b.name)


        bf.select_bones(rig, deform_bones)
        #context.view_layer.update()
        #rig.data.bones.active = rig.data.bones['pelvis']
        #context.view_layer.update()

        #print(context.scene.frame_start)
        #return {'FINISHED'}
        nlaOps.bake(frame_start = context.scene.frame_start,
        frame_end = context.scene.frame_end,
        only_selected = True,
        clear_constraints= True,
        visual_keying = True,
        #use_current_action = True,
        bake_types = {'POSE'})

        #


        bf.select_bones(rig, non_deform_bones)

        objOps.mode_set(mode = 'EDIT')
        armOps.delete()
        objOps.mode_set(mode = 'OBJECT')
        for name in deform_bones:
            bone = rig.data.bones[name]
            bf.set_array_indices(bone.layers, [0])


            #print(bone.layers[0])
        #objOps.mode_set(mode = 'EDIT')
        #armOps.select_all(action = 'SELECT')
        objOps.mode_set(mode = 'POSE')
        bf.switch_to_layer(rig.data, 0)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)
