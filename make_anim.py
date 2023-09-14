import os
import imageio.v3 as iio
import cv2

def create_gif(input_folder, output_path, delay, max_frames):
    # Get all .png files from the input folder
    png_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]
    
    # Sort the files by their filename
    png_files.sort()
    
    # Create a list to store the images
    images = []

    # Read each file and append it to the images list
    frame_count = 0
    for png_file in png_files:
        file_path = os.path.join(input_folder, png_file)

        print("Reading file:",file_path,"        ", end="\r", flush=True)
        images.append(iio.imread(file_path))

        frame_count += 1
        if frame_count >= max_frames:
            break
    
    print("Creating ",output_path,"        ", end="\r", flush=True)
    # Create a gif/webp from the images with the specified delay
    iio.imwrite(output_path, images, fps=30)

    print("Operation completed.        ")



def create_video(input_folder, output_path, delay, max_frames):
    # Get all .png files from the input folder
    png_files = [f for f in os.listdir(input_folder) if f.endswith('.png')]
    
    # Sort the files by their filename
    png_files.sort()
    
    frame_count = 0
    # Calculate FPS from the delay
    fps = int(1 / delay)

    # Read the first file to get the dimensions
    first_image = cv2.imread(os.path.join(input_folder, png_files[0]))
    h, w, layers = first_image.shape
    size = (w, h)

    # Initialize VideoWriter (using *'XVID' as the codec)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    for png_file in png_files:
        file_path = os.path.join(input_folder, png_file)

        print("Reading file:", file_path, "        ", end="\r", flush=True)
        
        img = cv2.imread(file_path)
        out.write(img)

        frame_count += 1
        if frame_count >= max_frames:
            break
    
    out.release()
    print("Operation completed.        ")


# main method, read input_folder, output_path and delay from command line arguments
if __name__ == '__main__':
    import sys
    if not (len(sys.argv) in [4, 5]):
        print('Usage: python make_gif.py <input_folder> <output_path> <delay> (<max_frames>)')
        sys.exit(1)

    # read arguments:
    import argparse
    parser = argparse.ArgumentParser(description='Create a gif from a folder of png files.')
    parser.add_argument('input_folder', type=str, help='The folder containing the png files.')
    parser.add_argument('output_path', type=str, help='The path to the output gif file.')
    parser.add_argument('delay', type=float, help='The delay between frames in the gif (in seconds).')
    parser.add_argument('max_frames', type=int, help='The maximum number of frames to include in the gif.')
    args = parser.parse_args()

    create_video(args.input_folder, args.output_path, args.delay, args.max_frames)
