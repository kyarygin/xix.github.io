from PIL import Image, ImageOps
import os

def process(image_path, output_size):
    with Image.open(image_path) as im:
        width, height = im.size
        if width == height == output_size:
            print(image_path, 'no resize needed')
            return
        print(image_path, (width, height), '->', (output_size, output_size))

        min_dim = min(width, height)

        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim

        cropped_im = im.crop((left, top, right, bottom))
        resized_im = cropped_im.resize((output_size, output_size), Image.LANCZOS)
        resized_im.save(image_path)

if __name__ == '__main__':
    image_path_list = [
        os.path.join('images', x)
        for x in os.listdir('images')
        if x.endswith('.png')
    ]
    for image_path in image_path_list:
        process(image_path, 200)
