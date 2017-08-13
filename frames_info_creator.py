import os, glob, struct
from PIL import Image
from natsort import natsort

from info_file_constans import *


def create_frames_info(BMP_files_directory_path, info_file_path):
    frames_info = {}

    BMP_file_paths = get_BMP_file_paths(BMP_files_directory_path)
    frames_info['palette_bytes'] = get_palette_bytes(BMP_file_paths)
    frames_info['number_of_frames'] = len(BMP_file_paths)
    frames_info['number_of_cycles'] = int(input('how many cycles are there supposed to be?'))
    frames_info['frames_in_cycles'] = [int(input('how many frames are in {0} cycle?'.format(i))) for i in
                                       range(0, frames_info['number_of_cycles'])]
    frames_info['frames_data'] = [create_frame_data(BMP_file_path, i, info_file_path) for i, BMP_file_path in
                                  enumerate(BMP_file_paths)]
    print(frames_info)
    return frames_info


def get_BMP_file_paths(BMP_files_directory_path):
    BMP_file_path_pattern = os.path.join(BMP_files_directory_path, '*.bmp')
    BMP_file_paths = natsort.natsorted(glob.glob(BMP_file_path_pattern))
    return BMP_file_paths


def get_palette_bytes(BMP_files_paths):
    image = Image.open(BMP_files_paths[0])
    palette_bytes = image.palette.getdata()[1]
    return palette_bytes


def create_frame_data(BMP_file_path, i, info_file_path):
    frame_data = {}

    BMP_image = Image.open(BMP_file_path)
    frame_data['BMP_file_path'] = BMP_file_path
    frame_data['width'], frame_data['height'] = BMP_image.size
    frame_data['x_center'], frame_data['y_center'] = get_frame_xy_centers(i, info_file_path)
    return frame_data


def get_frame_xy_centers(i, info_file_path):
    with open(info_file_path, 'r+b') as info_file:
        info_file.read(header_length +
                       i * frame_data_length +
                       current_frame_centers_offset)
        x_center = struct.unpack('i', info_file.read(4))[0]
        y_center = struct.unpack('i', info_file.read(4))[0]
        return x_center, y_center


def get_frame_sizes(frames_info):
    frames_sizes = [frame_data['width'] * frame_data['height'] for frame_data in frames_info['frames_data']]
    return frames_sizes
