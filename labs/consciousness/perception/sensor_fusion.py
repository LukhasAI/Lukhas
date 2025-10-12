import numpy as np


def fuse_lidar_and_camera(lidar_points: np.ndarray, camera_features: np.ndarray) -> np.ndarray:
    """Fuse LiDAR point cloud coordinates with camera-derived features.

    Both arrays must have the same number of points. The result is an
    ``(N, lidar_dim + feature_dim)`` array combining positional and
    visual information.
    """
    if lidar_points.shape[0] != camera_features.shape[0]:
        raise ValueError("Input arrays must have the same length")
    return np.concatenate([lidar_points, camera_features], axis=1)
