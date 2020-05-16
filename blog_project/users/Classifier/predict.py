#! /usr/bin/env python

import os
from multiprocessing.connection import Listener

from classifier import *


def main():
    # Set parameters
    net_h, net_w = 416, 416  # a multiple of 32, the smaller the faster
    obj_thresh, nms_thresh = 0.5, 0.45
    anchors = [
        17,
        18,
        28,
        24,
        36,
        34,
        42,
        44,
        56,
        51,
        72,
        66,
        90,
        95,
        92,
        154,
        139,
        281,
    ]

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    # Load the model
    infer_model = load_model("raccoon.h5", compile=False)

    address = ("localhost", 6007)  # family is deduced to be 'AF_INET'

    while True:
        try:
            # Get image path from socket
            listener = Listener(address, authkey=b"epicpass")
            conn = listener.accept()
            path = conn.recv()

            if path == "close":
                listener.close()
                return

            # Do detection on an image
            image = cv2.imread(path)

            # Predict the bounding boxes
            score = get_yolo_score(
                infer_model, [image], net_h, net_w, anchors, obj_thresh, nms_thresh
            )

            # Print the scores
            print(score)
            conn.send(score)
        except:
            print("Invalid path!")
            conn.send("Invalid path!")
        finally:
            listener.close()


if __name__ == "__main__":
    main()
