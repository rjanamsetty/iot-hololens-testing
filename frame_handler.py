# Import appropriate modules
import csv
import time

import cv2
import numpy as np

# Compare two images using ORB feature matching with a Brute force matcher
import square_detection


def compare_images_bf(ref_img, comp_img):
    # Start time and get features
    start = time.time()
    comp_descriptors, comp_keypoints, ref_descriptors, ref_keypoints = orb_features(comp_img, ref_img)

    # Initalize the brute force detector (fastest combo with the ORB detector)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = matcher.match(ref_descriptors, comp_descriptors)

    # Draw the final image showing the ORB descriptors
    final_img = cv2.drawMatches(ref_img, ref_keypoints,
                                comp_img, comp_keypoints, matches, None)

    # Print statistics
    dist = [m.distance for m in matches]
    avg_dist = sum(dist) / len(dist)
    print("Matches Hamming Distance: " + str(avg_dist))
    print("Elapsed: " + str((time.time() - start) * 1000) + " ms")
    print("Matches: " + str(len(matches)))
    print("Percent Matched: " + str((len(matches) / len(ref_keypoints) * 100)))
    # Show image
    cv2.imshow("Matches", final_img)


# Compare two images using ORB feature matching with a FLANN matcher
def compare_images_flann(ref_img, comp_img):
    # Start time and get features
    comp_descriptors, comp_keypoints, ref_descriptors, ref_keypoints = orb_features(comp_img, ref_img)
    if comp_descriptors is None or ref_descriptors is None: return []

    # Initalize the FLANN matcher
    index_params = dict(algorithm=0, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(np.asarray(comp_descriptors,np.float32),np.asarray(ref_descriptors,np.float32), k=2)
    good_matches = []
    matches_mask = [[0, 0] for _ in range(len(matches))]
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.85 * n.distance:
            matches_mask[i] = [1, 0]
            good_matches.append(m)

    '''
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=(255, 0, 0),
                       matchesMask=matches_mask,
                       flags=0)

    final_img = cv2.drawMatchesKnn(ref_img, ref_keypoints, comp_img, comp_keypoints, matches, None, **draw_params)
    '''

    total = max(len(ref_descriptors), len(comp_descriptors))
    data = [len(matches), len(matches) / total * 100, len(good_matches), len(good_matches) / total * 100]

    #cv2.imshow("Matches", final_img)
    return data


def find_squares(ref_image, comp_img):
    h, w, _ = ref_image.shape
    center = (w / 2, h / 2)
    squares = square_detection.find_squares_hololens(ref_image)
    possible = square_detection.select_optimal_square(squares, ref_image, center)
    if len(possible) == 0: return []
    (x, y, w, h) = cv2.boundingRect(possible[0])
    crop_img = ref_image[y:y + h, x:x + w]
    return compare_images_flann(comp_img, crop_img)


def orb_features(comp_img, ref_img):
    # Convert given images to grayscale
    ref_bw = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
    comp_bw = cv2.cvtColor(comp_img, cv2.COLOR_BGR2GRAY)
    # Initialize the ORB detector algorithm
    orb = cv2.ORB_create()
    # Now detect the keypoints and compute the ORB descriptors for each image
    ref_keypoints, ref_descriptors = orb.detectAndCompute(ref_bw, None)
    comp_keypoints, comp_descriptors = orb.detectAndCompute(comp_bw, None)
    return comp_descriptors, comp_keypoints, ref_descriptors, ref_keypoints


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('Running the script')

    # define a video capture object
    vid = cv2.VideoCapture(1)

    # Raise errors if the video capture object is not available
    if not vid.isOpened():
        raise IOError("Cannot open webcam")
    record = False

    while True:

        # Capture the video frame by frame
        ret, frame = vid.read()
        if not ret:
            print("Can't receive frame")
            break

        # comp_img = cv2.resize(frame, (200, 200))

        # Perform feature extraction
        ref = cv2.imread('vegas.png')
        ref_max = max(ref.shape[0], ref.shape[1])
        ref_dim = (ref.shape[0] * 200 / ref_max, ref.shape[1] * 200 / ref_max)
        ref_img = cv2.resize(ref, (200, 200))
        find_squares(frame, ref_img, record)

        # Enable c as record button
        record = cv2.waitKey(1) & 0xFF == ord('c')

        # Enable q as escape button
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # After the loop release the cap object and destroy all the windows
    vid.release()
    cv2.destroyAllWindows()
