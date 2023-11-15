import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import multiprocessing as mp
import os
from tkinter.messagebox import showerror, showinfo
import tkinter as tk
from tkinter import ttk

directory = ""

def safe_parametres():
    global directory
    directory = input_Entry.get()
    showinfo(title="успешно", message="данные сохранены")

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

    font_path = "font/arialuni.ttf"
    font = ImageFont.truetype(font_path, 14)

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
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i, image in enumerate(filtered_images):
        filename = f"{name_file[i][:name_file[i].find('.')]}_new{name_file[i][name_file[i].find('.'):]}"
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        
def is_error(directory)->bool:
    if not os.path.exists(directory):
        showerror(title= "ошибка", message= "такой директории не существует")

def main():
    global directory
    if is_error(directory):
        return
    
    queue = mp.Queue()
    # Загрузка изображения
    image = cv2.imread(directory)
    num_parts = 4
    mp_parts = split_image(image, num_parts)
    
    Processes = []
    number = 0
    for mp_part in mp_parts:
        number += 1
        Process = mp.Process(target=detect_space_object, args=(mp_part, number, queue))
        Process.start()
        Processes.append(Process)
        
    sum_finish = 0
    
    image_parts = [0] * len(mp_parts)
    
    while sum_finish != len(Processes):
        if not queue.empty():
            sum_finish += 1
            image_part = queue.get()
            image_parts[image_part[1]] = image_part[0].copy()
    
    image_vstack = [image_parts[i] for i in range(0, num_parts ** 2, num_parts)]
    
    k = 0
    for i in range(num_parts):
        for j in range(1, num_parts):
            image_vstack[i] = np.vstack([image_vstack[i], image_parts[j + k]])
        k += num_parts
    
    image_with_objects = np.hstack(image_vstack)
    
    new_directory = directory[:directory.rfind("/")]
    cv2.imwrite(f"{new_directory}/new_image.tif", image_with_objects)
    showinfo(title="успешно", message="изображение обработано")

# Пример использования функции
if __name__ == "__main__":
    root = tk.Tk()
    root.title("поиск космических тел")
    root.geometry('400x100')
    root['background'] = "gray"
    root.resizable(False, False)
    
    my_font = ("Arial", 16) 
    style_frame = ttk.Style()
    style_frame.configure("CustomFrame.TFrame", background="white")
    style_Entry = ttk.Style()
    style_Entry.configure("TEntry", padding=5, font=my_font, foreground="black", background="gray")
    style_label = ttk.Style()
    style_label.configure("TLabel", font=my_font, padding=10, foreground="white", background="gray")
    
    main_menu = tk.Menu()
    main_menu.add_cascade(label="найти объекты", command=main)
    main_menu.add_cascade(label="сохранить параметры", command = safe_parametres)
    
    input_label = ttk.Label(root, style="TLabel", text="Введите название директории")
    input_label.pack()
    input_Entry = ttk.Entry(root, justify="center", width=30, style="TEntry")
    input_Entry.pack()
    
    root.config(menu=main_menu)
    root.mainloop()
