import cv2
import base64
from multiprocessing import Process, Value
import time

import numpy as np
'''
def register_owner(owner_id):
    img = pyqrcode.create(owner_id)
    img.png(owner_id + '.png', scale=8)
    img.show()
'''

def tracking_loop_QR(camera, bbox_shared, frame_base64, track_status, deviation_angle, desired_speed, max_speed, owner_id="abcd"):
    def calc_deviation_angle(bbox, size):
        x, y = bbox
        width, height = size
        return (x - width / 2) / width * 45
    
    def tilt_correction(frame, angle):
        angle = np.deg2rad(angle)
        height, width = frame.shape[:2]
        src_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        dst_points = np.float32([
        [0, height * np.sin(angle)], 
        [width, height * np.sin(angle)], 
        [0, height], 
        [width, height]
    ])
        perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        return cv2.warpPerspective(frame, perspective_matrix, (width, height))

    decoder = cv2.QRCodeDetector()
    vid = cv2.VideoCapture(camera)
    
    IMG_WIDTH = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    LOST_PERIOD = 5
    track_status.value = 0
    found_obj = False

    # iterative variables
    lost_count = 0
    cur_dev = 0

    while True:
        ret, frame = vid.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame = tilt_correction(frame, -20)

        data, points, _ = decoder.detectAndDecode(frame)

        if points is not None:
            #for de_qr_code in info:
                if data == owner_id:
                    # owner (owner_id) found at (center)
                    found_obj = True
                    #index = info.index(owner_id)
                    #points = points[index]
                    points = points[0]
                    center = np.array(points).mean(axis=0)
                    
                    # calculate deviation angle
                    cur_dev = calc_deviation_angle(center, (IMG_WIDTH, IMG_HEIGHT))

                    # draw boudning box around the owner QR code
                    for i in range(len(points)):
                        pt1 = [int(val) for val in points[i]]
                        pt2 = [int(val) for val in points[(i + 1) % 4]]
                        pt1 = tuple(pt1)
                        pt2 = tuple(pt2)
                        cv2.line(frame, pt1, pt2, color=(255, 0, 0), thickness=3)

        if found_obj:
            # tracker found the owner
            found_obj = False
            deviation_angle.value = cur_dev 
            desired_speed.value = max_speed.value
            track_status.value = 1
            lost_count = 0
        else:
            # owner lost!
            lost_count += 1
            if lost_count > LOST_PERIOD:
                track_status.value = 0

        cur_dev = 0
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


