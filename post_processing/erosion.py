import cv2 as cv
import numpy as np


def morph_open(img, kernel_size):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    open_m = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
    return open_m


if __name__ == '__main__':
    import os
    import json
    import rasterio

    env = json.load(open('C:/Users/xianyu/GraduationProject/env.json'))
    base_dir = env['base_dir']
    output_dir = env['output_dir']

    Epath = os.walk(f'{base_dir}/3_predict_result')
    for path, dir, filelist in Epath:
        for filename in filelist:
            if filename.endswith('.tif') and not filename.startswith('.'):
                _path = str(os.path.join(path, filename))
                _file = rasterio.open(_path).read(1)
                result = morph_open(_file, 3)
                cv.imwrite(f'{output_dir}/morph/morph_{filename}', result)
                print('morph_' + filename)
