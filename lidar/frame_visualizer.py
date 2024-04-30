"""
UNH Capstone Project Teams

2024
Jay Bazenas, Theo DiMambro, Will Morong
"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

# Import the extract_frames_from_file function from pirail_json_parser.py
from pirail_json_parser import extract_frames_from_file

def lidar_to_3d_points(lidar_data, horizontal_fov=56, vertical_fov=32):
    num_rows, num_cols = lidar_data.shape
    horizontal_angles = np.linspace(-horizontal_fov / 2, horizontal_fov / 2, num_cols)
    vertical_angles = np.linspace(-vertical_fov / 2, vertical_fov / 2, num_rows)
    points = []

    for i in range(num_rows):
        for j in range(num_cols):
            depth = lidar_data[i, j]
            if depth <= 0:
                continue
            x = depth * np.sin(np.radians(horizontal_angles[j])) * np.cos(np.radians(vertical_angles[i]))
            y = depth * np.sin(np.radians(vertical_angles[i]))
            z = depth * np.cos(np.radians(horizontal_angles[j])) * np.cos(np.radians(vertical_angles[i]))
            points.append([x, y, z])

    return np.array(points)

def sanitize_lidar_data(lidar_data):
    invalid_readings = [0x0000, 0xFF14, 0xFF78, 0xFFDC, 0xFFFA]
    for invalid_reading in invalid_readings:
        lidar_data[lidar_data == invalid_reading] = -1
    return lidar_data

def rotate_points_around_x(points, degrees=225):
    theta = np.radians(degrees)
    print("Rotating matrix", degrees, "degrees around the x axis")
    rotation_matrix = np.array([ # rotation matrix
        [1, 0, 0],
        [0, np.cos(theta), -np.sin(theta)],
        [0, np.sin(theta), np.cos(theta)]
    ])
    return np.dot(points, rotation_matrix.T)

def visualize_frame(frame_data, mode='2D'):
    if mode == '2D':
        plt.imshow(frame_data, cmap='hot', interpolation='nearest')
        plt.colorbar()
        plt.title('2D Heatmap Visualization')
        plt.show()
    elif mode == '3D':
        wcs_data = lidar_to_3d_points(frame_data)
        rotated_wcs_data = rotate_points_around_x(wcs_data, degrees=225)
        regular_points = np.array([point for point in rotated_wcs_data if point[2] <= -600])
        highlighted_points = np.array([point for point in rotated_wcs_data if point[2] > -600])
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        if len(regular_points) > 0:
            x, y, z = zip(*regular_points)
            ax.scatter(x, y, z, s=2, c=z, cmap='viridis', label='Regular Points')
        
        if len(highlighted_points) > 0:
            x, y, z = zip(*highlighted_points)
            ax.scatter(x, y, z, s=15, c='red', label='Outside of Bounding Box')

        ax.set_title('3D Point Cloud Visualization (Ground Rotated)')
        ax.set_box_aspect([np.ptp(a) for a in [x, y, z]])
        
        ax.legend()

        plt.show()

def main():
    if len(sys.argv) != 2:
        print("Usage: python visualizer.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Use extract_frames_from_file to parse the input file
    frames, num_frames = extract_frames_from_file(file_path)
    print(f"Extracted {num_frames} frames.")

    while True:
        frame_index = input("Select a frame to view (or type 'exit' to quit): ")
        if frame_index.lower() == 'exit':
            print("Exiting...")
            break

        try:
            frame_index = int(frame_index)
            if frame_index < 0 or frame_index >= num_frames:
                print(f"Please enter a number between 0 and {num_frames - 1}.")
                continue
        except ValueError:
            print("Please enter a valid number or 'exit'.")
            continue

        mode = input("Select visualization mode ('2D' or '3D'): ").strip()
        if mode not in ['2D', '3D']:
            print("Invalid mode selected. Please enter '2D' or '3D'.")
            continue

        frame_data = frames[frame_index]
        sanitized_frame_data = sanitize_lidar_data(np.array(frame_data))
        visualize_frame(sanitized_frame_data, mode=mode)

if __name__ == "__main__":
    main()
