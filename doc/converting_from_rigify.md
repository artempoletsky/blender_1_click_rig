# Converting from rigify

Only unreal mannequin-like characters are supported for now. 

## Pose character to mannequin pose

Matches the rigify character with the unreal mannequin default pose.

Valid pose needs for correct work of the [unreal retargeting system](https://docs.unrealengine.com/en-US/Engine/Animation/AnimationRetargeting/index.html) 

The pose will be baked to the armature(edit mode). This is not an animation tool.

Usage: select rigify rig and run operator. 

Better not using this rig for animation and export character to FBX and reimport as unreal character and regenerate rig. It has some issues with IK and finger controls.

How it works: the script inside have rigifyed ue mannequin pose and it copies rotation of fk bones to the rig. If rig have extra bones they will be ignored. 

Different poses will be added later probably.

## Add unreal skeleton to rig

Creates unreal mannequin bones inside of rigify rig.

Usage: select **POSED**(chapter above) rigify character and run operator. 

How it works: the script inside have a template of unreal mannequin. For each `DEF` bone it will create matching unreal bone according of `uemqnnequin_rigify` default mapping. 

If bone not in the mapping, it will be copied as is. 

Also default mannequin IK bones will be added and constrained to the foot/hand bones.

Vertex groups of child meshes will be renamed according to the mapping.

You can export this character to the unreal and it should support all default mannequin animations. 

## Reset rigify

Opposite of `Add unreal skeleton to rig`. It will delete unreal armature from the rig. 

## Apply scale to rigify

Applies the scale and fixes the `stretch to` constraints. 

Use this if you want to convert rigify character created in the default blender units.
1. Change the scene unit scale to 0.01
2. Scale rig to 100. Or whatever you want.
3. Run operator.
