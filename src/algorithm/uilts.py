import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import multiprocessing as mp
import os


def get_class_object(area, brigtness):
    return {
        area < 10 and brigtness > 100: "звезда",
        area < 10 and brigtness > 50: "комета",
        area < 10 and brigtness > 0: "планета",
        area > 10000 and brigtness > 1000000: "галактика",
        area < 10000 and brigtness > 1000000: "квазар",
        area >= 10 and brigtness > 0: "звезда"
    }[True]

def detect_space_object(image, number, queue: mp.Queue)->None:

    if image is None:
        print("Не удалось загрузить изображение")
        
    image_with_objects = image.copy()
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    image = cv2.filter2D(image, -1, kernel)


    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    _, binary_image = cv2.threshold(blurred_image, 200, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    space_objects = []
    
    font = ImageFont.load_default()

    for contour in contours:
        # Вычисление площади контура
        area = cv2.contourArea(contour)

        # Вычисление ограничивающего прямоугольника для контура
        x, y, width, height = cv2.boundingRect(contour)

        # Вычисление координат центра контура
        center_x = x + width / 2
        center_y = y + height / 2

        # Вычисление суммарного яркого состояния пикселей в контуре
        brightness = np.sum(gray_image[y:y + height, x:x + width])

        object_type = get_class_object(area, brightness)

        space_object = {
            "x": center_x,
            "y": center_y,
            "brightness": brightness,
            "type": object_type, 
            "size": width * height
        }

        space_objects.append(space_object)

        cv2.rectangle(image_with_objects, (x, y), (x + width, y + height), (0, 255, 0), 2)

        (text_width, text_height) = cv2.getTextSize(object_type, cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, thickness=1)[0]
        cv2.rectangle(image_with_objects, (x, y - text_height - 5), (x + text_width // 2, y - 5), (0, 255, 0), cv2.FILLED)

        pil_image = Image.fromarray(image_with_objects)
        draw = ImageDraw.Draw(pil_image)

        draw.text((x, y - text_height - 10), object_type, font=font, fill=(0, 0, 0))

        image_with_objects = np.array(pil_image)

    cv2.imwrite(f"image_crop/{number}.tif", image_with_objects)

    if not is_error(f"image_result"):
        os.makedirs("image_result")
    with open(f"image_result/{number}.txt", "w", encoding="utf-8") as file:
        for object in space_objects:
            file.write(f"Координаты: ({object['x']}, {object['y']}); Светимость: {object['brightness']}; Размер: {object['size']}; Тип: {object['type']}\n")
    print(f"Process-{number} is finished")
    queue.put((image_with_objects, number - 1))
    return

# Функция для разделения изображений на равные части
def split_image(image: np.ndarray, num_parts):
    height, width, _ = image.shape
    part_width = (width // num_parts) + 1
    part_height = (height // num_parts) + 1
    parts = []
    for chunk_width in range(num_parts):
        for chunk_height in range(num_parts):
            part = image[chunk_height * part_height:min((chunk_height + 1) * part_height, len(image))]
            part = part[:, chunk_width * part_width:(chunk_width + 1) * part_width, :]
            parts.append(part)
    return parts

# Функция для сохранения обработанных изображений в новую директорию
def save_images(filtered_images, directory):
    name_file = os.listdir(directory)
    if not is_error(directory):
        os.makedirs(directory)
    for i, image in enumerate(filtered_images):
        filename = f"{name_file[i][:name_file[i].find('.')]}_new{name_file[i][name_file[i].find('.'):]}"
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        
def is_error(directory)->bool:
    if not os.path.isdir(directory):
        return False
    else:
        return True