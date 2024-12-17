#!/usr/bin/env python3

import sys
import math
import struct
import os

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

def generate_entropy_bmp(input_file, window_size=1024, image_height=32):
    with open(input_file, "rb") as f:
        data = f.read()

    num_windows = len(data) // window_size
    entropy_values = []
    for i in range(num_windows):
        window = data[i * window_size: (i + 1) * window_size]
        entropy = calculate_entropy(window)
        entropy_values.append(entropy)

    output_file = f"{os.path.basename(input_file)}.bmp"

    write_bmp_image(len(entropy_values), image_height, entropy_values, output_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ent.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    generate_entropy_bmp(input_file)

