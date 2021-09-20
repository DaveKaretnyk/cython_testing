# Copyright (c) 2012-2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.


from tfs_eels.scripting_api.eels_min_scripting import EelsMinScripting
from tfs_eels.scripting_api.eels_min_scripting_data_types import (
    EelsDetectorSettings,
    EnergyOffset, DriftTubeMode, EnergyFilterSettings,
    AcquireSingleSpectraSettings
)

if __name__ == '__main__':
    eels_min_script = None
    try:
        eels_min_script = EelsMinScripting(log_to_console=False, log_to_file=True,
                                           log_file_name=r'c:\temp\eels_min_scripting_test')
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

        acq_single_settings = AcquireSingleSpectraSettings(
            eels_detector_settings=eels_detector_settings,
            energy_filter_settings=ef_settings)

        eels_min_script.abort_experiment()  # just in case something was still running
        received_spectra = eels_min_script.acquire_single_spectra(
            acquire_single_spectra_settings=acq_single_settings)
        # now received spectra contains a list of spectra related to offsets specified

        print("Received {} spectra".format(len(received_spectra)))
        for (energies, counts_at_energies) in received_spectra:
            # plot the data, or do something else
            pass
    finally:
        if eels_min_script is not None:
            eels_min_script.release()
