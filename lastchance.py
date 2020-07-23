
import json
if __name__ == '__main__':
    data = '''{'poses': (Pose:
    translation.x : -0.7215400926577586
    translation.y : -0.5520699698539067
    translation.z : 0.16894348129149322
    quaternion.w : 0.7585280363283299
    quaternion.x : -0.282578330390553
    quaternion.y : 0.002227979455766831
    quaternion.z : 0.5871794797207412
    frame_id : world, Pose:
    translation.x : -0.6277724910363291
    translation.y : -0.4924484798711226
    translation.z : 0.17069346334685823
    quaternion.w : 0.7553498944505329
    quaternion.x : -0.29278859248733835
    quaternion.y : 0.012784967774539208
    quaternion.z : 0.5861381421319178
    frame_id : world, Pose:
    translation.x : -0.3330618574341937
    translation.y : 0.009741986778691387
    translation.z : 0.11748772646138031
    quaternion.w : 0.458446656061056
    quaternion.x : -0.2290388700928738
    quaternion.y : -0.056464282459656505
    quaternion.z : 0.8568428352617136
    frame_id : world, Pose:
    translation.x : -0.3196255256807796
    translation.y : 0.12301205480512556
    translation.z : 0.10751975238666946
    quaternion.w : 0.4502608609318504
    quaternion.x : -0.20635556236623814
    quaternion.y : -0.03440418621181797
    quaternion.z : 0.8680431388845403
    frame_id : world, Pose:
    translation.x : -0.6449054660605258
    translation.y : 0.5879777199515429
    translation.z : 0.3875616143828583
    quaternion.w : 0.08017001850107502
    quaternion.x : -0.13690154451142675
    quaternion.y : -0.2699350952555821
    quaternion.z : 0.9497187897442502
    frame_id : world, Pose:
    translation.x : -0.6702215702639835
    translation.y : 0.6381957831800311
    translation.z : 0.19829947891395622
    quaternion.w : 0.041802229306180556
    quaternion.x : -0.23117476871452694
    quaternion.y : -0.16947171245301695
    quaternion.z : 0.9571259784443532
    frame_id : world), 'joint_values': (JointValues:
    shoulder_pan_joint : 3.7256338596343994
    shoulder_lift_joint : -0.15768033662904912
    elbow_joint : 0.28905153274536133
    wrist_1_joint : 4.6227126121521
    wrist_2_joint : -4.13453179994692
    wrist_3_joint : 2.315901756286621, JointValues:
    shoulder_pan_joint : 3.7300822734832764
    shoulder_lift_joint : -0.5408313910113733
    elbow_joint : 1.0859284400939941
    wrist_1_joint : 4.18250036239624
    wrist_2_joint : -4.112954918538229
    wrist_3_joint : 2.3031535148620605, JointValues:
    shoulder_pan_joint : 2.762056350708008
    shoulder_lift_joint : -1.1588199774371546
    elbow_joint : 2.6742208003997803
    wrist_1_joint : 3.6699395179748535
    wrist_2_joint : -4.775107685719625
    wrist_3_joint : 4.086153507232666, JointValues:
    shoulder_pan_joint : 2.405630350112915
    shoulder_lift_joint : -1.0601447264300745
    elbow_joint : 2.645905017852783
    wrist_1_joint : 3.515446662902832
    wrist_2_joint : -4.885514203702108
    wrist_3_joint : 4.449174404144287, JointValues:
    shoulder_pan_joint : 2.228983163833618
    shoulder_lift_joint : -0.3745339552508753
    elbow_joint : 0.23813867568969727
    wrist_1_joint : 4.602029800415039
    wrist_2_joint : -5.2783653179751795
    wrist_3_joint : 5.531320095062256, JointValues:
    shoulder_pan_joint : 2.215242385864258
    shoulder_lift_joint : -0.08709317842592412
    elbow_joint : 0.06842470169067383
    wrist_1_joint : 4.764069557189941
    wrist_2_joint : -5.28887921968569
    wrist_3_joint : 5.543368339538574)}'''

    j = json.loads(data)
    print(j)