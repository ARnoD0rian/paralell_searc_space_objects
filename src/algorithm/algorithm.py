import cv2
import multiprocessing as mp
from algorithm.uilts import *



def algorithm(directory) -> str:
    if is_error(directory):
        return "ERROR"
    
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
    
    cv2.imwrite(f"new_image.tif", image_with_objects)
    
    return "OK"