def tracking_loop(camera, bbox_shared, frame_base64, track_status, deviation_angle, desired_speed, max_speed):
    def scale_bbox(bbox_shared, size):
        bbox = [b for b in bbox_shared]
        bbox[0] *= size[0]
        bbox[1] *= size[1]
        bbox[2] *= size[0]
        bbox[3] *= size[1]
        x = (bbox[0] + bbox[2])/2 - 180
        y = (bbox[1] + bbox[3])/2 - 180
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        return (x,y,w,h)

    def calc_deviation_angle(bbox, size):
        x, y, w, h = bbox
        width, height = size
        return (x - width / 2) / width * 90

    INACTIVE = 0
    ACTIVE = 1
    HAS_BBOX = 2
    video = cv2.VideoCapture(camera)
    IMG_WIDTH = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    tracker = cv2.TrackerCSRT_create()
    init = False
    while True:
        ret, frame = video.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        if track_status.value == HAS_BBOX:
            init = True
            track_status.value = INACTIVE
        if init:
            if track_status.value == INACTIVE:
                bbox = scale_bbox(bbox_shared, (IMG_WIDTH, IMG_HEIGHT))
                tracker.clear()
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, bbox)
                track_status.value = ACTIVE
            elif track_status.value == ACTIVE:
                ret, bbox = tracker.update(frame)
                if ret:
                    # Draw the bounding box on the frame
                    x, y, w, h = map(int, bbox)
                    deviation_angle.value = calc_deviation_angle(bbox, (IMG_WIDTH, IMG_HEIGHT))
                    desired_speed.value = 0.5
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    # Display a message if tracking fails
                    cv2.putText(frame, "Tracking failed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


def tracking_loop_meta(camera, bbox_shared, frame_base64, track_status, deviation_angle, desired_speed, max_speed, owner_id="abcd"):
    def calc_deviation_angle(bbox, size):
        x, y, w, h = bbox
        width, height = size
        return (x+w/2 - width/2) / width * 90
        
    def tilt_correction(frame, angle):
        angle = np.deg2rad(angle)
        height, width = frame.shape[:2]
        src_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        dst_points = np.float32([
        [0, height * np.sin(angle)], 
        [width, height * np.sin(angle)], 
        [0, height], 
        [width, height]
    ])
        perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        return cv2.warpPerspective(frame, perspective_matrix, (width, height))

    decoder = cv2.QRCodeDetector()
    vid = cv2.VideoCapture(camera)
    tracker = cv2.TrackerCSRT_create()
    
    IMG_WIDTH = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    IMG_HEIGHT = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    LOST_PERIOD = 8
    track_status.value = 0
    found_obj = False
    bbox_update = False
    tracker_init = False

    # iterative variables
    lost_count = 0
    cur_dev = 0

    while True:
        ret, frame = vid.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        #frame = tilt_correction(frame, -20)

        data, info, points, _ = decoder.detectAndDecodeMulti(frame)

        if points is not None:
            for de_qr_code in info:
                if de_qr_code == owner_id:
                    # owner (owner_id) found at (center)
                    found_obj = True
                    lost_count = 0
                    bbox_update = True

                    index = info.index(owner_id)
                    points = points[index]
                    #points = points[0]
                    center = np.array(points).min(axis=0)
                    w = int(((points[2][0] - points[3][0])**2 + (points[2][1] - points[3][1])**2)**0.5)
                    h = int(((points[2][0] - points[1][0])**2 + (points[2][1] - points[1][1])**2)**0.5)
                    bbox = (center[0], center[1], w, h)
                    # calculate deviation angle
                    cur_dev = calc_deviation_angle(bbox, (IMG_WIDTH, IMG_HEIGHT))

                    # draw boudning box around the owner QR code
                    for i in range(len(points)):
                        pt1 = [int(val) for val in points[i]]
                        pt2 = [int(val) for val in points[(i + 1) % 4]]
                        pt1 = tuple(pt1)
                        pt2 = tuple(pt2)
                        cv2.line(frame, pt1, pt2, color=(255, 0, 0), thickness=3)

        else:
            if bbox_update:
                tracker_init = True
                bbox_update = False
                tracker.clear()
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, bbox)

            if tracker_init:
                found_obj = True
                ret, bbox = tracker.update(frame)
                lost_count += 1
                if ret:
                    # Draw the bounding box on the frame
                    x, y, w, h = map(int, bbox)
                    cur_dev = calc_deviation_angle(bbox, (IMG_WIDTH, IMG_HEIGHT))
                    #desired_speed.value = 0.5
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    # Display a message if tracking fails
                    cv2.putText(frame, "Tracking failed!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    track_status.value = 0    

        if found_obj:
            # tracker found the owner
            found_obj = False
            deviation_angle.value = cur_dev 
            desired_speed.value = max_speed.value
            track_status.value = 1

        if lost_count > LOST_PERIOD:
            track_status.value = 0
            bbox_update = False
            tracker_init = False

        cur_dev = 0
        frame = cv2.resize(frame, (380, int(380*9/16)))
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


def tracking_loop_debug(camera, bbox, frame_base64, track_status, deviation_angle, desired_speed, max_speed):
    video = cv2.VideoCapture(camera)
    while True:
        ret, frame = video.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frame_base64.value = base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode("utf-8")


class Tracker:
    def __init__(self, bbox_input, frame_base64, track_status, max_speed, camera=0):
        self.camera = camera
        self.frame_base64 = frame_base64
        self.bbox = bbox_input
        self.track_status = track_status
        self.deviation_angle = Value('f', 0.0)
        self.desired_speed = Value('f', 0.0)
        self.max_speed = max_speed
        self.thread = Process(target=tracking_loop_meta, args=(self.camera, self.bbox, self.frame_base64, self.track_status, self.deviation_angle, self.desired_speed, self.max_speed))
        self.thread.start()

    def stop(self):
        self.thread.terminate()

    def get_frame_base64(self):
        return self.frame_base64.value
    
    def get_deviation_angle(self):
        return self.deviation_angle.value
    
    def get_desired_speed(self):
        return self.desired_speed.value
