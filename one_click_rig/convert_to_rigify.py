import bpy
from . import preferences
from .map_bones import BoneMapping
from . import bone_functions as b_fun

oops = bpy.ops.object
pops = bpy.ops.pose
aops = bpy.ops.armature

class ConvertToRigifyOperator(bpy.types.Operator):
    """Convert character to rigify"""
    bl_idname = "object.ocr_convert_to_rigify"
    bl_label = "Convert UE character to rigify"
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
        armature_object = context.object
        parent = armature_object.parent
        mesh_object = armature_object.children[0]
        if parent:
            parent.select_set(True)
        mesh_object.select_set(True)

        oops.transform_apply(location = True, rotation = True, scale = True)
        if parent:
            parent.select_set(False)
        mesh_object.select_set(False)

        mapping = BoneMapping('uemannequin_rigify', False)
        mapping_reverse = BoneMapping('uemannequin_rigify', True)
        mapping.rename_armature(armature_object.data)
        oops.mode_set(mode = 'OBJECT')
        oops.ocr_generate_metarig()
        metarig = context.object
        oops.mode_set(mode = 'OBJECT')
        pops.rigify_generate()
        armature_object.select_set(True)
        mapping_reverse.rename_armature(armature_object.data)
        oops.mode_set(mode = 'OBJECT')
        oops.ocr_bind_rigify_to_armature()

        objs = bpy.data.objects

        objs.remove(armature_object)
        objs.remove(metarig)
        if parent:
            objs.remove(parent)
        # self.prefs = preferences.get_prefs()

        # self.report({'INFO'}, self.prefs.hello)
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


class ConvertToRigifyByMappingOperator(bpy.types.Operator):
    """Convert character to rigify"""
    bl_idname = "object.ocr_convert_to_rigify_by_mapping"
    bl_label = "Convert character to rigify by mapping"
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
        armature_object = context.object
        parent = armature_object.parent
        mesh_object = armature_object.children[0]
        if parent:
            parent.select_set(True)
        mesh_object.select_set(True)

        oops.transform_apply(location = True, rotation = True, scale = True)
        if parent:
            parent.select_set(False)
        mesh_object.select_set(False)

        ui = context.window_manager.one_click_rig_ui

        mapping = BoneMapping(ui.active_mapping, False)
        # mapping_reverse = BoneMapping(ui.active_mapping, True)
        mapping.rename_armature(armature_object.data)

        oops.mode_set(mode = 'OBJECT')
        oops.ocr_generate_metarig()
        metarig = context.object
        oops.mode_set(mode = 'OBJECT')
        pops.rigify_generate()
        rig = context.object
        rig.select_set(False)
        armature_object.select_set(True)
        context.view_layer.objects.active = armature_object
        aops.ocr_add_prefix(prefix = 'DEF-')
        armature_object.select_set(False)
        context.view_layer.objects.active = mesh_object
        mesh_object.select_set(True)
        oops.parent_clear(type = 'CLEAR')
        rig.select_set(True)
        context.view_layer.objects.active = rig
        oops.parent_set(type = 'ARMATURE')

        objs = bpy.data.objects

        objs.remove(armature_object)
        objs.remove(metarig)
        if parent:
            objs.remove(parent)

        mesh_object.select_set(False)
        oops.mode_set(mode = 'POSE')
        b_fun.prepare_rig(rig)

        return {'FINISHED'}
