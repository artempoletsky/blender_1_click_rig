import json
import bpy

class BoneMapping(object):
    """Map bones names from different rigs"""

    def __init__(self, json_source, reverse):

        try:
            with open(json_source) as json_file:
                data = json.load(json_file)
            # print(data)
            # print(234234)
            # print(self.filepath)
            # f = open(self.filepath)
            # data = f.read()
            # f.close()
        except Exception as e:
            print('Can\'t open json file')
            raise e

        mapping = {}
        for obj in data:
            for key in obj:
                val = obj[key]
                if reverse:
                    temp = key
                    key = val
                    val = temp
                mapping[key] = val
        self.mapping = mapping

    def get_name(self, name, safe = True):
        if name in self.mapping:
            return self.mapping[name]
        if safe:
            return name
        else:
            return None

    def rename_armature(self, armature):
        bpy.ops.object.mode_set(mode = 'EDIT')
        for bone in armature.edit_bones:
            bone.name = self.get_name(bone.name)
