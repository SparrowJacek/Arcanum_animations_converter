import struct
from PIL import Image

from BAM_file_constants import *
from frames_info_creator import create_frames_info, get_frame_sizes, create_Disc_frames_info

"""
Arcanum animation creator v 0.2

This program creates fully functional BAM files(Baldur's gate animation files) from a set of BMP files containing 
animation frames from Arcanum game(using for example Art View) and a .info file which contains frame x and y centers. 
Both programs can be downloaded from http://www.terra-arcanum.com/downloads/
"""


def create_bam_file(new_bam_name, BMP_files_directory_path, info_file_path):
    frames_info = create_frames_info(BMP_files_directory_path, info_file_path)

    create_empty_bam_file(new_bam_name)
    with open(new_bam_name, 'r+b') as bam_file:
        create_bam_heading(bam_file, frames_info)
        create_frame_entries(bam_file, frames_info)
        create_cycle_entries(bam_file, frames_info)
        create_palette(bam_file, frames_info)
        create_frames(bam_file, frames_info)
        create_frame_lookup_table(bam_file, frames_info)


def create_empty_bam_file(new_bam_name):
    open(new_bam_name, 'w').close()


def create_bam_heading(bam_file, frames_info):
    write_bam_signature(bam_file)
    write_bam_version(bam_file)
    write_frames_number(bam_file, frames_info)
    write_cycles_number(bam_file, frames_info)
    write_compressed_colour_index(bam_file)
    write_frame_entries_offset(bam_file)
    write_palette_offset(bam_file, frames_info)
    write_frame_lookup_table_offset(bam_file, frames_info)


def write_bam_signature(bam_file):
    bam_file.write(struct.pack('<B', 66))
    bam_file.write(struct.pack('<B', 65))
    bam_file.write(struct.pack('<B', 77))
    bam_file.write(struct.pack('<B', 32))


def write_bam_version(bam_file):
    bam_file.write(struct.pack('<B', 86))
    bam_file.write(struct.pack('<B', 49))
    bam_file.write(struct.pack('<B', 32))
    bam_file.write(struct.pack('<B', 32))


def write_frames_number(bam_file, frames_info):
    bam_file.write(struct.pack('<H', len(frames_info['frames_data'])))


def write_cycles_number(bam_file, frames_info):
    bam_file.write(struct.pack('<B', frames_info['number_of_cycles']))


def write_compressed_colour_index(bam_file):
    bam_file.write(struct.pack('<B', 0))


def write_frame_entries_offset(bam_file):
    bam_file.write(struct.pack('<I', bam_heading_length))


def write_palette_offset(bam_file, frames_info):
    bam_file.write(struct.pack('<I', bam_heading_length + sum(get_frame_and_cycle_entries_length(frames_info))))


def get_frame_and_cycle_entries_length(frames_info):
    number_of_frames, number_of_cycles = frames_info['number_of_frames'], frames_info['number_of_cycles']
    frame_entries_length = frame_entry_length * number_of_frames
    cycle_entries_length = cycle_entry_length * number_of_cycles
    return frame_entries_length, cycle_entries_length


def write_frame_lookup_table_offset(bam_file, frames_info):
    offset = calculate_frame_lookup_table_offset(frames_info)
    bam_file.write(struct.pack('<I', offset))


def calculate_frame_lookup_table_offset(frames_info):
    offset = bam_heading_length + \
             sum(get_frame_and_cycle_entries_length(frames_info)) + \
             palette_length + \
             sum(get_frame_sizes(frames_info))
    return offset


def create_frame_entries(bam_file, frames_info):
    first_frame_offset = bam_heading_length + sum(get_frame_and_cycle_entries_length(frames_info)) + palette_length
    for i, frame_data in enumerate(frames_info['frames_data']):
        bam_file.write(struct.pack('<H', frame_data['width']))
        bam_file.write(struct.pack('<H', frame_data['height']))
        bam_file.write(struct.pack('<h', frame_data['x_center']))
        bam_file.write(struct.pack('<h', frame_data['y_center']))
        frame_offset = first_frame_offset + sum(get_frame_sizes(frames_info)[:i])
        bam_file.write(struct.pack('<I', uncompressed_frame_value + frame_offset))


def create_cycle_entries(bam_file, frames_info):
    starting_frame = 0
    for frames_in_cycle in frames_info['frames_in_cycles']:
        bam_file.write(struct.pack('<H', frames_in_cycle))
        bam_file.write(struct.pack('<H', starting_frame))
        starting_frame += frames_in_cycle


def create_palette(bam_file, frames_info):
    set_transparent_color_to([0, 255, 0, 0], bam_file)
    bam_file.write(frames_info['palette_bytes'][4:])


def set_transparent_color_to(BGR0, bam_file):
    for color in BGR0:
        bam_file.write(struct.pack('<B', color))


def create_frames(bam_file, frames_info):
    for i, frame_data in enumerate(frames_info['frames_data']):
        frame = Image.open(frame_data['BMP_file_path'])
        bam_file.write(bytes(frame.getdata()))


def create_frame_lookup_table(bam_file, frames_info):
    for i in range(0, len(frames_info['frames_data'])):
        bam_file.write(struct.pack('<H', i))
