import math

import cv2 as cv


def find_squares_hololens(image):
    """
    Returns sequence of squares detected on the image. Uses the same algorithm as the
    algorithm deployed on the hololens
    :param image: The mat to find squares in
    :return: A list of MatOfPoints referencing all squares
    """
    gray = cv.cvtColor(image, cv.COLOR_BGRA2GRAY)
    filtered = cv.bilateralFilter(gray, 15, 75, 75)
    edges = cv.Canny(filtered, 0, 50, 5)
    edges = cv.dilate(edges, None, 1)
    contours, _ = cv.findContours(edges, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    # Early exit if there are no contours to process
    if not contours:
        return []

    # test each contour
    contour_list = []
    for contour in contours:
        approx = cv.approxPolyDP(contour, cv.arcLength(contour, True) * 0.02, True)
        if len(approx) != 4 or abs(cv.contourArea(approx)) < 1000 or not cv.isContourConvex(approx): continue;
        contour_list.append(approx)

    return contour_list


def select_optimal_square(squares, bgra_mat, reference):
    if len(squares) == 0: return []
    valid_squares = list(
        filter(lambda square: __calculate_area(__order_points(square)) < 0.9 * __calculate_mat_area(bgra_mat), squares))
    if len(valid_squares) == 0: return []
    if not reference == (-1, -1):
        ordered = sorted(valid_squares, key=lambda square: __find_contour_distance(square, reference))
        valid_squares = list(filter(lambda square: __find_contour_distance(square, reference) >= 0, ordered))
        if len(valid_squares) == 0: return [ordered[0]]
    valid_squares = sorted(valid_squares, key=lambda square: __calculate_area(__order_points(square)))
    return [] if len(valid_squares) == 0 else [valid_squares[0]]


def __order_points(point_list):
    """
    Orders points by distance from the center of the point list
    :param point_list: Points to order
    :return: Ordered set of points
    """
    moments = cv.moments(point_list)
    center = (moments["m10"] / moments["m00"], moments["m01"] / moments["m00"])
    return sorted(point_list, key=lambda pt: math.atan2(pt[0][0] - center[0], pt[0][1] - center[1]))


def __find_contour_distance(point_list, reference):
    """
    Determines the distance between contours
    :param point_list: The contour list
    :param reference: The reference point
    :return: Distance
    """
    return cv.pointPolygonTest(point_list, reference, True)


def __calculate_mat_area(mat):
    """
    Calculates the area of a given mat
    :param mat: mat to calculate the area of
    :return: the area of the given mat
    """
    h, w, _ = mat.shape
    return h * w


def __calculate_area(point_list):
    """
    Calculates the area of the given point list
    :param point_list: Points list to calculate area
    :return: Area of the point list
    """

    # Add the first point to the end of the list
    pts = point_list + point_list[0]

    # Calculate the area
    area = 0
    for i in range(len(pts) - 1):
        area += (pts[i + 1][0][0] - pts[i][0][0]) * (pts[i + 1][0][1] + pts[i][0][1]) / 2
    return abs(area)


def __contour_angle(first, last, center):
    """
    Finds a cosine of angle between vectors from center->first and from center->last
    :param first: First point
    :param last: Last point
    :param center: Center point
    :return: The angle between vectors
    """
    dx1 = first.x - center.x
    dy1 = first.y - center.y
    dx2 = last.x - center.x
    dy2 = last.y - center.y
    return (dx1 * dx2 + dy1 * dy2) / math.sqrt((dx1 * dx1 + dy1 * dy1) * (dx2 * dx2 + dy2 * dy2) + 1e-10)
