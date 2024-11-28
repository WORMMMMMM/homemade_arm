'''
Camera API.

Author: Hongjie Fang.
'''

import re
from easyrobot.camera.base import RGBCameraBase, RGBDCameraBase
from easyrobot.camera.realsense import RealSenseRGBDCamera
from easyrobot.camera.orbbec import OrbbecRGBDCamera


def get_rgb_camera(**params):
    '''
    Get the camera object from the camera library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    return RGBCameraBase(**params)


def get_rgbd_camera(**params):
    '''
    Get the camera object from the camera library.
    '''
    name = params.get('name', None)
    if name is not None:
        del params['name']
    try:
        if re.fullmatch('[ -_]*realsense[ -_]*', str.lower(name)):
            return RealSenseRGBDCamera(**params)
        elif re.fullmatch('[ -_]*orbbec[ -_]*', str.lower(name)):
            return OrbbecRGBDCamera(**params)
        else:
            return RGBDCameraBase(**params)
    except Exception:
        return RGBDCameraBase(**params)
