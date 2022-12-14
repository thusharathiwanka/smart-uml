import math

import cv2
import keras_ocr
import numpy as np

import app
from config.database import db
from models.actor_and_use_case import ActorANDUseCase
from decimal import Decimal

from models.extend_relationship import ExtendRelationship
from models.include_relationship import IncludeRelationship


def detect_extend_include_relationship(filename, boxes, accurate_indexes, use_case_id, category_index, class_id):
    image = cv2.imread(app.SUBMISSION_PATH + '/' + filename)
    height, width, c = image.shape
    use_case_objects = ActorANDUseCase.query.filter_by(use_case_answer=use_case_id, type='use case').all()

    for i in range(0, len(accurate_indexes)):

        if category_index[class_id[i]]['name'] == 'relationship':
            ymin = boxes[i][0] * height
            xmin = boxes[i][1] * width
            ymax = boxes[i][2] * height
            xmax = boxes[i][3] * width

            crop_img = image[int(ymin):int(ymax), int(xmin):int(xmax)]

            r_type = text_detection(crop_img)
            line_recovery_image = line_recovery(crop_img)

            gray_image = cv2.cvtColor(line_recovery_image, cv2.COLOR_BGR2GRAY)
            _, thresh_image = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY_INV)
            arrow_image = get_filter_arrow_image(thresh_image)

            if arrow_image is not None:
                arrow_info_image, point1, point2 = get_arrow_info(arrow_image)

                point1_x = int(xmin) + point1[0]
                point1_y = int(ymin) + point1[1]
                point2_x = int(xmin) + point2[0]
                point2_y = int(ymin) + point2[1]

                line_point1 = (point1_x, point1_y)
                line_point2 = (point2_x, point2_y)

                u1_object = find_closest_components_length(line_point1, use_case_objects)

                u2_object = find_closest_components_length(line_point2, use_case_objects)

                if (r_type == 'include'):
                    include_obj = IncludeRelationship(use_case_answer=use_case_id,
                                                      connected_component_01=u1_object.id,
                                                      connected_component_02=u2_object.id)
                    db.session.add(include_obj)
                    db.session.commit()

                if (r_type == "extend"):
                    extend_obj = ExtendRelationship(use_case_answer=use_case_id,
                                                    connected_component_01=u1_object.id,
                                                    connected_component_02=u2_object.id)
                    db.session.add(extend_obj)
                    db.session.commit()


def line_recovery(img):
    kernel1 = np.ones((3, 5), np.uint8)
    kernel2 = np.ones((9, 9), np.uint8)

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBW = cv2.threshold(imgGray, 230, 255, cv2.THRESH_BINARY_INV)[1]

    img1 = cv2.erode(imgBW, kernel1, iterations=1)
    img2 = cv2.dilate(img1, kernel2, iterations=3)
    img3 = cv2.bitwise_and(imgBW, img2)
    img3 = cv2.bitwise_not(img3)
    img4 = cv2.bitwise_and(imgBW, imgBW, mask=img3)
    imgLines = cv2.HoughLinesP(img4, 1, np.pi / 180, 20, minLineLength=0, maxLineGap=5)

    for i in range(len(imgLines)):
        for x1, y1, x2, y2 in imgLines[i]:
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 0), 2)

    return img


def text_detection(c_img):
    pipeline = keras_ocr.pipeline.Pipeline()

    prediction_groups = pipeline.recognize([c_img])

    for prg in prediction_groups[0]:
        print(prg[0])
        if prg[0].find('clu') >= 0:
            return "include"
        else:
            if prg[0].find('ten') >= 0:
                return "extend"


def get_filter_arrow_image(threslold_image):
    blank_image = np.zeros_like(threslold_image)

    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    threslold_image = cv2.dilate(threslold_image, kernel_dilate, iterations=1)

    contours, hierarchy = cv2.findContours(threslold_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is not None:

        threshold_distnace = 100

        for cnt in contours:
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)
            if defects is not None:
                for i in range(defects.shape[0]):
                    start_index, end_index, farthest_index, distance = defects[i, 0]

                    if distance > threshold_distnace:
                        cv2.drawContours(blank_image, [cnt], -1, 225, -1)

        return blank_image
    else:
        return None


def get_length(p1, p2):
    line_length = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
    return line_length


def find_max_length(contours):
    max_lenth = 0

    for cnt in contours:
        p1, p2 = get_max_distace_point(cnt)
        line_length = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

        if line_length > max_lenth:
            max_lenth = line_length

    return max_lenth


def get_max_distace_point(cnt):
    max_distance = 0
    max_points = None
    for [[x1, y1]] in cnt:
        for [[x2, y2]] in cnt:
            distance = get_length((x1, y1), (x2, y2))

            if distance > max_distance:
                max_distance = distance
                max_points = [(x1, y1), (x2, y2)]

    return max_points


def angle_beween_points(a, b):
    arrow_slope = (a[0] - b[0]) / (a[1] - b[1])
    arrow_angle = math.degrees(math.atan(arrow_slope))
    return arrow_angle


def get_arrow_info(arrow_image):
    arrow_info_image = cv2.cvtColor(arrow_image.copy(), cv2.COLOR_GRAY2BGR)
    contours, hierarchy = cv2.findContours(arrow_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if hierarchy is not None:

        max_lenth = find_max_length(contours)

        for cnt in contours:

            blank_image = np.zeros_like(arrow_image)
            cv2.drawContours(blank_image, [cnt], -1, 255, -1)

            point1, point2 = get_max_distace_point(cnt)

            lenght = get_length(point1, point2)

            if lenght == max_lenth:
                cv2.circle(arrow_info_image, point1, 2, (255, 0, 0), 3)
                cv2.circle(arrow_info_image, point2, 2, (255, 0, 0), 3)

                cv2.putText(arrow_info_image, "point 1 : %s" % (str(point1)), point2, cv2.FONT_HERSHEY_PLAIN, 0.8,
                            (0, 0, 255), 1)
                cv2.putText(arrow_info_image, "point 2 : %s" % (str(point2)), (point2[0], point2[1] + 20),
                            cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 255), 1)

                return arrow_info_image, point1, point2
    else:
        return None, None


def find_closest_components_length(point, use_case_objects):
    u_object = 0
    min_length = 1000000000000
    for obj in use_case_objects:

        ymin = Decimal(obj.y_min)
        xmin = Decimal(obj.x_min)
        ymax = Decimal(obj.y_max)
        xmax = Decimal(obj.x_max)

        usecase_x = xmin + (xmax - xmin) / 2
        usecase_y = ymin + (ymax - ymin) / 2

        usecase_point = (int(usecase_x), int(usecase_y))

        l_length = ((point[0] - usecase_point[0]) ** 2 + (point[1] - usecase_point[1]) ** 2) ** 0.5

        if min_length > l_length:
            min_length = l_length
            u_object = obj

    return u_object
