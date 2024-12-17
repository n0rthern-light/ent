#!/usr/bin/env python3

import argparse
import sys
import math
import struct
import os
import statistics

def calculate_entropy(data):
    if not data:
        return 0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = len(data)
    entropy = -sum((count / total) * math.log2(count / total) for count in counts if count > 0)
    return entropy

def entropy_to_color(entropy, max_entropy):
    normalized = entropy / max_entropy
    if normalized <= 0.5:
        red = int(255 * (normalized / 0.5))
        green = 255
        blue = 0
    else:
        red = 255
        green = int(255 * ((1 - normalized) / 0.5))
        blue = 0

    return (blue, green, red)

def write_bmp_image(width, height, entropy_values, output_file):
    max_entropy = math.log2(256)
    row_padding = (4 - (width * 3 % 4)) % 4

    normalized_heights = [int((e / max_entropy) * height) for e in entropy_values]

    bmp_header = b'BM'  # Signature
    pixel_data_offset = 54  # BMP header size
    file_size = pixel_data_offset + (width * 3 + row_padding) * height
    bmp_header += struct.pack('<I', file_size)  # File size
    bmp_header += struct.pack('<H', 0)  # Reserved
    bmp_header += struct.pack('<H', 0)  # Reserved
    bmp_header += struct.pack('<I', pixel_data_offset)  # Offset to pixel data

    dib_header = struct.pack('<I', 40)  # Header size
    dib_header += struct.pack('<i', width)  # Image width
    dib_header += struct.pack('<i', -height)  # Image height
    dib_header += struct.pack('<H', 1)  # Number of color planes
    dib_header += struct.pack('<H', 24)  # Bits per pixel (24-bit)
    dib_header += struct.pack('<I', 0)  # No compression
    dib_header += struct.pack('<I', file_size - pixel_data_offset)  # Image size
    dib_header += struct.pack('<I', 2835)  # Horizontal resolution (pixels/meter)
    dib_header += struct.pack('<I', 2835)  # Vertical resolution (pixels/meter)
    dib_header += struct.pack('<I', 0)  # Number of colors in palette
    dib_header += struct.pack('<I', 0)  # Important colors

    pixel_data = bytearray()
    for row in range(height):
        for col in range(width):
            bar_height = normalized_heights[col]
            if height - row <= bar_height:
                color = entropy_to_color(entropy_values[col], max_entropy)
            else:
                color = (0, 0, 0)
            pixel_data.extend(color)
        pixel_data.extend(b'\x00' * row_padding)

    with open(output_file, "wb") as f:
        f.write(bmp_header)
        f.write(dib_header)
        f.write(pixel_data)

def check_file_entropy(input_file, window_size=1024, image_height=32, show_spikes=True):
    with open(input_file, "rb") as f:
        data = f.read()

    num_windows = len(data) // window_size
    entropy_values = []
    for i in range(num_windows):
        window = data[i * window_size: (i + 1) * window_size]
        entropy = calculate_entropy(window)
        entropy_values.append(entropy)
        
    prev_ent = None
    if len(entropy_values) >= 2 and show_spikes == True:
        mean_entropy = statistics.mean(entropy_values)
        stddev_entropy = statistics.stdev(entropy_values)
        for i in range(num_windows):
            entropy = entropy_values[i]
            if prev_ent != None and entropy > mean_entropy + (2 * stddev_entropy):
                print(f"0x{(i*window_size):x} (size: 0x{window_size:x}): Entropy spike from {prev_ent:.2f} to {entropy:.2f}")
            prev_ent = entropy

    output_file = f"{os.path.basename(input_file)}.bmp"

    write_bmp_image(len(entropy_values), image_height, entropy_values, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process file and generate entropy chart.")
    parser.add_argument("input_file", type=str, help="Path to the input file")
    parser.add_argument("--size", type=int, default=1024, help="Size of the window for entropy calculation for single PX of width in bytes (default: 1024)")
    parser.add_argument("--height", type=int, default=32, help="Height of the output image (default: 32)")
    parser.add_argument("--spikes", action="store_true", help="Display entropy spikes in stdout (default: False)")

    args = parser.parse_args()

    check_file_entropy(args.input_file, window_size=args.size, image_height=args.height, show_spikes=args.spikes)

