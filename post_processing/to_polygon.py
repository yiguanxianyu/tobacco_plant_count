import cv2 as cv
import numpy as np


if __name__ == '__main__':
    import os
    import json
    from osgeo import gdal

    env = json.load(open('C:/Users/xianyu/GraduationProject/env.json'))
    base_dir = env['base_dir']
    output_dir = env['output_dir']

    Epath = os.walk(f'{base_dir}/3_predict_result')

    for path, dir, filelist in Epath:
        for filename in filelist:
            if filename.endswith('.tif') and not filename.startswith('.'):
                source_path = str(os.path.join(path, filename))
                target_path = f'{output_dir}/morph/morph_{filename}'

                source_file = gdal.Open(source_path)
                target_file = source_file.GetDriver().CreateCopy(target_path, source_file)

                band = target_file.GetRasterBand(1)

                result = morph_open(band.ReadAsArray(), 3)
                band.WriteArray(result)
                band.FlushCache()
                band.SetNoDataValue(0)
                print('morph_' + filename)
