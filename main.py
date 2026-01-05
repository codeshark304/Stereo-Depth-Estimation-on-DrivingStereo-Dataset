import cv2
import numpy as np
import os

def load_drivingstereo_calib(calib_path):
    with open(calib_path, "r") as f:
        lines = f.readlines()

    data = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":")
            data[key.strip()] = np.array(
                [float(x) for x in value.strip().split()]
            )

    P0 = data["P_rect_101"].reshape(3, 4)
    P1 = data["P_rect_103"].reshape(3, 4)

    fx = P0[0, 0]
    baseline = abs(P1[0, 3]) / fx

    return fx, baseline


def disparity_to_depth(disparity, fx, baseline):
    depth = np.zeros_like(disparity, dtype=np.float32)
    valid = disparity > 0
    depth[valid] = (fx * baseline) / disparity[valid]
    return depth


def compute_disparity(left, right):
    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=192,
        blockSize=5,
        P1=8 * 3 * 5 * 5,
        P2=32 * 3 * 5 * 5,
        disp12MaxDiff=1,
        uniquenessRatio=10,
        speckleWindowSize=100,
        speckleRange=32
    )

    disp = stereo.compute(left, right).astype(np.float32) / 16.0
    return disp

def depth_metrics(pred, gt):
    mask = (gt > 0) & (pred > 0)

    pred = pred[mask]
    gt = gt[mask]

    rmse = np.sqrt(np.mean((pred - gt) ** 2))
    mae = np.mean(np.abs(pred - gt))
    abs_rel = np.mean(np.abs(pred - gt) / gt)

    return rmse, mae, abs_rel



root = r"C:\Users\Monish Kiran\Desktop\task\final_dataset"

left_img = cv2.imread(os.path.join(root, "left", os.listdir(root + "/left")[0]), cv2.IMREAD_GRAYSCALE)
right_img = cv2.imread(os.path.join(root, "right", os.listdir(root + "/right")[0]), cv2.IMREAD_GRAYSCALE)

gt_depth = cv2.imread(
    os.path.join(root, "depth_map", os.listdir(root + "/depth_map")[0]),
    cv2.IMREAD_UNCHANGED
).astype(np.float32)

# IMPORTANT: DrivingStereo depth scale
gt_depth /= 256.0

fx, baseline = load_drivingstereo_calib(
    os.path.join(root, "calib", "2018-08-01-11-13-14.txt")
)

disparity = compute_disparity(left_img, right_img)
pred_depth = disparity_to_depth(disparity, fx, baseline)

rmse, mae, abs_rel = depth_metrics(pred_depth, gt_depth)

print(f"RMSE     : {rmse:.3f} m")
print(f"MAE      : {mae:.3f} m")
print(f"Abs Rel  : {abs_rel:.3f}")
