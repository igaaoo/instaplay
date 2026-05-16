# Keypoint indices — COCO format used by YOLOv8 pose
LEFT_SHOULDER = 5
RIGHT_SHOULDER = 6
LEFT_WRIST = 9
RIGHT_WRIST = 10

CONF_THRESHOLD = 0.4  # minimum keypoint confidence to trust a coordinate


def has_both_hands_raised(keypoints) -> bool:
    """
    Determine whether a single person has both hands raised.

    Args:
        keypoints: numpy array of shape (17, 3) — columns are (x, y, confidence).

    Returns:
        True if both wrists are above (lower y value than) their respective
        shoulders and all four keypoints are detected with enough confidence.
    """
    if len(keypoints) <= max(LEFT_WRIST, RIGHT_WRIST, LEFT_SHOULDER, RIGHT_SHOULDER):
        return False

    lw_x, lw_y, lw_c = keypoints[LEFT_WRIST]
    rw_x, rw_y, rw_c = keypoints[RIGHT_WRIST]
    ls_x, ls_y, ls_c = keypoints[LEFT_SHOULDER]
    rs_x, rs_y, rs_c = keypoints[RIGHT_SHOULDER]

    # Reject if any relevant keypoint is below the confidence threshold
    if min(lw_c, rw_c, ls_c, rs_c) < CONF_THRESHOLD:
        return False

    # Image y-axis points downward: a raised hand has a smaller y than the shoulder
    left_raised = lw_y < ls_y
    right_raised = rw_y < rs_y

    return left_raised and right_raised
