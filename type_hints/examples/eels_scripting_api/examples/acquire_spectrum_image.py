# Copyright (c) 2012-2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from tfs_eels.scripting_api.eels_min_scripting import EelsMinScripting
from tfs_eels.scripting_api.eels_min_scripting_data_types import (
    ScanSettings, EelsDetectorSettings, EelsDetectorStorageSettings,
    EnergyOffset, DriftTubeMode, EnergyFilterSettings,
    SpectrumImageSettings)
import logging

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    def live_data_callback(live_data_list):
        print("Received {} spectra".format(len(live_data_list)))
        for (energies, counts_at_energies) in live_data_list:
            # plot the data, or do something else, preferably decoupled so this callback returns quickly
            pass

    eels_min_script = None
    try:
        eels_min_script = EelsMinScripting(log_to_console=False, log_to_file=True,
                                           log_file_name=r'c:\temp\eels_min_scripting_test')
        logger.info("EELS SI Script started")
        eels_min_script.set_live_data_callback(live_data_callback=live_data_callback)

        offset_1 = EnergyOffset(energy_offset=0.0, exposure_time=1e-6, nr_frames=1)
        offset_2 = EnergyOffset(energy_offset=50.0, exposure_time=10e-6, nr_frames=1)
        offset_3 = EnergyOffset(energy_offset=400.0, exposure_time=100e-6, nr_frames=1)
        offset_4 = EnergyOffset(energy_offset=800.0, exposure_time=400e-6, nr_frames=1)
        offset_5 = EnergyOffset(energy_offset=1000.0, exposure_time=800e-6, nr_frames=1)

        ef_settings = EnergyFilterSettings()
        ef_settings.drift_tube_mode = DriftTubeMode.FullRangeFast
        ef_settings.energy_offsets = [offset_1, offset_2, offset_3, offset_4, offset_5]

        eels_detector_settings = EelsDetectorSettings()
        eels_detector_settings.corrected = True
        eels_detector_settings.exposure_time = 0.1  # not required for this experiment

        eels_detector_storage_settings = EelsDetectorStorageSettings()
        eels_detector_storage_settings.experiment_id = "Test 5-offset SI Experiment"
        eels_detector_storage_settings.delete_existing = True
        eels_detector_storage_settings.save_data = True
        eels_detector_storage_settings.data_location = r"c:\temp\EelsMinScriptingData"

        scan_settings = ScanSettings()
        scan_settings.area = (0, 0, 1, 1)
        scan_settings.resolution = 512
        scan_settings.dwell_time = 1e-6
        scan_settings.mains_lock_active = False
        scan_settings.line_scan_orientation_vertical = False
        scan_settings.serpentine_scan = False
        scan_settings.selected_stem_detectors = ["HAADF"]

        si_settings = SpectrumImageSettings(
            scan_settings=scan_settings, eels_detector_settings=eels_detector_settings,
            eels_detector_storage_settings=eels_detector_storage_settings,
            energy_filter_settings=ef_settings)

        eels_min_script.abort_experiment()  # just in case something was still running
        eels_min_script.start_spectrum_image_experiment(spectrum_image_settings=si_settings)
        eels_min_script.wait_for_experiment_finished()
        # now you can retrieve the acquired data
        results = eels_min_script.get_last_results()
        if 'hdf5_file_name' in results:
            print("Data is saved to: {}".format(results.get('hdf5_file_name', "")))
    finally:
        if eels_min_script is not None:
            logger.info("EELS Script releasing environment")
            eels_min_script.release()
        logger.info("EELS SI Script finished")