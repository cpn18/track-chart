"""
UNH Capstone Project Teams

2024
Jay Bazenas, Theo DiMambro, Will Morong
"""
import ast
import sys
import concurrent.futures
import matplotlib.pyplot as plt

def delete_last_line():
    #cursor up one line
    sys.stdout.write('\x1b[1A')

    #delete last line
    sys.stdout.write('\x1b[2K')

""" def extract_frames_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    frames_str = []
    start_marker = '"depth": [['
    end_marker = ']]'
    start_idx = content.find(start_marker)
    j = 0

    print("Extracted ", j, " frames")

    while start_idx != -1:
        end_idx = content.find(end_marker, start_idx) + len(end_marker)
        frame_str = content[start_idx + len(start_marker) - 2:end_idx]
        frames_str.append(frame_str)
        start_idx = content.find(start_marker, end_idx)
    
    frames = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_frame = {executor.submit(ast.literal_eval, frame_str): frame_str for frame_str in frames_str}
        for future in concurrent.futures.as_completed(future_to_frame):
            try:
                frame_data = future.result()
                frames.append(frame_data)
                delete_last_line()
                j = j + 1
                print("Extracted ", j, " frames")
            except Exception as e:
                print(f"Error parsing frame: {e}")

    return frames, j
 """
def extract_frames_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    frames = []
    start_marker = '"depth": [['
    end_marker = ']]'
    start_idx = content.find(start_marker)
    j = 0
    print("Extracted ", j, " frames")
    
    while start_idx != -1:
        end_idx = content.find(end_marker, start_idx) + len(end_marker)
        frame_str = content[start_idx + len(start_marker) - 2:end_idx]  # Include brackets
        try:
            frame_data = ast.literal_eval(frame_str)
            frames.append(frame_data)
            j = j + 1
            delete_last_line()
            print("Extracted ", j, " frames")
        except ValueError as e:
            print(f"Error parsing frame: {e}")
        start_idx = content.find(start_marker, end_idx)
    
    return frames, j

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")
    frames, j = extract_frames_from_file(sys.argv[1])
    print("COMPLETED: Extracted ", j, " frames")
    
    if len(sys.argv) >= 3 and sys.argv[2] == "show":
        for frame in frames:
            print("In show loop")
            plt.imshow(frame, interpolation="nearest", origin="upper")
            plt.colorbar()
            plt.show()
