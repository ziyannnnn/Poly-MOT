"""
object's trajectory. A trajectory is a collection of information for each frame(nusc_object.py)
Two core functions: state predict and state update.
The 'state' here is generalized, including attribute info, motion info, geometric info, score info, etc.
"""

import numpy as np
from nusc_life_manage import LifeManagement
from motion_module.nusc_object import FrameObject
from motion_module import LinearKalmanFilter, ExtendKalmanFilter


class Trajectory:
    def __init__(self, timestamp: int, config: dict, track_id: int, det_infos: dict):
        # init basic infos
        self.cfg, self.tracking_id, self.class_label = config, track_id, det_infos['NuscBox'][-1]
        # manage tracklet's attribute
        self.life_management = LifeManagement(timestamp, config, self.class_label)
        # manage for tracklet's motion/geometric/score infos
        KF_type = self.cfg['motion_model']['filter']
        assert KF_type in ['LinearKalmanFilter', 'ExtendKalmanFilter'], "must use specific kalman filter"
        self.tracklet = globals()[KF_type](timestamp, config, track_id, det_infos)
    
    def state_predict(self, timestamp: int) -> None:
        """
        predict trajectory's state
        :param timestamp: current frame id
        """
        self.life_management.predict(timestamp)
        self.tracklet.predict(timestamp)
    
    def state_update(self, timestamp: int, det: dict = None) -> None:
        """
        update trajectory's state
        :param timestamp: current frame id
        :param det: dict, detection infos under different data format
            {
                'NuscBox': NuscBox,
                'np_array': np.array,
                'has_velo': bool, whether the detetor has velocity info
            }
        """
        self.life_management.update(timestamp, det)
        self.tracklet.update(timestamp, det)
        
    def __getitem__(self, item) -> FrameObject:
        return self.tracklet[item]
    
    def __len__(self) -> int:
        return len(self.tracklet)