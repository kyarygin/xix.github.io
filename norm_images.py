from PIL import Image, ImageOps
import os

def process(input_path, output_path, output_size):
    with Image.open(input_path) as im:
        width, height = im.size
        print(input_path, output_path, width, height)
        min_dim = min(width, height)

        # Calculate the cropping box to center the square
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim

        # Crop the image to the square
        cropped_im = im.crop((left, top, right, bottom))

        # Resize the cropped square to the desired output_size
        resized_im = cropped_im.resize((output_size, output_size), Image.LANCZOS)

        resized_im.save(output_path)


if __name__ == '__main__':
    image_path_list = [
        os.path.join('images_raw', x)
        for x in os.listdir('images_raw')
        if x.endswith('.png')
    ]
    for input_path in image_path_list:
        output_path = input_path.replace('_raw', '')
        print(input_path, '->', output_path)
        process(input_path, output_path, 200)
