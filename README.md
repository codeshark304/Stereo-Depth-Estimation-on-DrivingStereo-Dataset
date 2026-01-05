# Stereo Depth Estimation on DrivingStereo Dataset

## Overview

This project implements **classical stereo depth estimation** using the **DrivingStereo dataset**.  
Depth is computed from left–right stereo image pairs using **OpenCV’s StereoSGBM** algorithm and the standard **stereo geometry formula**. The estimated depth is then evaluated against the **ground-truth depth maps** provided by the dataset.

The goal of this work is **not** to train a neural network, but to:

- Validate stereo geometry  
- Understand the role of camera calibration  
- Quantify the limitations of classical stereo methods in real-world driving scenes  

---

## Dataset

**Dataset:** DrivingStereo  
**Source:** https://drivingstereo-dataset.github.io/

The dataset provides:

- Rectified left and right stereo images  
- Ground-truth disparity maps  
- Ground-truth depth maps  
- Precise camera calibration parameters  

---

## Directory Structure

dataset/
│
├── left/ # Left camera images (grayscale)
├── right/ # Right camera images (grayscale)
├── disparity_map/ # Ground-truth disparity maps (16-bit PNG)
├── depth_map/ # Ground-truth depth maps (16-bit PNG)
├── calib/ # Camera calibration files
└── main.py # Depth estimation and evaluation script


---

## Methodology

### 1. Stereo Disparity Estimation

Disparity is computed from the left and right images using **OpenCV StereoSGBM**:

- Block-matching–based classical stereo algorithm  
- Outputs disparity in pixel units  
- Scaled by `1/16` as per OpenCV convention  

This step is the **main source of error** in classical stereo pipelines, especially for:

- Long-range objects  
- Low-texture road regions  
- Sky and reflective surfaces  

---

### 2. Depth Computation from Disparity

Depth is computed using the standard stereo formula:

\[
\text{Depth} = \frac{f \cdot B}{d}
\]

Where:

- `f` = focal length (in pixels)  
- `B` = baseline between stereo cameras (in meters)  
- `d` = disparity (in pixels)  

This formula comes directly from stereo triangulation geometry.

---

### 3. Camera Calibration Usage

The calibration file provides projection matrices for both cameras.

From the rectified projection matrices:

- Focal length (`fx`) is extracted from `P_rect_101`  
- Baseline (`B`) is computed from the translation term in `P_rect_103`  

This calibration step is critical because it converts **pixel disparity into metric depth (meters)**.

---

### 4. Ground-Truth Depth Scaling

DrivingStereo ground-truth depth maps are stored as **16-bit images**.

They are converted to meters using:

```python
gt_depth = gt_depth / 256.0
