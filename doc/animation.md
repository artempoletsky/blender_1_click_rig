# Animation operators

## (OCR) retariget animation

Or `Retarget animation` button. 

Retargets animation by `animation mapping` from one skeleton to another. 

Creating and editing animation mappings is not realized yet. 
The addon has only one mapping internaly. It's UE mannequin to Rigify FK bones. 

Usage: select rigify rig and source armature, run operator.

Props: 
1. Set animation length - Set the length of the scene animation is equal to the length of the source animation.

The operator creates `copy of FK bones` from the Rigify rig inside of source skeleton and parents them by mapping.

In the Rigify rig it creates constraints from `copy bones` to the rig. 

Tou can create keyframes by pressing the `Add keyframe` button. And then delete source armature, when it not needed anymore. 

## (OCR) add keyframe

Or `Add keyframe button`.

Bakes constrained bone position to the pose. 

A combination of two operators:
1. Ctrl + A -> Apply Visual Transform to pose
2. I(Insert keyframe menu) -> LocRotScale
