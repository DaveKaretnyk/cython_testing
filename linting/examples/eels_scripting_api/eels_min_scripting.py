# Copyright (c) 2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from tfs_eels.scripting.eels_min_scripting_environment import EelsMinScriptingEnvironment
from .eels_min_scripting_itf import EelsMinScriptingInterface


class EelsMinScripting(EelsMinScriptingInterface):
    def __init__(self, log_to_console=True, log_to_file=True, log_file_name=""):
        self.__eelsmin_scripting_environment = EelsMinScriptingEnvironment(
            log_to_console=log_to_console, log_to_file=log_to_file, log_file_name=log_file_name)

    def release(self):
        """
        Will free all the used resources
        :return:
        """
        if self.__eelsmin_scripting_environment is not None:
            self.__eelsmin_scripting_environment.release()
            self.__eelsmin_scripting_environment = None

    def set_live_data_callback(self, live_data_callback):
        """
        Sets a callback function that receives a list of tuples
        the tuple will be in the form: (energies [in eV], counts_at_energies) and
        represents the spectra data for each defined energy offset
        please note that not all data is send through this callback;
        It will be a limited data_rate to enable live viewing and/or processing;
        Also note that you should not do the actual processing in the callback itself but decouple,
        otherwise it may block and/or influence the stability of the system.
        :param live_data_callback: call_back function
        :return:
        """
        self.__eelsmin_scripting_environment.set_live_data_callback(live_data_callback)

    def wait_for_experiment_finished(self):
        """
        Returns once experiment is finished
        :return:
        """
        self.__eelsmin_scripting_environment.wait_for_experiment_finished()

    def wait_for_experiment_started(self, timeout=20.0):
        """
        Returns once experiment is started
        :return:
        """
        self.__eelsmin_scripting_environment.wait_for_experiment_started(timeout=timeout)

    def abort_experiment(self):
        """
        Aborts running experiment
        :return:
        """
        self.__eelsmin_scripting_environment.abort_experiment()

    def is_experiment_active(self):
        """
        Returns whether experiment is still active or not
        :return:
        """
        return self.__eelsmin_scripting_environment.is_experiment_active()

    def start_spectrum_image_experiment(self, spectrum_image_settings):
        """
        Will start a spectrum image experiment with (Multi-)Eels and stem data
        When finished get_last_results will return dictionary that may contain the following keys:
        - 'hdf5_file_name' : name of resulting HDF5 file (Hyperspy format)
        :param spectrum_image_settings:
        :return:
        """
        self.__eelsmin_scripting_environment.start_spectrum_image_experiment(
            spectrum_image_settings)

    def start_eels_experiment(self, eels_settings):
        """
        Depending on settings, will start a (multi-)eels experiment
        When finished get_last_results will return dictionary that may contain the following keys:
        - 'hdf5_file_name' : name of resulting HDF5 file (Hyperspy format)
        :param eels_settings:
        :return:
        """
        self.__eelsmin_scripting_environment.start_eels_experiment(eels_settings)

    def acquire_single_spectra(self, acquire_single_spectra_settings):
        """
        Will acquire one set of spectra; 1 or more spectra depending on energy offsets defined

        :param acquire_single_spectra_settings:
        :return: list of one or more tuples (depending on number of energy_offsets defined)
                 tuples are of form (energies [in ev], counts_at_energies)
        """
        return self.__eelsmin_scripting_environment.acquire_single_spectra(
            acquire_single_spectra_settings)

    def get_last_results(self):
        """
        Retrieves results of recently executed procedure
        :return: dictionary, content depends on executed procedure
        """
        return self.__eelsmin_scripting_environment.get_last_results()

    def acquire_single_data(self, exposure_time, target_sensor, prepare_system=True):
        """
        Returns data from a single acquisition (not continuous mode)
        :param exposure_time: the exposure time in secs
        :param target_sensor: 0=image detector 1=eels detector
        :param prepare_system: to setup the system (e.g. cdd to deflect to correct position)
        :return: Will return a tuple of (np_data, metadatalist)
        """
        return self.__eelsmin_scripting_environment.acquire_single_data(
            exposure_time=exposure_time, target_sensor=target_sensor,
            prepare_system=prepare_system)

    def start_continuous_data(self, exposure_time,
                              target_sensor,
                              prepare_system=True):
        """
        Starts a continuous acquisition on selected sensor
        Use get_last_data to retrieve last received data
        :param exposure_time: The exposure time in sec
        :param target_sensor: 0=image detector 1=eels detector
        :param prepare_system: to setup the system (e.g. cdd to deflect to correct position)
        :return:
        """
        return self.__eelsmin_scripting_environment.start_continuous_data(
            exposure_time=exposure_time, target_sensor=target_sensor,
            prepare_system=prepare_system)

    def stop_continuous_data(self):
        """
        Will stop a previously started continuous acquisition
        :return:
        """
        self.__eelsmin_scripting_environment.stop_continuous_data()

    def get_last_data(self, skip_count=0):
        """
        Will return last received data for a single position
        Will return a tuple of (np_data, metadatalist)
        :param skip_count: number of data packages to skip before return This may be necessary
        to avoid getting data collected while action you did before was executing
        :return:
        """
        return self.__eelsmin_scripting_environment.get_last_data(skip_count=skip_count)

    def acquire_sw_synchronized_eels_experiment(self, settings):
        """

        :param settings:
        :return:
        """
        return self.__eelsmin_scripting_environment.acquire_sw_synchronized_eels_experiment(settings)
