import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
import imageio
from datetime import datetime
import os
import subprocess
from OSC_sender import OSC


def make_video(experiment_root: str, time: str):
    # put all images together
    command = f"ffmpeg -framerate 30 -pattern_type glob -i '{experiment_root}/*.png' -c:v libx264 -pix_fmt yuv420p out_{time}.mp4"

    if subprocess.run(command, shell=True).returncode == 0:
        print("FFmpeg success")
    else:
        print("There was an error with ffmpeg")


def main():

    # setup experiment folder
    time = datetime.now().strftime("%m%d_%H%M%S")
    experiment_root = os.path.join("OUTPUT", time)
    os.mkdir(experiment_root)

    # setup config
    config = dict()
    config['ip'] = "127.0.0.1"                                  # the OSC server ip address
    config['port'] = 505                                        # The port the OSC server is listening to
    config['source_video'] = 'SOURCE/dynamic_clipped_short.MOV' # The port the OSC server is listening to

    osc = OSC(config)

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5,
                        min_tracking_confidence=0.5)

    count = 0
    cap = cv2.VideoCapture(config['source_video'])
    while cap.isOpened():
        # read frame
        _, frame = cap.read()
        try:
            # resize the frame for portrait video
            frame = cv2.resize(frame, (600, 350))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # convert to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # process the frame for pose detection
            pose_results = pose.process(frame_rgb)
            # print(pose_results.pose_landmarks)

            # draw skeleton on the frame
            mp_drawing.draw_landmarks(
                frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # extract information
            # listed here: https://developers.google.com/android/reference/com/google/mlkit/vision/pose/PoseLandmark
            rigthwrist_x = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x
            rigthwrist_y = pose_results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y

            osc.send("rightwrist_x", rigthwrist_x)
            osc.send("rightwrist_y", rigthwrist_y)

            # cv2.imshow('Output', frame)
            imageio.imwrite(f"{experiment_root}/frame{count:04}.png", frame)
            count += 1
        except:
            break

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    make_video()

if __name__ == "__main__":
    main()