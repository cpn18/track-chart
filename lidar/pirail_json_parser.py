import ast
import sys
import matplotlib.pyplot as plt

def extract_frames_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    frames = []
    start_marker = '"depth": [['
    end_marker = ']]'
    start_idx = content.find(start_marker)
    
    while start_idx != -1:
        end_idx = content.find(end_marker, start_idx) + len(end_marker)
        frame_str = content[start_idx + len(start_marker) - 2:end_idx]  # Include brackets
        try:
            frame_data = ast.literal_eval(frame_str)
            frames.append(frame_data)
        except ValueError as e:
            print(f"Error parsing frame: {e}")
        start_idx = content.find(start_marker, end_idx)
    
    return frames

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    frames = extract_frames_from_file(sys.argv[1])
    print("Extracted frames")
    
    if len(sys.argv) >= 3 and sys.argv[2] == "show":
        for frame in frames:
            print("In show loop")
            plt.imshow(frame, interpolation="nearest", origin="upper")
            plt.colorbar()
            plt.show()
