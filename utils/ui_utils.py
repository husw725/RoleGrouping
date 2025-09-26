import os
from PIL import Image

def display_images(images, input_dir, container, images_per_row=4):
    for i in range(0, len(images), images_per_row):
        cols = container.columns(images_per_row)
        for col, img_name in zip(cols, images[i:i + images_per_row]):
            img_path = os.path.join(input_dir, img_name)
            try:
                img = Image.open(img_path)
                col.image(img, caption=img_name, use_container_width=True)
            except:
                col.write(f"无法加载 {img_name}")