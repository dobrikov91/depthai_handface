from HandFaceTracker import HandFaceTracker
from HandFaceRenderer import HandFaceRenderer
from zmq_pub import ZmqPub
from panda3d.core import LPoint3, Quat
import math

tracker = HandFaceTracker(
        double_face=True,
        use_face_pose=True,
        nb_hands=0,
        xyz=True,
    )

renderer = HandFaceRenderer(
        tracker=tracker)
renderer.show_metric_landmarks = False

zmqPub = ZmqPub("P")

def convert_to_quaternion(pose_mat):
        # Per issue #2, adding a abs() so that sqrt only results in real numbers
        r_w = math.sqrt(abs(1+pose_mat[0][0]+pose_mat[1][1]+pose_mat[2][2]))/2
        r_x = (pose_mat[2][1]-pose_mat[1][2])/(4*r_w)
        r_y = (pose_mat[0][2]-pose_mat[2][0])/(4*r_w)
        r_z = (pose_mat[1][0]-pose_mat[0][1])/(4*r_w)

        return [r_w,r_x,r_y,r_z]

def convert(pos, mat):
    newPos = LPoint3(-pos[0] / 1000, -pos[2] / 1000, pos[1] / 1000)

    oakPos = convert_to_quaternion(mat)
    quat = Quat(oakPos[3], -oakPos[2], oakPos[0], oakPos[1]) # almost working
    # silly hack
    rot = quat.getHpr()
    rot[0] += 180
    rot[0] *= -1
    rot[2] *= -1
    quat.setHpr(rot)

    return [*newPos, *quat]

while True:
    frame, faces, hands = tracker.next_frame()

    for face in faces:      
        print(convert(face.xyz, face.pose_transform_mat))
        pos = convert(face.xyz, face.pose_transform_mat)
        zmqPub.sendDoubles(pos)

    if frame is None: break
    # Draw face and hands
    frame = renderer.draw(frame, faces, hands)
    key = renderer.waitKey(delay=1)
    if key == 27 or key == ord('q'):
        break
renderer.exit()
tracker.exit()
