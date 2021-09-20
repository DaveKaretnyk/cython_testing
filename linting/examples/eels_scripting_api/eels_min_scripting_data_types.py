# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from enum import Enum


class ScanSettings:
    """
    scan acquisition settings
    """

    def __init__(self):
        """ Initialize an instance of the ScanSettings class.
        """
        self.area = (0, 0, 1, 1)
        self.resolution = 1024
        self.dwell_time = 1e-6
        self.mains_lock_active = False
        self.line_scan_orientation_vertical = False
        self.serpentine_scan = False
        self.selected_stem_detectors = []


class EelsDetectorSettings:
    """

    """

    def __init__(self):
        """ Initialize an instance of the EelsDetectorSettings class.
        """
        self.exposure_time = 0.1
        self.corrected = True
        self.use_image_area = False


class EelsDetectorStorageSettings:
    """

    """

    def __init__(self):
        """ Initialize an instance of the EelsDetectorStorageSettings class.
        """
        self.experiment_id = "Name_of_experiment"
        self.delete_existing = True
        self.save_data = True
        self.data_location = r"c:\temp\EelsMinScriptingData"


class EnergyOffset:
    def __init__(self, energy_offset: float, exposure_time: float, nr_frames: int):
        super().__init__()
        self.energy_offset = energy_offset
        self.exposure_time = exposure_time
        self.nr_frames = nr_frames


class DriftTubeMode(str, Enum):
    FullRangeFast = "Fast Full Range"
    FullRangeMedium = "Medium Full Range"
    FullRangeSlow = "Slow Full Range"
    Grounded = "Grounded"
    LowNoiseFast = "Fast Low Noise"
    LowNoiseMedium = "Medium Low Noise"
    LowNoiseSlow = "Slow Low Noise"
    BeamCurrentMeasurement = "BCM"

    @staticmethod
    def get_conversion_dict():
        return {DriftTubeMode.FullRangeFast: 0,
                DriftTubeMode.FullRangeMedium: 1,
                DriftTubeMode.FullRangeSlow: 2,
                DriftTubeMode.Grounded: 3,
                DriftTubeMode.LowNoiseFast: 4,
                DriftTubeMode.LowNoiseMedium: 5,
                DriftTubeMode.LowNoiseSlow: 6,
                DriftTubeMode.BeamCurrentMeasurement: 7}

    @staticmethod
    def from_index_to_drift_tube_mode(index):
        for key, value in DriftTubeMode.get_conversion_dict().items():
            if value == index:
                return key
        raise ValueError("Drift tube mode with index: {} not found".format(index))

    @staticmethod
    def from_drift_tube_mode_to_index(mode):
        if mode in DriftTubeMode.get_conversion_dict():
            return DriftTubeMode.get_conversion_dict()[mode]
        raise ValueError("Drift tube mode: {} not found".format(mode))


class EnergyFilterSettings:
    """

    """

    def __init__(self):
        """ Initialize an instance of the EelsDetectorSettings class.
        """
        self.drift_tube_mode = DriftTubeMode.FullRangeFast
        self.energy_offsets = []
        self.use_dtd = True


class SpectrumImageSettings:
    """

    """
    def __init__(self,
                 scan_settings: ScanSettings,
                 eels_detector_settings: EelsDetectorSettings,
                 eels_detector_storage_settings: EelsDetectorStorageSettings,
                 energy_filter_settings: EnergyFilterSettings):
        """ Initialize an instance of the EelsDetectorSettings class.
        """
        self.scan_settings = scan_settings
        self.eels_detector_settings = eels_detector_settings
        self.eels_detector_storage_settings = eels_detector_storage_settings
        self.energy_filter_settings = energy_filter_settings


class EelsSettings:
    """

    """
    def __init__(self,
                 eels_detector_settings: EelsDetectorSettings,
                 eels_detector_storage_settings: EelsDetectorStorageSettings,
                 energy_filter_settings: EnergyFilterSettings,
                 nr_points=0):
        """ Initialize an instance of the EelsSettings class.
        """
        self.eels_detector_settings = eels_detector_settings
        self.eels_detector_storage_settings = eels_detector_storage_settings
        self.energy_filter_settings = energy_filter_settings
        self.nr_points = nr_points


class ActionSettings:
    """

    """
    def __init__(self, action_values, action_callback_function, action_description):
        """ Initialize an instance of the EelsSettings class.
        """
        self.action_values = action_values
        self.action_callback_function = action_callback_function
        self.action_description = action_description


class SwSynchronizedEelsSettings:
    """

    """
    def __init__(self,
                 eels_detector_settings: EelsDetectorSettings,
                 eels_detector_storage_settings: EelsDetectorStorageSettings,
                 energy_filter_settings: EnergyFilterSettings,
                 action_settings: ActionSettings):
        """ Initialize an instance of the SwSynchronizedEelsSettings class.
        """
        self.eels_detector_settings = eels_detector_settings
        self.eels_detector_storage_settings = eels_detector_storage_settings
        self.energy_filter_settings = energy_filter_settings
        self.action_settings = action_settings


class AcquireSingleSpectraSettings:
    """

    """

    def __init__(self,
                 eels_detector_settings: EelsDetectorSettings,
                 energy_filter_settings: EnergyFilterSettings):
        """ Initialize an instance of the EelsDetectorSettings class.
        """
        self.eels_detector_settings = eels_detector_settings
        self.energy_filter_settings = energy_filter_settings
