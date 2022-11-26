# import the required library
import numpy as np
import cv2
from matplotlib import pyplot as plt
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import msvcrt

write_flag = 0

class HTTPRequestHandler(BaseHTTPRequestHandler):
    """Extend SimpleHTTPRequestHandler to handle PUT requests"""

    def do_PUT(self):
        self.send_response(201, 'Created')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        file_length = int(self.headers['Content-Length'])
        body = self.rfile.read(file_length)
        self.wfile.write(body)
        print("PUT Received: ", body)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(centroid_str, encoding='utf8'))
        print('Write data: ' + centroid_str)

        #if write_flag == 1:
        #    print('Write data: ' + str(centroid))
        #    self.wfile.write(centroid)
        #    write_flag = 0

def start_server():
    print("HTTP is running")
    httpd.serve_forever()

def filter_matches(all_matches, MIN_MATCH_COUNT, keyObj, keyScene):
    # Store all the good matches as per Lowe's ratio test
    good_matches = []
    for m, n in all_matches:
        if m.distance < 1.0 * n.distance:
            good_matches.append(m)

    if len(good_matches) > MIN_MATCH_COUNT:
        src_pts = np.float32([keyObj[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keyScene[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        h, w = imgObj.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        #imgScene = cv2.polylines(imgScene, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
        print("{} matches are found".format(len(good_matches)))
        print(dst)  # print four corners of the detected object

    else:
        print("Not enough matches are found - {}/{}".format(len(good_matches), MIN_MATCH_COUNT))
        matchesMask = None

    return dst, matchesMask

############################################################
OPTS_FEATURE = 'SIFT'
OPTS_FLANN = True
OPTS_KNN_MATCH = False

imgObj = cv2.imread('color_fundus_zoomedin_Sensys.jpg', cv2.IMREAD_GRAYSCALE)
imgScene = cv2.imread('color_fundus.jpg', cv2.IMREAD_GRAYSCALE)

stdShape = (1200, 1200)
#imgScene = cv2.resize(imgScene, stdShape)
imgObj = cv2.resize(imgObj, stdShape)

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
imgObj = clahe.apply(imgObj)
imgObj2 = imgObj
imgScene = clahe.apply(imgScene)
imgScene2 = imgScene

if OPTS_FEATURE == 'SURF':
    detector = cv2.xfeatures2d.SURF_create(400)
    keyObj, featObj = detector.compute(imgObj, None)
    keyScene, featScene = detector.compute(imgScene, None)
elif OPTS_FEATURE == 'SIFT':
    detector = cv2.SIFT_create()
    keyObj, featObj = detector.detectAndCompute(imgObj, None)
    keyScene, featScene = detector.detectAndCompute(imgScene, None)
elif OPTS_FEATURE == 'ORB':
    detector = cv2.ORB_create(1000)
    keyObj, featObj = detector.compute(imgObj, None)
    keyScene, featScene = detector.compute(imgScene, None)
elif OPTS_FEATURE == 'BRISK':
    detector = cv2.BRISK_create()
elif OPTS_FEATURE == 'AKAZE':
    detector = cv2.AKAZE_create()
elif OPTS_FEATURE == 'KAZE':
    detector = cv2.KAZE_create()
elif OPTS_FEATURE == 'BEBLID':
    detector = cv2.xfeatures2d.BEBLID_create(0.75)
    keyObj, featObj = detector.compute(imgObj, None)
    keyScene, featScene = detector.compute(imgScene, None)
else:
    print('unrecognized feature: %s', OPTS_FEATURE)

FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(featObj, featScene, k=2)

# for ORB, use the Brute Force with Hamming Distance
#matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_BRUTEFORCE_HAMMING)
#matches = matcher.knnMatch(featObj, featScene, k=2)

MIN_MATCH_COUNT = 1

# Store all the good matches as per Lowe's ratio test
good_matches = []
for m, n in matches:
    if m.distance < 1.0 * n.distance:
        good_matches.append(m)

if len(good_matches) > MIN_MATCH_COUNT:
    src_pts = np.float32([keyObj[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keyScene[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matchesMask = mask.ravel().tolist()

    h, w = imgObj.shape
    pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    dst_center = (dst[0] + dst[1] + dst[2] + dst[3]) // 4
    dst_center = np.int32(dst_center[0])
    dst_radius = np.int32(((dst[1, 0][1]-dst[0, 0][1]) + (dst[2, 0][0]-dst[0, 0][0])) // 4)
    print(dst_center)
    cv2.circle(imgScene, dst_center, radius=dst_radius, color=(0, 255, 0), thickness=10)
    #imgScene = cv2.polylines(imgScene, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

    print("{} matches are found".format(len(good_matches)))
    #print(dst)  # print four corners of the detected object

else:
    print("Not enough matches are found - {}/{}".format(len(good_matches), MIN_MATCH_COUNT))
    matchesMask = None

centroid = (dst[0] + dst[1] + dst[2] + dst[3]) // 4
centroid_str = str(np.int32(centroid[0, 0])) + ', ' + str(np.int32(centroid[0, 1])) + ', ' + str(np.int32(dst_radius))
print(centroid_str)

# crop an image based on the four corners detected
#mag_img = imgScene[dst[0, 0][1]:dst[1, 0][1], dst[0, 0][0]:dst[2, 0][0]]

# Draw inliners or matching keypoints
draw_params = dict(matchColor=(0, 255, 0),    # draw matches in red color
                   singlePointColor=None,
                   matchesMask=matchesMask,   # draw only inliners
                   flags=2)
img_final = cv2.drawMatches(imgObj, keyObj, imgScene, keyScene, good_matches, None, **draw_params)
plt.imshow(img_final, 'gray')
plt.show()

httpd = HTTPServer(("10.197.169.102", 8000), HTTPRequestHandler)
threading.Thread(target=start_server()).start()

write_flag = 1
