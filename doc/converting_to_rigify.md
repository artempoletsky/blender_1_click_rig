# Converting to rigify

## Unreal characters workflow
### Convert UE character to rigify

A combination of 4 operators:

1. Rename armature by mapping to the rigidy names. The default `uemannequin_rigify` mapping will be used. If you delete `uemannequin_rigify` mapping, the script won't work. 
2. Generate metarig from armature
3. Rigify generate rig. Standart rigify button. 
4. Rename the original armature backwards to the original UE names.
5. Bind the rigify rig to the armature

Usage: select unreal armature and run operator

If you want to edit the metarig for characters that don't match the unreal mannequin bone structure, then you need to run this operators separately.

### Rename armature by mapping. 
Go to [mappings page](./doc/mappings.md)

### Generate metarig from armature

Creates rigify metarig using as input other armature with rigify names.

Usage: select an armature and run operator. 

Props: 
head_chain_length - you can specify the length of rigify `spines.super_head` sample. E.g. for unreal mannequin it will be default 2 (`neck_01` and `head` bones).

Features: 
1. Auto align and roll bones. 
2. For hand the script will compute rolls accordingly to position of `hand.{Suffix}`, `f_index.{Suffix}`, `f_middle.{Suffix}`, `f_ring.{Suffix}` bones. 
If one of the bones is missing, the script won't work.
3. For toes the script will try to compute position of the end toe bone accordingly to the child mesh object.
If mesh object doesn't have weight painted toes, they size and position likely will be wrong. 

### Bind rigify rig to armature

Copies the unreal armature to the rigify rig and makes constraints. 

Original unreal armature will be copied on 24 layer of rigify rig. And will copy all transforms from the rigify.

Usage: 
1. select unreal armature
2. select rigify rig.
3. run operator. 

Only unreal armatures supported for now.

### Other characters workflow

Prepare character for the script. 

1. An armature need to have 10 fingers, 3 bones each. 
2. 2 arms, 2 legs. 3 bones for the each limb is required. Also the armature can have twist bones for limbs.
3. Spine should contain 4 bones, and one neck bone and one head. 
4. Separate toes and face rig is not supported for now. 
5. Character can have breast bones.

If bones with this structure is named properly, and you have related mapping. You can just select related mapping and press `Convert character to rigify by mapping`

## Convert character to rigify by mapping

A combination of 4 operations:

1. Rename armature by mapping. Same as unreal.
2. Generate metarig from armature. Same as unreal.
3. Rigify generate rig. Standart rigify button. 
4. Then the script will add rigify `DEF-` prefix to the armature bones and replace it with generated rigify rig. 

Now you have a rigify character. 
