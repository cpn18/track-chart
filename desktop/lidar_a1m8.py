
def estimate_from_lidar(distance_in_mm):
    """
    Estimates the actual distance based on LIDAR measurement
    https://mycurvefit.com/
    """
    x = distance_in_mm / 10
    y = 101418000 + (4.013375 - 101418000)/(1 + (x/13384660) ** 1.174833)
    return y*10
