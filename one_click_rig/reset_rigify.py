import bpy
from . import preferences
from . import bone_functions as b_fun

oops = bpy.ops.object
pops = bpy.ops.pose
aops = bpy.ops.armature

class ResetRigifyOperator(bpy.types.Operator):
    """Remove one click rig skeleton from the rigify rig"""
    bl_idname = "object.ocr_reset_rigify"
    bl_label = "Reset rigify"
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
        rig = context.view_layer.objects.active
        if  not 'one_click_rig' in rig.data:
            self.report({'ERROR'}, 'Rig doesn\'t contain one click rig armature')
            return {'FINISHED'}
        oops.mode_set(mode = 'EDIT')
        b_fun.switch_to_layer(rig.data, 24)

        aops.select_all(action = 'SELECT')
        bones = context.selected_editable_bones
        for b in bones:
            if b.name.endswith('.copy'):
                parent = b.parent
                parent.use_deform = True
                name = b.name.rstrip('.copy')
                b_fun.rename_childs_v_group(rig, name, parent.name)

            rig.data.edit_bones.remove(b)
        oops.mode_set(mode = 'OBJECT')
        b_fun.set_def_bones_deform(rig, True)
        b_fun.show_layers(rig, False)
        rig.data.bones['root'].use_deform = False
        rig.data.pop('one_click_rig')
        oops.mode_set(mode = 'POSE')
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)

class ApplyScaleRigifyOperator(bpy.types.Operator):
    """Applys scale to rigify rig"""
    bl_idname = "object.ocr_apply_scale_rigify"
    bl_label = "Apply scale to rigify"
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
        rig = context.view_layer.objects.active
        oops.transform_apply(scale = True, rotation = False, location = False)

        # https://www.reddit.com/r/blender/comments/eu3w6m/guide_how_to_scale_a_rigify_rig/
        for b in rig.pose.bones:
            for c in b.constraints:
                if c.type == "STRETCH_TO":
                    c.rest_length = 0
                    
        return {'FINISHED'}
