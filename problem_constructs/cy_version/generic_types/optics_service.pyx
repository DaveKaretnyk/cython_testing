# Copyright(c) 2021 by Thermo Fisher Scientific
# All rights reserved. This file includes confidential and proprietary information
# of Thermo Fisher Scientific
from collections.abc import Iterable
from typing import Callable, Tuple

from fei_common.tem.omp.api import Subscription

from fei_common.infra.tem_service.omp_control.api import OpticsControl

from fei_common.infra.tem_service.interface.beam_current_calibration_data import (
    BeamCurrentCalibrationData)
from fei_common.infra.tem_service.interface.column_mode import ColumnMode
from fei_common.infra.tem_service.interface.column_operating_mode import ColumnOperatingMode
from fei_common.infra.tem_service.interface.config_not_supported_exception import (
    ConfigNotSupportedException)
from fei_common.infra.tem_service.interface.configuration_service import ConfigurationService
from fei_common.infra.tem_service.interface.magnification_info import MagnificationInfo
# Cython issue: APITS_260
# from fei_common.infra.tem_service.interface.normalization import Normalization


class OpticsService:
    """ Provide access to Optics related parameters of the microscope.

    That is, get/set access to various parameters: defocus, various
    stigmator values, lens values, magnification, optical mode, etc.
    """

    def __init__(self, optics_control: OpticsControl,
                 configuration_service: ConfigurationService) -> None:
        super().__init__()
        self._tem = optics_control
        self._config = configuration_service

    def get_stem_objective_focus(self):
        """ Get the current STEM Objective focus value.

        :return float
        """
        return self._tem.get_stem_objective_focus()

    def set_stem_objective_focus(self, focus, delay=0.1):
        """ Set the STEM Objective focus value.

        """
        return self._tem.set_stem_objective_focus(focus, delay)

    def get_stem_objective_defocus(self):
        """ Get the current STEM Objective defocus value.

        :return float
        """
        return self._tem.get_stem_objective_defocus()

    def set_stem_objective_defocus(self, defocus, delay=0.1):
        """ Set the STEM Objective defocus value.

        """
        return self._tem.set_stem_objective_defocus(defocus, delay)

    def is_reset_stem_objective_defocus_supported(self):
        """ Verify whether or not it is possible to reset the STEM objective defocus.
        On TEM server versions prior to 7.4 the STEM objective defocus cannot be reset.

        :return: True when the STEM objective defocus can be reset, otherwise False.
        """
        return self._tem.is_reset_stem_objective_defocus_supported()

    def reset_stem_objective_defocus(self):
        """ Reset STEM objective defocus value.

        """
        self._tem.reset_stem_objective_defocus()

    def get_stem_intensity_focus(self):
        """ Get the current STEM Intensity focus (unitless) value.
        Throws exception if current mode is TEM.

        :return float
        """
        return self._tem.get_stem_intensity_focus()

    def set_stem_intensity_focus(self, focus, delay=0.1):
        """ Set the current STEM Intensity focus (unitless) value. Throws exception
        if setting value fails (value out of bounds) and maximal / minimal allowed value is set.
        Throws exception if current mode is TEM.

        """
        self._tem.set_stem_intensity_focus(focus, delay)

    def get_stem_intensity_defocus(self):
        """ Get the current STEM Intensity defocus value.

        :return float
        """
        return self._tem.get_stem_intensity_defocus()

    def set_stem_intensity_defocus(self, defocus, delay=0.1):
        """ Set the current STEM Intensity defocus value.

        """
        self._tem.set_stem_intensity_defocus(defocus, delay)

    def is_reset_stem_intensity_defocus_supported(self):
        """ Verify whether or not it is possible to reset the STEM intensity defocus.
        On TEM server versions prior to 7.4 the STEM intensity defocus cannot be reset.

        :return: True when the STEM intensity defocus can be reset, otherwise False.
        """
        return self._tem.is_reset_stem_intensity_defocus_supported()

    def reset_stem_intensity_defocus(self):
        """ Reset STEM intensity defocus value.

        """
        self._tem.reset_stem_intensity_defocus()

    def set_tem_focus(self, focus: float, delay: float = 0.1) -> None:
        """
        Set the TEM focus value [excitation units]
        :param focus: TEM Focus value to set
        :param delay: a delay that follows the setting.
        """
        self._tem.set_tem_focus(focus, delay)
        return None

    def get_tem_focus(self) -> float:
        """
        Get the current TEM focus value [excitation units]
        :return TEM Focus value
        """
        return self._tem.get_tem_focus()

    def set_tem_focus_in_meters(self, focus: float) -> None:
        """
        Set the TEM focus value [meters]
        :param focus: TEM Focus value to set in meters
        """
        self._tem.set_tem_focus_in_meters(focus)
        return None

    def get_tem_focus_in_meters(self) -> float:
        """
        Get the current TEM focus value [meters]
        :return TEM Focus value in meters
        """
        return self._tem.get_tem_focus_in_meters()

    def get_tem_focus_calibration_factor(self) -> float:
        """
        Get the TEM focus calibration factor.
        """
        return self._tem.get_tem_focus_calibration_factor()

    def set_tem_focus_calibration_factor(self, value: float) -> None:
        """
        Set the TEM focus calibration factor.
        """
        self._tem.set_tem_focus_calibration_factor(value)
        return None

    def reset_tem_defocus(self) -> None:
        """
        Reset TEM defocus value.
        """
        self._tem.reset_tem_defocus()
        return None

    def is_reset_tem_defocus_supported(self):
        """ Verify whether or not it is possible to reset the TEM defocus.
        On TEM server versions prior to 7.0 the TEM defocus cannot be reset.

        :return: True when the TEM defocus can be reset, otherwise False.
        """
        return self._tem.is_reset_tem_defocus_supported()

    def set_tem_defocus(self, defocus: float, delay: float = 0.1) -> None:
        """
        Set the TEM defocus value.
        """
        self._tem.set_tem_defocus(defocus, delay)
        return None

    def get_tem_defocus(self) -> float:
        """
        Get the current TEM defocus value.
        :return float
        """
        return self._tem.get_tem_defocus()

    def stigmator_set_condenser(self, x, y=None):
        """ Set the Condenser Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_condenser_stigmator, x, y)

    def stigmator_get_condenser(self):
        """ Get the Condenser Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_condenser_stigmator()

    def stigmator_change_condenser(self, x, y=None):
        """ Change the Condenser Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_condenser_stigmator, x, y)

    def stigmator_get_condenser_deflection_factor(self):
        """ Get the deflection factors of the condenser stigmator.

        :return Matrix2x2
        """
        return self._tem.get_condenser_stigmator_deflection_factor()

    def stigmator_set_condenser_deflection_factor(self, value):
        """ Set the deflection factors of the condenser stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_condenser_stigmator_deflection_factor(value)

    def stigmator_set_condenser_3fold(self, x, y=None):
        """ Set the 3-fold Condenser Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_condenser_stigmator_3fold, x, y)

    def stigmator_get_condenser_3fold(self):
        """ Get the 3-fold Condenser Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :return X and Y 3-fold stigmator values respectively (tuple of floats)
        """
        return self._tem.get_condenser_stigmator_3fold()

    def stigmator_change_condenser_3fold(self, x, y=None):
        """ Change the 3-fold Condenser Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_condenser_stigmator_3fold, x, y)

    def stigmator_get_condenser_3fold_deflection_factor(self):
        """ Get the deflection factors of the condenser-3fold stigmator.

        :return Matrix2x2
        """
        return self._tem.get_condenser_stigmator_3fold_deflection_factor()

    def stigmator_set_condenser_3fold_deflection_factor(self, value):
        """ Set the deflection factors of the condenser stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_condenser_stigmator_3fold_deflection_factor(value)

    def stigmator_get_condenser_3fold_deflection_factor_3fold_to_2fold(self):
        """ Get the 3fold to 2fold deflection factors of the condenser-3fold stigmator.

        :return Matrix2x2
        """
        return self._tem.get_condenser_stigmator_3fold_deflection_factor_3fold_to_2fold()

    def stigmator_set_condenser_3fold_deflection_factor_3fold_to_2fold(self, value):
        """ Set the 3fold to 2fold deflection factors of the condenser-3fold stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_condenser_stigmator_3fold_deflection_factor_3fold_to_2fold(value)

    def stigmator_set_coma(self, x, y=None):
        """ Set the coma correction (X and Y). (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_coma_stigmator, x, y)

    def stigmator_get_coma(self):
        """ Get the coma correction value (X and Y). (non-physical units, between -1 and +1)

        :return X and Y coma values respectively (tuple of floats)
        """
        return self._tem.get_coma_stigmator()

    def stigmator_change_coma(self, x, y=None):
        """ Change the coma correction by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_coma_stigmator, x, y)

    def stigmator_set_gun(self, x, y=None):
        """ Set the Gun Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_gun_stigmator, x, y)

    def stigmator_get_gun(self):
        """ Get the Gun Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_gun_stigmator()

    def stigmator_change_gun(self, x, y=None):
        """ Change the Gun Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_gun_stigmator, x, y)

    def stigmator_get_gun_deflection_factor(self):
        """ Get the deflection factors of the gun stigmator.

        :return Matrix2x2
        """
        return self._tem.get_gun_stigmator_deflection_factor()

    def stigmator_set_gun_deflection_factor(self, value):
        """ Set the deflection factors of the gun stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_gun_stigmator_deflection_factor(value)

    def stigmator_set_objective(self, x, y=None):
        """ Set the Objective Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_objective_stigmator, x, y)

    def stigmator_get_objective(self):
        """ Get the Objective Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_objective_stigmator()

    def stigmator_change_objective(self, x, y=None):
        """ Change the Objective Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_objective_stigmator, x, y)

    def stigmator_get_objective_deflection_factor(self):
        """ Get the deflection factors of the objective stigmator.

        :return Matrix2x2
        """
        return self._tem.get_objective_stigmator_deflection_factor()

    def stigmator_set_objective_deflection_factor(self, value):
        """ Set the deflection factors of the objective stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_objective_stigmator_deflection_factor(value)

    def stigmator_set_objective_3fold(self, x, y=None):
        """ Set the 3-fold Objective Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_objective_stigmator_3fold, x, y)

    def stigmator_set_image_corrector_astigmatism(self, x, y=None):
        """ Set the Image Corrector Astigmatism Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_image_corrector_astigmatism_stigmator, x, y)

    def stigmator_set_probe_corrector_astigmatism(self, x, y=None):
        """ Set the Probe Corrector Astigmatism Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_probe_corrector_astigmatism_stigmator, x, y)

    def stigmator_get_probe_corrector_astigmatism(self) -> Tuple[float, float]:
        """ Get the   Probe Corrector Astigmatism Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_probe_corrector_astigmatism_stigmator()

    def stigmator_get_objective_3fold(self):
        """ Get the 3-fold Objective Stigmator value (X and Y).
        (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_objective_stigmator_3fold()

    def stigmator_change_objective_3fold(self, x, y=None):
        """ Change the 3-fold Objective Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_objective_stigmator_3fold, x, y)

    def stigmator_get_objective_3fold_deflection_factor(self):
        """ Get the deflection factors of the objective-3fold stigmator.

        :return Matrix2x2
        """
        return self._tem.get_objective_stigmator_3fold_deflection_factor()

    def stigmator_set_objective_3fold_deflection_factor(self, value):
        """ Set the deflection factors of the objective 3-fold stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_objective_stigmator_3fold_deflection_factor(value)

    def stigmator_set_diffraction(self, x, y=None):
        """ Set the Diffraction Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :param x stigmator X value or a tuple of X and Y values (floats)
        :param y stigmator Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_diffraction_stigmator, x, y)

    def stigmator_get_diffraction(self):
        """ Get the Diffraction Stigmator value (X and Y). (non-physical units, between -1 and +1)

        :return X and Y stigmator values respectively (tuple of floats)
        """
        return self._tem.get_diffraction_stigmator()

    def stigmator_change_diffraction(self, x, y=None):
        """ Change the Diffraction Stigmator by the supplied deltas.

        :param x stigmator X delta or a tuple of X and Y deltas (floats)
        :param y stigmator Y delta or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.change_diffraction_stigmator, x, y)

    def stigmator_get_diffraction_deflection_factor(self):
        """ Get the deflection factors of the diffraction stigmator.

        :return Matrix2x2
        """
        return self._tem.get_diffraction_stigmator_deflection_factor()

    def stigmator_set_diffraction_deflection_factor(self, value):
        """ Set the deflection factors of the diffraction stigmator.

        :param value: Matrix2x2
        """
        self._tem.set_diffraction_stigmator_deflection_factor(value)

    def get_probe_convergence_semi_angle(self):
        """ Get the convergence semi-angle of the STEM probe.

        :return semi-angle in radians (float)
        :exception ConfigNotSupportedException
        """
        return self._tem.get_probe_convergence_semi_angle()

    def set_probe_convergence_semi_angle(self, angle):
        """ Set the convergence semi-angle of the STEM probe.

        Only supported on Titan - exception raised on other microscope
        families.

        :param angle semi-angle in radians (float)
        :exception ConfigNotSupportedException

        ISSUE: CURRENTLY CALLER SHOULD PAUSE AFTER CHANGING THE VALUE TO
        ALLOW IT TO SETTLE.
        """
        if self._config.is_titan():
            self._tem.set_probe_convergence_semi_angle(angle)
        else:
            raise ConfigNotSupportedException(
                "Probe convergence angle not implemented for current configuration")

    def get_full_scan_field_of_view(self):
        """ Get the STEM full-scan FOV.

        :return X and Y value a tuple of floats
        """
        return self._tem.get_full_scan_field_of_view()

    def set_spot_size_index(self, index: int) -> None:
        """ Set the Spot Size index.

        :param index int
        """
        self._tem.set_spot_size_index(index)

    def get_spot_size_index(self) -> int:
        """ Get the current Spot Size index.

        :return int
        """
        return self._tem.get_spot_size_index()

    def get_minimum_spot_size_index(self) -> int:
        return self._tem.get_minimum_spot_size_index()

    def get_maximum_spot_size_index(self) -> int:
        return self._tem.get_maximum_spot_size_index()

    def is_hm_sub_mode_sa(self):
        """ Is the sub mode of the current magnification SA?

        :return bool
        """
        return self._tem.is_hm_sub_mode_sa()

    def get_objective_mode(self):
        """ Get the current objective mode (LM/HM/Lorentz)

        :return enum fei_common.infra.tem_service.api.ObjectiveMode
        """
        return self._tem.get_objective_mode()

    def set_objective_mode(self, objective_mode):
        """ Set the current objective mode (LM/HM/Lorentz)

        :param objective_mode enum fei_common.infra.tem_service.api.ObjectiveMode
        """
        self._tem.set_objective_mode(objective_mode)

    def get_current_magnification(self):
        """ Get the current magnification index. So NOT the actual mag. value
        but the index to the value.

        Return index to current value, flag indicating TEM imaging mode, and
        max possible index.
        :return tuple of (int, bool, int)
        """
        _index, _, _in_imaging, _max_index = self._tem.get_current_mag_value()
        return _index, _in_imaging, _max_index

    def get_current_magnification_info(self, typed_submode=False):
        """ Get the current magnification information.

        :param typed_submode: (bool) if True, return sub-mode as  (enum MagnificationSubMode)
        :return MagnificationInfo:
            index to current value      (int)
            in imaging mode flag?       (bool)
            maximum possible index      (int)
            display magnification       (float)
            nominal magnification       (float)
            is calibrated flag?         (bool)
            calibrated magnification    (float)
            rotation                    (float)
            sub-mode                    (basestring) or (enum fei_common.infra.tem_service.api.
                                        MagnificationSubMode)
        """
        _index, _current_magnification, _in_imaging, _max_index = self._tem.get_current_mag_value()
        display, nominal, is_calibrated, calibrated_value, rotation, sub_mode, is_imaging = \
            self._tem.get_magnification_info(_current_magnification, typed_submode)
        magnification_info = MagnificationInfo(_index, _in_imaging, _max_index, display, nominal,
                                               is_calibrated, calibrated_value, rotation, sub_mode)
        return magnification_info

    def get_magnification_info(self, index, typed_submode=False):
        """ Get the  magnification information for the specified index.

        :param index: (int)
        :param typed_submode: (bool) if True, return sub-mode as  (enum MagnificationSubMode)
        :return MagnificationInfo:
            index to current value      (int)
            in imaging mode flag?       (bool)
            maximum possible index      (int)
            display magnification       (float)
            nominal magnification       (float)
            is calibrated flag?         (bool)
            calibrated magnification    (float)
            rotation in radians         (float)
            sub-mode                    (basestring) or (enum fei_common.infra.tem_service.api.
                                        MagnificationSubMode)
        """
        _magnification, _max_index = self._tem.get_mag_value(index)
        display, nominal, is_calibrated, calibrated_value, rotation, sub_mode, is_imaging = \
            self._tem.get_magnification_info(_magnification, typed_submode)
        magnification_info = MagnificationInfo(index, is_imaging, _max_index, display, nominal,
                                               is_calibrated, calibrated_value, rotation, sub_mode)
        return magnification_info

    def set_magnification_index(self, index):
        """ Set the magnification index to the supplied value.
        Note: It is preferred to use set_magnification with display magnification values, as those
        are more resistant to custom magnification ranges.

        :param index int
        """
        self._tem.set_magnification_index(index)

    def set_magnification(
            self,
            display_magnification: float,
            search_nearest_magnification: bool = True,
            force_over_the_hill_magnification_range: bool = False
    ):
        """ In the current objective mode, change magnification to the requested display
            magnification.
            :param display_magnification: The desired display magnification
            :param search_nearest_magnification: When the requested nominal magnification does not
                   exist, use the nearest magnification.
            :param force_over_the_hill_magnification_range: On some systems the Mh magnification
                   increases to a maximal magnification and from that point on the magnification
                   actually decreases when the magnification index is increased.
                   Those decreasing magnifications are called 'over the hill' magnifications.
                   When force_over_the_hill_magnification_range is False (the default) it will not
                   change the magnification to any of the 'over the hill' magnifications.
                   When force_over_the_hill_magnification_range is True, it will change to nearest
                   or exact magnification in the 'over the hill' magnifications.
                   The maximum magnification is considered the largest number in both ranges, and
                   can be reached either with force_over_the_hill_magnification_range True or False.
            :returns None:
        """
        self._tem.set_display_magnification(
            magnification=display_magnification,
            search_nearest_magnification=search_nearest_magnification,
            force_over_the_hill_magnification_range=force_over_the_hill_magnification_range
        )

    def get_nearest_display_magnification(
            self, magnification: float, column_mode: ColumnMode) -> float:
        """ In the current objective mode, change magnification to the requested display
            magnification.
            :param magnification: The desired display magnification
            :param column_mode: Column mode where magnification should be found
            :returns: the nearest magnification
        """
        return self._tem.get_nearest_display_magnification(magnification, column_mode)

    def get_magnification_index(self):
        """ Get the index of the current magnification.

        :return int
        """
        return self.get_current_magnification_info().index

    def get_available_mags(self):
        """
        Get list of all available magnifications.
        :return list of tuples (int, float) mag. index, display magnification
        """
        return self._tem.get_available_mags()

    def get_available_magnifications_for_mode(self, column_mode):
        """
        Get list of Magnification info for all magnifications available for the given column mode.
        :param column_mode: (fei_common.infra.tem_service.api.ColumnMode)
        :return: (list of (fei_common.infra.tem_service.api.MagnificationInfo))
        """
        mags_for_mode = self._tem.get_available_mags_for_mode(column_mode)
        max_index = len(mags_for_mode) - 1
        return [
            MagnificationInfo(
                index, is_imaging, max_index, display, nominal, is_calibrated, calibrated_value,
                rotation, sub_mode)
            for index, (display, nominal, is_calibrated, calibrated_value, rotation, sub_mode,
                        is_imaging) in mags_for_mode.items()]

    def get_stem_rotation_in_rad(self):
        """ Get STEM rotation value.

        :return rotation in radians (float)
        """
        return self._tem.get_stem_rotation_in_rad()

    def set_stem_rotation(self, angle_in_rad):
        """ Set the STEM rotation.

        :param angle_in_rad angle in radians (float)
        """
        self._tem.set_stem_rotation(angle_in_rad)

    def in_stem_mode(self):
        """ Are the Optics in STEM mode?

        :return bool
        """
        return self._tem.in_stem_mode()

    def in_tem_mode(self):
        """ Are the Optics in TEM mode?

        :return bool
        """
        return self._tem.in_tem_mode()

    def get_intensity(self):
        """ Get the Intensity (C2) value.

        :return float
        """
        return self._tem.get_intensity()

    def set_intensity(self, intensity):
        """ Set the Intensity (C2 value.

        :param intensity float
        """
        self._tem.set_intensity(intensity)

    def set_align_beam_shift(self, x, y=None):
        """ Set the Aligned Beam Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_beam_shift, x, y)

    def get_align_beam_shift(self):
        """ Get the Aligned Beam Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_align_beam_shift()

    def set_align_beam_tilt(self, x, y=None):
        """ Set the Aligned Beam Tilt. (non-physical units, between -1 and +1)

        :param x: tilt X value or a tuple of X and Y values (floats)
        :param y: tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_beam_tilt, x, y)

    def get_align_beam_tilt(self):
        """ Get the Aligned Beam Tilt value. (non-physical units, between -1 and +1)

        :return: X and Y, tuple of floats
        """
        return self._tem.get_align_beam_tilt()

    def set_condenser_tilt_offset(self, x, y=None):
        """ Set the condenser tilt offset (CT_Offset). (non-physical units, between -1 and +1)

        :param x: tilt X value or a tuple of X and Y values (floats)
        :param y: tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_condenser_tilt_offset, x, y)

    def get_condenser_tilt_offset(self):
        """ Get the condenser tilt offset (CT_Offset). (non-physical units, between -1 and +1)

        :return: X and Y, tuple of floats
        """
        return self._tem.get_condenser_tilt_offset()

    def is_condenser_dc_deflector_available(self):
        """ Check if the condenser DC deflector is available. """
        return self._tem.is_condenser_dc_deflector_available()

    def set_condenser_shift_offset(self, x, y=None):
        """ Set the condenser shift offset (CS_Offset). (non-physical units, between -1 and +1)

        :param x: shift X value or a tuple of X and Y values (floats)
        :param y: shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_condenser_shift_offset, x, y)

    def get_condenser_shift_offset(self):
        """ Get the condenser shift offset (CS_Offset). (non-physical units, between -1 and +1)

        :return: X and Y, tuple of floats
        """
        return self._tem.get_condenser_shift_offset()

    def is_condenser_shift_offset_supported(self):
        """ Verify whether or not it is possible to get/set the condenser shift offset.
        On TEM server versions prior to 7.5 the condenser shift offset value cannot be set.

        :return: True when the condenser shift offset can be set, otherwise False.
        """
        return self._tem.is_condenser_shift_offset_supported()

    def set_user_beam_shift(self, x, y=None):
        """ Set the User Beam Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_beam_shift, x, y)

    def get_user_beam_shift(self):
        """ Get the User Beam Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_beam_shift()

    def set_user_beam_tilt(self, x, y=None):
        """ Set the User Beam Tilt. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_beam_tilt, x, y)

    def get_user_beam_tilt(self):
        """ Get the User Beam Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_beam_tilt()

    def is_user_beam_tilt_supported(self):
        """ Verify whether or not it is possible to get/set the user beam tilt.
        On TEM server versions prior to 7.2 the user beam tilt value cannot be set.

        :return: True when the user beam tilt can be set, otherwise False.
        """
        return self._tem.is_user_beam_tilt_supported()

    def set_dark_field_tilt(self, x, y=None):
        """ Set the Dark Field Tilt. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_dark_field_tilt, x, y)

    def get_dark_field_tilt(self):
        """ Get the Dark Field Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_dark_field_tilt()

    def set_calibrated_beam_shift(self, x, y=None):
        """ Set the Calibrated Beam Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_calibrated_beam_shift, x, y)

    def get_calibrated_beam_shift(self):
        """ Get the Calibrated Beam Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_calibrated_beam_shift()

    def set_beam_tilt_pivot_point(self, x, y=None):
        """ Set the Beam Tilt Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_beam_tilt_pivot_point, x, y)

    def get_beam_tilt_pivot_point(self):
        """ Get the Beam Tilt Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_beam_tilt_pivot_point()

    def set_beam_shift_pivot_point(self, x, y=None):
        """ Set the Beam Shift Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_beam_shift_pivot_point, x, y)

    def get_beam_shift_pivot_point(self):
        """ Get the Beam Shift Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_beam_shift_pivot_point()

    def set_beam_lower_correction(self, x, y=None):
        """ Set the Beam Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :param x lower correction X value or a tuple of X and Y values (floats)
        :param y lower correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_beam_lower_correction, x, y)

    def get_beam_lower_correction(self):
        """ Get the Beam Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :return X and Y, tuple of floats
        """
        return self._tem.get_beam_lower_correction()

    def set_beam_perpendicular_correction(self, x, y=None):
        """ Set the Beam Deflector Perpendicular Correction.
        (non-physical units, between -1 and +0.25)

        :param x perp correction X value or a tuple of X and Y values (floats)
        :param y perp correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_beam_perpendicular_correction, x, y)

    def get_beam_perpendicular_correction(self):
        """ Get the Beam Deflector Perpendicular Correction.
        (non-physical units, between -1 and +0.25)

        :return X and Y, tuple of floats
        """
        return self._tem.get_beam_perpendicular_correction()

    def set_dark_field_tilt_calibration(self, calibration: Tuple[float, float]) -> None:
        """
        Set the Dark Field Tilt Calibration (beam tilt calibration for conversion
        of excitation units to radians).
        :param calibration: calibration factors for x and y coordinates
        :raises RuntimeError with HRESULT if not operating in DarkField mode.
        """
        return self._tem.set_dark_field_tilt_calibration(*calibration)

    def get_dark_field_tilt_calibration(self) -> Tuple[float, float]:
        """
        Get the Dark Field Tilt Calibration (beam tilt calibration for conversion
        of excitation units to radians).
        :raises RuntimeError with HRESULT if not operating in DarkField mode.
        :return calibration factors for x and y coordinates
        """
        return self._tem.get_dark_field_tilt_calibration()

    def set_user_gun_shift(self, x, y=None):
        """ Set the User Gun Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_gun_shift, x, y)

    def get_user_gun_shift(self):
        """ Get the User Gun Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_gun_shift()

    def set_align_gun_shift(self, x, y=None):
        """ Set the Aligned Gun Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_gun_shift, x, y)

    def get_align_gun_shift(self):
        """ Get the Aligned Gun Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_align_gun_shift()

    def set_align_gun_tilt(self, x, y=None):
        """ Set the Aligned Gun Tilt. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_gun_tilt, x, y)

    def get_align_gun_tilt(self):
        """ Get the Aligned Gun Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_align_gun_tilt()

    def set_gun_tilt_pivot_point(self, x, y=None):
        """ Set the Gun Tilt Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_gun_tilt_pivot_point, x, y)

    def get_gun_tilt_pivot_point(self):
        """ Get the Gun Tilt Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_gun_tilt_pivot_point()

    def set_gun_shift_pivot_point(self, x, y=None):
        """ Set the Gun Shift Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_gun_shift_pivot_point, x, y)

    def get_gun_shift_pivot_point(self):
        """ Get the Gun Shift Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_gun_shift_pivot_point()

    def set_gun_lower_correction(self, x, y=None):
        """ Set the Gun Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :param x lower correction X value or a tuple of X and Y values (floats)
        :param y lower correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_gun_lower_correction, x, y)

    def get_gun_lower_correction(self):
        """ Get the Gun Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :return X and Y, tuple of floats
        """
        return self._tem.get_gun_lower_correction()

    def set_align_image_shift(self, x, y=None):
        """ Set the Aligned Image Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_image_shift, x, y)

    def get_align_image_shift(self):
        """ Get the Aligned Image Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_align_image_shift()

    def set_align_image_tilt(self, x, y=None):
        """ Set the Aligned Image Tilt. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_align_image_tilt, x, y)

    def get_align_image_tilt(self):
        """ Get the Aligned Image Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_align_image_tilt()

    def set_calibrated_image_shift(self, x, y=None):
        """ Set the Calibrated Image Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_calibrated_image_shift, x, y)

    def get_calibrated_image_shift(self):
        """ Get the Calibrated Image Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_calibrated_image_shift()

    def set_calibrated_image_tilt(self, x, y=None):
        """ Set the Calibrated Image Tilt. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_calibrated_image_tilt, x, y)

    def get_calibrated_image_tilt(self):
        """ Get the Calibrated Image Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_calibrated_image_tilt()

    def set_user_image_shift(self, x, y=None):
        """ Set the User Image Shift. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_image_shift, x, y)

    def get_user_image_shift(self):
        """ Get the User Image Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_image_shift()

    def set_user_image_tilt(self, x, y=None):
        """ Set the User Image Tilt. (non-physical units, between -1 and +1)

        :param x shift X value or a tuple of X and Y values (floats)
        :param y shift Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_image_tilt, x, y)

    def get_user_image_tilt(self):
        """ Get the User Image Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_image_tilt()

    def is_user_image_tilt_supported(self):
        """ Verify whether or not it is possible to get/set the user image tilt.
        On TEM server versions prior to 7.2 the user image tilt value cannot be set.

        :return: True when the user image tilt can be set, otherwise False.
        """
        return self._tem.is_user_image_tilt_supported()

    def set_image_tilt_pivot_point(self, x, y=None):
        """ Set the Image Tilt Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_image_tilt_pivot_point, x, y)

    def get_image_tilt_pivot_point(self):
        """ Get the Image Tilt Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_image_tilt_pivot_point()

    def set_image_shift_pivot_point(self, x, y=None):
        """ Set the Image Shift Pivot Point. (non-physical units, between 2 and 6)

        :param x pivot point X value or a tuple of X and Y values (floats)
        :param y pivot point Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_image_shift_pivot_point, x, y)

    def get_image_shift_pivot_point(self):
        """ Get the Image Shift Pivot Point. (non-physical units, between 2 and 6)

        :return X and Y, tuple of floats
        """
        return self._tem.get_image_shift_pivot_point()

    def set_image_lower_correction(self, x, y=None):
        """ Set the Image Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :param x lower correction X value or a tuple of X and Y values (floats)
        :param y lower correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_image_lower_correction, x, y)

    def get_image_lower_correction(self):
        """ Get the Image Deflector Lower Correction. (non-physical units, between -0.2 and 0.2)

        :return X and Y, tuple of floats
        """
        return self._tem.get_image_lower_correction()

    def set_magnification_dependent_shift_correction(self, x, y=None):
        """ Set Magnification Dependent Shift Correction value.
        (non-physical units, between -1 and +1)

        :param x correction X value or a tuple of X and Y values (floats)
        :param y correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_magnification_dependent_shift_correction, x, y)

    def get_magnification_dependent_shift_correction(self):
        """ Get Magnification Dependent Shift Correction value.
        (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_magnification_dependent_shift_correction()

    def set_spot_list(self, x, y=None):
        """ Set the spot list value (non-physical units, between -1 and 1) """
        self._perform_tuple_function(self._tem.set_spot_list, x, y)

    def get_spot_list(self):
        """ Get the spot list value (non-physical units, between -1 and 1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_spot_list()

    def get_spot_list_array(self):
        return self._tem.get_spot_list_array()

    def set_spot_list_array(self, new_values):
        self._tem.set_spot_list_array(new_values)

    def set_calibrated_image_beam_tilt(self, x, y=None):
        """ Set the Calibrated Image-Beam Tilt. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_calibrated_image_beam_tilt, x, y)

    def get_calibrated_image_beam_tilt(self):
        """ Get the Calibrated Image-Beam Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_calibrated_image_beam_tilt()

    def set_calibrated_image_beam_shift(self, x, y=None):
        """ Set the Calibrated Image-Beam Shift. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_calibrated_image_beam_shift, x, y)

    def get_calibrated_image_beam_shift(self):
        """ Get the Calibrated Image-Beam Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_calibrated_image_beam_shift()

    def set_user_image_beam_tilt(self, x, y=None):
        """ Set the User Image-Beam Tilt. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_image_beam_tilt, x, y)

    def get_user_image_beam_tilt(self):
        """ Get the User Image-Beam Tilt value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_image_beam_tilt()

    def set_user_image_beam_shift(self, x, y=None):
        """ Set the User Image-Beam Shift. (non-physical units, between -1 and +1)

        :param x tilt X value or a tuple of X and Y values (floats)
        :param y tilt Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_user_image_beam_shift, x, y)

    def get_user_image_beam_shift(self):
        """ Get the User Image-Beam Shift value. (non-physical units, between -1 and +1)

        :return X and Y, tuple of floats
        """
        return self._tem.get_user_image_beam_shift()

    def is_imaging(self):
        """ Returns whether optics is in imaging or not

        :return: True when in imaging, otherwise False
        """
        return self._tem.is_imaging()

    def is_diffraction(self):
        """ Returns whether optics is in diffraction or not

        :return: True when in diffraction, otherwise False
        """
        return self._tem.is_diffraction()

    def set_diffraction(self, diffraction_active):
        """ Sets optics to diffraction (or back to imaging)

        :param diffraction_active: True: make diffraction active, False:
        switch of diffraction (back to imaging)
        """
        self._tem.set_diffraction(diffraction_active)

    def set_imaging(self):
        """ Sets optics to imaging

        """
        self._tem.set_imaging()

    def is_eftem_mode(self):
        """ Returns whether eftem lens series is active or not

        :return True: eftem active, otherwise not (regular lens series is
        active)
        """
        return self._tem.is_eftem_mode()

    def set_eftem_mode(self, eftem_mode_active):
        """ Sets optics to eftem lens serie (or back to regular)

        :param eftem_mode_active: True: make eftem lens serie active, False:
        switch back to regular lens serie
        """
        self._tem.set_eftem_mode(eftem_mode_active)

    def is_holography_mode(self):
        """Returns whether holography mode is active or not

        :return: True: holography active, otherwise false
        """
        return self._tem.is_holography_mode()

    def set_holography_mode(self, holography_mode_active):
        """ Sets optics to holography active / off

        :param holography_mode_active: True: make holography active, False: turn holography off
        """
        self._tem.set_holography_mode(holography_mode_active)

    def get_dark_field_mode(self):
        """ Returns current Dark Field mode.

        :return: enum fei_common.infra.tem_service.api.DarkFieldMode
        """
        return self._tem.get_dark_field_mode()

    def set_dark_field_mode(self, dark_field_mode):
        """ Sets optics to given Dark Field mode.

        :param dark_field_mode: enum fei_common.infra.tem_service.api.DarkFieldMode
        """
        self._tem.set_dark_field_mode(dark_field_mode)

    def is_nano_probe(self):
        """ Returns whether nano probe is active or not

        :return True: nano probe active, False: micro probe active
        """
        return self._tem.is_nano_probe()

    def get_probe_mode(self):
        """ Returns which probe mode is active.

        :return Either ProbeMode.Nano or ProbeMode.Micro
        """
        return self._tem.get_probe_mode()

    def set_nano_probe(self, nano_probe_active):
        """ Sets optics to nano probe (or back to micro probe)

        :param nano_probe_active: True: make nano probe active, False: switch
        back to micro probe
        """
        self._tem.set_nano_probe(nano_probe_active)

    def get_intensity_for_minimal_probe(self):
        """ Get intensity for minimal probe

        Note - exception thrown if system has 3 condenser lenses.
        :return: float
        """
        return self._tem.get_intensity_for_minimal_probe()

    def get_minimum_illuminated_area_diameter_for_parallel_beam(self):
        """ Get minimum illuminated area diameter for parallel beam

        :return: float
        """
        return self._tem.get_minimum_illuminated_area_diameter_for_parallel_beam()

    def get_maximum_illuminated_area_diameter_for_parallel_beam(self):
        """ Get maximum illuminated area diameter for parallel beam

        :return: float
        """
        return self._tem.get_maximum_illuminated_area_diameter_for_parallel_beam()

    def get_illuminated_area_diameter(self):
        """ Get illuminated area diameter.

        Illuminated area diameter in meters returned. Note - exception thrown
        if not Titan.
        :return float
        """
        return self._tem.get_illuminated_area_diameter()

    def set_illuminated_area_diameter(self, target):
        """ Set illuminated area diameter.

        Set the illuminated area diameter in meters. Client responsibility to
        pass sensible value in.
        :return float
        """
        self._tem.set_illuminated_area_diameter(target)

    def is_illumination_free_c3_off(self):
        """ Checks for Free control illumination mode C3 Off

        :return boolean
        """
        return self._tem.is_illumination_free_c3_off()

    def is_illumination_free_c2_off(self):
        """ Checks for Free control illumination mode C2 Off

        :return boolean
        """
        return self._tem.is_illumination_free_c2_off()

    def is_illumination_probe(self):
        """ Checks for illumination mode probe

        :return boolean
        """
        return self._tem.is_illumination_probe()

    def is_illumination_parallel(self):
        """ Checks for illumination mode parallel

        :return boolean
        """
        return self._tem.is_illumination_parallel()

    def is_illumination_probe_normal_angle(self):
        """ Checks for illumination mode probe normal angle

        :return boolean
        """
        return self._tem.is_illumination_probe_normal_angle()

    def is_illumination_probe_large_angle(self):
        """ Checks for illumination mode probe large angle

        :return boolean
        """
        return self._tem.is_illumination_probe_large_angle()

    def set_illumination_free_c3_off(self):
        """ Sets illumination mode to free control C3 Off
        """
        self._tem.set_illumination_free_c3_off()

    def set_illumination_free_c2_off(self):
        """ Sets illumination mode to free control C2 Off
        """
        self._tem.set_illumination_free_c2_off()

    def set_illumination_parallel(self):
        """ Sets parallel illumination mode
        """
        self._tem.set_illumination_parallel()

    def set_illumination_probe_normal_angle(self):
        """ Sets probe illumination normal angle mode
        """
        self._tem.set_illumination_probe_normal_angle()

    def set_illumination_probe_large_angle(self):
        """ Sets probe illumination large angle mode
        """
        self._tem.set_illumination_probe_large_angle()

    def set_basic_monochromator_tuning_mode(self):
        """ Set the optics suitable for monochromator turning.

        Specifically:
        * enum fei_common.infra.tem_service.api.ProjectorMode:
            to ProjectorMode.Imaging
        * enum fei_common.infra.tem_service.api.IlluminationMode:
            to IlluminationMode.Free
        * enum fei_common.infra.tem_service.api.IlluminationFreeSubMode:
            to IlluminationFreeSubMode.C3Off
        * enum fei_common.infra.tem_service.api.IlluminationProbeSubMode:
            to IlluminationProbeSubMode.NONE
        * enum fei_common.infra.tem_service.api.ObjectiveMode:
            to ObjectiveMode.HM
        * enum fei_common.infra.tem_service.api.EftemMode:
            to EftemMode.Off
        * enum fei_common.infra.tem_service.api.ProbeMode:
            to ProbeMode.Micro
        * enum fei_common.infra.tem_service.api.MonochromatorMode:
            to MonochromatorMode.Filtered
        * enum fei_common.infra.tem_service.api.ColumnOperatingTemSubMode:
            to ColumnOperatingTemSubMode.BrightField
            THIS SUB-MODE IS NOT NOT CURRENTLY IMPLEMENTED IN OMP SO WILL NOT
            BE SET.
        """
        self._tem.set_basic_monochromator_tuning_mode()

    def switch_to_stem(self):
        """ Switch to STEM.

        Specifically:
        * enum fei_common.infra.tem_service.api.ColumnOperatingMode:
            to ColumnOperatingTemSubMode.Stem
        * enum fei_common.infra.tem_service.api.ProjectorMode:
            to ProjectorMode.Diffraction
        * enum fei_common.infra.tem_service.api.ProbeMode:
            to ProbeMode.Nano
        * enum fei_common.infra.tem_service.api.ObjectiveMode:
            to ObjectiveMode.HM

        Does nothing if ColumnOperatingMode is already Stem.
        """
        self._tem.switch_to_stem()

    def switch_to_tem(self):
        """ Switch to TEM.

        Specifically:
        * enum fei_common.infra.tem_service.api.ColumnOperatingMode:
            to ColumnOperatingTemSubMode.Tem
        * enum fei_common.infra.tem_service.api.ProjectorMode:
            to ProjectorMode.Imaging
        * enum fei_common.infra.tem_service.api.ProbeMode:
            to ProbeMode.Micro
        * enum fei_common.infra.tem_service.api.ObjectiveMode:
            to ObjectiveMode.HM

        Does nothing if ColumnOperatingMode is already Tem.
        """
        self._tem.switch_to_tem()

    def set_column_operating_mode(self, column_operating_mode: ColumnOperatingMode) -> None:
        """ Switch to TEM or STEM keeping rest of the ColumnMode as is.

        Does nothing if ColumnOperatingMode is already set.
        """
        self._tem.set_column_operating_mode(column_operating_mode)

    def get_current_optics_mode_state(self):
        """ Return optics mode state as a list of sub-states.

        The state is defined by a number of sub-states, specifically:
        * enum fei_common.infra.tem_service.api.IlluminationMode.
        * enum fei_common.infra.tem_service.api.IlluminationFreeSubMode.
        * enum fei_common.infra.tem_service.api.IlluminationProbeSubMode.
        * enum fei_common.infra.tem_service.api.EftemMode.
        * enum fei_common.infra.tem_service.api.ColumnOperatingMode.
        * enum fei_common.infra.tem_service.api.ProbeMode.
        * enum fei_common.infra.tem_service.api.ProjectorMode.
        * enum fei_common.infra.tem_service.api.ObjectiveMode.

        Note that the following sub-states are not always returned:
        * enum fei_common.infra.tem_service.api.MonochromatorMode.
        * enum fei_common.infra.tem_service.api.ColumnOperatingTemSubMode.
            THIS SUB-MODE IS NOT NOT CURRENTLY IMPLEMENTED IN OMP SO WILL NOT
            BE RETURNED.

        Intended for use with the corresponding method
        restore_optics_mode_state on this same class.
        """
        return self._tem.get_current_optics_mode_state()

    def restore_optics_mode_state(self, optics_mode_state):
        """ Restore the optics mode state.

        The optics_mode_state supplied should be that provided by the
        corresponding method get_current_optics_mode_state.
        """
        self._tem.restore_optics_mode_state(optics_mode_state)

    def get_column_mode(self):
        """
        Read current Column Mode state
        :return: (fei_common.infra.tem_service.api.ColumnMode)
        """
        return self._tem.get_column_mode()

    def get_lens_value(self, lens_id):
        """ Get lens output value (non-physical units, between -1 and +1).

        :param lens_id: enum fei_common.infra.tem_service.api.LensId
        :return: float
        """
        return self._tem.get_lens_value(lens_id)

    def set_lens_value(self, lens_id, value):
        """ Set the output value of the specified lens as fraction of the
        maximal output (value is between - 1.0 and 1.0).

        :param fei_common.infra.tem_service.api.LensId lens_id: The lens whose output value
                                                               is to be set.
        :param float value: The desired output value of the lens.
        """
        self._tem.set_lens_value(lens_id, value)

    def is_set_lens_value_supported(self, lens_id):
        """ Verify whether or not it is possible to set the output value of the lens.
        On TEM server versions prior to 6.12 the lens output value cannot be set.

        :param fei_common.infra.tem_service.api.LensId lens_id: The lens to check.
        :return: True when the output value of the specified lens can be set, otherwise False.
        """
        return self._tem.is_set_lens_value_supported(lens_id)

    def get_lens_value_unscaled(self, lens_id):
        """ Get the output value of the specified lens value in unscaled optical units
        (value is between - max and max with max depending on HT).

        :param fei_common.infra.tem_service.api.LensId lens_id: The lens whose output value
                                                                       is desired.
        :return: float: The desired output value of the lens."""
        return self._tem.get_lens_value_unscaled(lens_id)

    def set_lens_value_unscaled(self, lens_id, value):
        """ Set the output value of the specified lens value in unscaled optical units
        (value is between - max and max with max depending on HT).

        :param fei_common.infra.tem_service.api.LensId lens_id: The lens whose output value
                                                                       is to be set.
        :param float value: The desired output value of the lens.
        """
        self._tem.set_lens_value_unscaled(lens_id, value)

    def get_lens_minimum_value_unscaled(self, lens_id):
        """
        Get the minimum unscaled value of the specified lens.

        :param LensId lens_id: The ID of the lens.
        :return: float: The minimum output value
        """
        return self._tem.get_lens_minimum_value_unscaled(lens_id)

    def get_lens_maximum_value_unscaled(self, lens_id):
        """
        Get the maximum unscaled value of the specified lens.

        :param LensId lens_id: The ID of the lens.
        :return: float: The maximum output value
        """
        return self._tem.get_lens_maximum_value_unscaled(lens_id)

    def is_set_lens_value_unscaled_supported(self, lens_id):
        """ Verify whether or not it is possible to set the output value of the lens.
        On TEM server versions prior to 7.8 the lens output value cannot be set.

        :param fei_common.infra.tem_service.api.LensId lens_id: The lens to check.
        :return: True when the output value of the specified lens can be set, otherwise False.
        """
        return self._tem.is_set_lens_value_unscaled_supported(lens_id)

    def get_objective_lens_focal_distance(self) -> float:
        """ Get objective lens focal distance

        The value returned depends on the current HT voltage. If the current HT
        does not match one of the predefined values (e.g. free HT is being used)
        then either the nearest value or a linear interpolated value is returned.

        Exception thrown if no values are available for the system lens type.

        :return: float Focal distance in meters
        """
        return self._tem.get_objective_lens_focal_distance()

    def get_cs(self) -> float:
        """ Get the spherical aberration coefficient.

        The value returned depends on the current HT voltage. If the current HT
        does not match one of the predefined values (e.g. free HT is being used)
        then either the nearest value or a linear interpolated value is returned.

        For a system with an image corrector in TEM mode a value of 0.0 is
        returned.
        For a system with a probe corrector in STEM mode a value of 0.0 is
        returned.

        Exception returned if no values are available for the system lens type.

        :return: float
        """
        return self._tem.get_cs()

    def get_cc(self) -> float:
        """ Get the chromatic aberration coefficient.

        The value returned depends on the current HT voltage. If the current HT
        does not match one of the predefined values (e.g. free HT is being used)
        then either the nearest value or a linear interpolated value is returned.

        Exception returned if no values are available for the system lens type.

        :return: float
        """
        return self._tem.get_cc()

    def get_smart_optics_alignment_mode_enabled(self):
        """ Get alignment mode flag of smart optics.

        This IOM interface is added in Tem6.13.

        :return: bool
        """
        return self._tem.get_smart_optics_alignment_mode_enabled()

    def set_smart_optics_alignment_mode_enabled(self, enable):
        """ Set alignment mode flag of smart optics. This equals the C2-alignment mode.

        This IOM interface is added in Tem6.13

        :param: enable: True to enable, False to disable.
        """
        self._tem.set_smart_optics_alignment_mode_enabled(enable)

    def get_c2_image_distance(self):
        """ Return the image distance of the C2 that is used for smart optics.
        This IOM interface is added in Tem6.13

        :return image_distance in meters.
        """
        return self._tem.get_c2_image_distance()

    def set_c2_image_distance(self, value):
        """ Set smart optics C2-image distance.
        This is only allowed when set_smart_optics_alignment_mode_enabled is enabled.

        :param value  Image distance in meters .
        """
        return self._tem.set_c2_image_distance(value)

    def get_c3_image_distance_parallel_offset(self):
        """ get smart optics C3-image distance offset for parallel mode.

        :return: value  Image distance parallel offset in meters .
        """
        return self._tem.get_c3_image_distance_parallel_offset()

    def set_c3_image_distance_parallel_offset(self, value):
        """ Set smart optics C3-image distance offset for parallel mode.

        param value  Image distance parallel_offset in meters .
        """
        return self._tem.set_c3_image_distance_parallel_offset(value)

    def is_aberration_free_image_beam_shift_enabled(self):
        """ Get if afis is enabled.

        :return: bool
        """
        return self._tem.is_aberration_free_image_beam_shift_enabled()

    def enable_aberration_free_image_beam_shift(self):
        """ Enable afis.

        """
        self._tem.enable_aberration_free_image_beam_shift()

    def disable_aberration_free_image_beam_shift(self):
        """ Disable afis.

        """
        self._tem.disable_aberration_free_image_beam_shift()

    def is_aberration_free_image_beam_shift_is_aligned_supported(self):
        """ Get if afis is_aligned is supported.

        :return: bool
        """
        return self._tem.is_aberration_free_image_beam_shift_is_aligned_supported()

    def is_aberration_free_image_beam_shift_aligned(self, probe_mode):
        """ Get if afis is aligned for probe_mode.

        :return: bool
        """
        return self._tem.is_aberration_free_image_beam_shift_aligned(probe_mode)

    def is_auto_normalize_enabled(self):
        """ Get if auto normalization is enabled.

        :return: bool
        """
        return self._tem.is_auto_normalize_enabled()

    def enable_auto_normalize(self, enable):
        """ Enable/Disable auto normalization

        :param enable: True if auto-normalization is to be enabled, False to disable
        """
        self._tem.enable_auto_normalize(enable)

    # Cython issue: APITS-260, causes:
    #   TypeError: 'ABCMeta' object is not subscriptable
    # def execute_normalizations(self, normalizations: Iterable[Normalization]) -> None:
    def execute_normalizations(self, normalizations) -> None:
        """ Perform normalization of the specified sub systems.
        This method is synchronous. It typically takes several seconds to
        complete on a real system depending on number of normalizations executed.

        :param normalizations: Iterable (of fei_common.infra.tem_service.api.Normalization)
        """
        self._tem.execute_normalizations(normalizations)

    def save_alignments_to_file(self, file_name: str) -> None:
        """ Save Optics alignments to the given file.
        (C:\\Titan\\Alg\\file_name.alg is created; C:\\Tecnai\\Alg\\file_name.alg on Talos)

        :param file_name: basestring name of the file where to save the alignments
        """
        self._tem.save_alignments_to_file(file_name)

    def save_alignments_to_file_path(self, folder_path: str, file_name: str) -> bool:
        """
        Save Optics alignments to the given file in the given folder.
        :param folder_path: the path where the .alg file should be created
        :param file_name: name of the .alg file
        :return True if operation was executed, False if it is not supported
        """
        return self._tem.save_alignments_to_file_custom_path(folder_path, file_name)

    def load_alignments_from_file(self, file_name: str) -> None:
        """ Load Optics alignments from the given file.
        (C:\\Titan\\Alg\\file_name.alg is loaded; C:\\Tecnai\\Alg\\file_name.alg on Talos)

        :param file_name: basestring name of the file from which alignments are to be loaded
        """
        self._tem.load_alignments_from_file(file_name)

    def load_alignments_from_file_path(self, folder_path: str, file_name: str) -> bool:
        """
        Load Optics alignments from the given file in the given folder.
        :param folder_path: the path where the .alg file is located
        :param file_name: name of the .alg file
        :return True if operation was executed, False if it is not supported
        """
        return self._tem.load_alignments_from_file_custom_path(folder_path, file_name)

    def save_alignments_to_registry(self) -> None:
        """ Save the optics alignments from memory to registry.
        """
        self._tem.save_alignments_to_registry()

    def get_intensity_list(self):
        """ Get the current active value in intensity list (Intensity in optics model).
        (non-physical units)

        :return: float the current value in the intensity list
        """
        return self._tem.get_intensity_list()

    def set_intensity_list(self, value):
        """ Set the current active value in intensity list(Intensity in optics model).
        (non-physical units)

        :param value: the current value in the intensity list to set
        """
        self._tem.set_intensity_list(value)

    def get_intensity_preset(self):
        """ Get the intensity preset (IntPreset in optics model). Only supported on Metrios.
        (non-physical units)

        :return: float intensity preset
        """
        return self._tem.get_intensity_preset()

    def set_intensity_preset(self, value):
        """ Set the intensity preset (IntPreset in optics model). Only supported on Metrios.
        (non-physical units)

        :param value: intensity preset to set
        """
        self._tem.set_intensity_preset(value)

    def get_image_shift_to_beam_shift_conversion_matrix(self):
        """ Get image shift to beam shift conversion matrix. (non-physical units)

        :return: matrix 2x3 of floats
        """
        return self._tem.get_image_shift_to_beam_shift_conversion_matrix()

    def set_image_shift_to_beam_shift_conversion_matrix(self, matrix):
        """ Set image shift to beam shift conversion matrix. (non-physical units)

        :param matrix: matrix 2x3 of floats to set
        """
        self._tem.set_image_shift_to_beam_shift_conversion_matrix(matrix)

    def get_condenser_calibration(self):
        """ Get Condenser calibration.
        Applicable for 3 condenser system. Not supported for Two condenser System.

        :return: float condenser calibration
        """
        return self._tem.get_condenser_calibration()

    def get_condenser_calibration_for_mode(self, objective_mode, probe_mode, illumination_mode):
        """ Get Condenser calibration for given mode.
        CondenserCalibration is a calibration factor for illuminated area in
        parallel illumination  mode and for probe convergence angle in probe illumination mode.
        Applicable for 3 condenser system.
        Supported modes: LM-Microprobe-Parallel, HM-Microprobe-Parallel, HM-Nanoprobe-Parallel

        :param objective_mode: enum fei_common.infra.tem_service.api.ObjectiveMode
        :param probe_mode: enum fei_common.infra.tem_service.api.ProbeMode
        :param illumination_mode: enum fei_common.infra.tem_service.api.IlluminationMode.
        :return: float condenser calibration for given mode
        """
        return self._tem.get_condenser_calibration_for_mode(objective_mode, probe_mode,
                                                            illumination_mode)

    def get_gun_crossover(self):
        """ Get the gun crossover in meters using sample as reference height
        (GunXO in optics model).
        Not supported for Two condenser systems.

        :return: float gun crossover in meters
        """
        return self._tem.get_gun_crossover()

    def set_gun_crossover(self, value):
        """ Set the gun crossover in meters using sample as reference height
        (GunXO in optics model).
        Not supported for Two condenser systems.

        :param value: float gun crossover to set in meters
        """
        self._tem.set_gun_crossover(value)

    def get_focus_correction(self):
        """ Get the (magnification/camera length) dependent focus correction
        (FocusCorr in optics model).

        :return: float focus correction
        """
        return self._tem.get_focus_correction()

    def set_focus_correction(self, value):
        """ Set the (magnification/camera length) dependent focus correction
        (FocusCorr in optics model).

        :param value: float focus correction to set
        """
        self._tem.set_focus_correction(value)

    def get_spotsize_dependent_stem_intensity_preset(self):
        """ Get the spot size dependent intensity correction in Stem mode (non-physical units)
        (combination of IntensList (spotsize <= 11)
        and MonoIntensList (spotsize > 11) in optics model).
        Allowed only in STEM.

        :return: float intensity preset
        """
        return self._tem.get_spotsize_dependent_stem_intensity_preset()

    def set_spotsize_dependent_stem_intensity_preset(self, value):
        """ Set the spot size dependent intensity correction in Stem mode (non-physical units)
        (combination of IntensList (spotsize <= 11)
        and MonoIntensList (spotsize > 11) in optics model).
        Allowed only in STEM.

        :param value: float intensity preset to set
        """
        self._tem.set_spotsize_dependent_stem_intensity_preset(value)

    def get_distortion(self):
        """ Get the average distortion value in image or diffraction pattern for all magnifications.

        :return: X and Y, tuple of floats
        """
        return self._tem.get_distortion()

    def set_distortion(self, x, y=None):
        """ Set the average distortion value in image or diffraction pattern for all magnifications.

        :param x distortion X value or a tuple of X and Y values (floats)
        :param y distortion Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_distortion, x, y)

    def get_distortion_correction(self):
        """ Get distortion correction value for the current magnification.

        :return: X and Y, tuple of floats
        """
        return self._tem.get_distortion_correction()

    def set_distortion_correction(self, x, y=None):
        """ Set distortion correction value for the current magnification.

        :param x: x distortion correction X value or a tuple of X and Y values (floats)
        :param y: y distortion correction Y value or None if x is a tuple
        """
        self._perform_tuple_function(self._tem.set_distortion_correction, x, y)

    def get_distortion_correction_collection(self):
        """ Get distortion correction values for all magnifications for current mode.

        :return: dictionary of tuples
        """
        return self._tem.get_distortion_correction_collection()

    def get_stig_to_stig(self):
        """ Get transformation matrix for transforming distortion to stigmator.
        (non-physical units)

        :return: matrix 2x3 of floats
        """
        return self._tem.get_stig_to_stig()

    def set_stig_to_stig(self, matrix):
        """ Set transformation matrix for transforming distortion to stigmator.
        (non-physical units)

        :param matrix: transformation matrix 2x3 of floats to set
        """
        self._tem.set_stig_to_stig(matrix)

    def get_current_coarse_attenuator_switch_index(self):
        """ Get Current Coarse Attenuator Switch state.

        :return: int switch state
        """
        return self._tem.get_current_coarse_attenuator_switch_index()

    def get_minimum_coarse_attenuator_switch_index(self):
        """ Get Minimum Coarse Attenuator Switch state.

        :return: int switch state
        """
        return self._tem.get_minimum_coarse_attenuator_switch_index()

    def get_maximum_coarse_attenuator_switch_index(self):
        """ Get Maximum Coarse Attenuator Switch state

        :return: int switch state
        """
        return self._tem.get_maximum_coarse_attenuator_switch_index()

    def get_ac_deflector_correction_value(self, switch_index, ac_deflector):
        """ Get Correction Value for specified Ac deflector hardware for current mode.

        :param switch_index: switch state
        :param ac_deflector: enum fei_common.infra.tem_service.api.AcDeflector
        :return: float correction value
        """
        return self._tem.get_ac_deflector_correction_value(switch_index, ac_deflector)

    def set_ac_deflector_correction_value(self, switch_index, ac_deflector, value):
        """ Set Correction Value for specified Ac deflector hardware.

        :param switch_index: switch state
        :param ac_deflector: enum fei_common.infra.tem_service.api.AcDeflector
        :param value: float correction value to set
        """
        self._tem.set_ac_deflector_correction_value(switch_index, ac_deflector, value)

    def _perform_tuple_function(self, function, x, y):
        if y is None and isinstance(x, Iterable) and len(x) == 2:
            function(*x)
        else:
            function(x, y)

    def get_zoom_mode(self):
        """ Returns whether zoom mode is active or not

        :return: True: zoom active, otherwise false
        """
        return self._tem.get_zoom_mode()

    def set_zoom_mode(self, zoom_mode_active):
        """ Set auto zoom on or off

        :param zoom_mode_active: True is on, False is off
        """
        self._tem.set_zoom_mode(zoom_mode_active)

    def get_focus_preset(self):
        """ Get the focus preset (Preset in optics model).
        Supported in TEM6.12. An OMP exception is raised for versions below 6.12

        :return: float focus preset in optical units
        """
        return self._tem.get_focus_preset()

    def set_focus_preset(self, value):
        """ Set the focus preset (Preset in optics model, this is a
        lens offset to obtain focus at eucentric height)
        Supported in TEM6.12. An OMP exception is raised for versions below 6.12

        :param value: float, focus preset to set (optical units, range depends
                      on optics state)
        """
        self._tem.set_focus_preset(value)

    def init_intensity_zoom(self):
        """ Init Intensity Zoom functionality.
        """
        self._tem.init_intensity_zoom()

    def is_init_intensity_zoom_supported(self):
        """ Check if init_intensity_zoom is supported for current TEM server version.
        (supported from TEM 7.2)
        :return: (bool) True if supported, False otherwise
        """
        return self._tem.is_init_intensity_zoom_supported()

    def clear_focus_correction_list(self):
        """ Clear Focus Correction list.
        """
        self._tem.clear_focus_correction_list()

    def is_clear_focus_correction_list_supported(self):
        """ Check if clear_focus_correction_list is supported for current TEM server version.
        (supported from TEM 7.2)
        :return: (bool) True if supported, False otherwise
        """
        return self._tem.is_clear_focus_correction_list_supported()

    def set_all_intensity_list(self, intensity_list):
        """ Set all intensity list values - 11 values (non-physical units, between -1 and +1).

        :param intensity_list: (list of float) intensity values to set
        """
        self._tem.set_all_intensity_list(intensity_list)

    def is_set_all_intensity_list_supported(self):
        """ Check if set_all_intensity_list is supported for current TEM server version.
        (supported from TEM 7.2)
        :return: (bool) True if supported, False otherwise
        """
        return self._tem.is_set_all_intensity_list_supported()

    def set_all_mono_intensity_list(self, mono_intensity_list):
        """ Set all Mono intensity list values - 6 values (non-physical units, between -1 and +1)

        :param mono_intensity_list: (list of float) intensity values to set
        """
        self._tem.set_all_mono_intensity_list(mono_intensity_list)

    def is_set_all_mono_intensity_list_supported(self):
        """ Check if set_all_mono_intensity_list is supported for current TEM server version.
        (supported from TEM 7.2)
        :return: (bool) True if supported, False otherwise
        """
        return self._tem.is_set_all_mono_intensity_list_supported()

    def get_full_scan_field_of_view_range(self, column_mode):
        """ Get the STEM full-scan field of view range( minim and maxim) and boolean value for
            isCalibrated.
            First fei_common.infra.tem_service.api.FieldOfView represents the minimum values
            that x and y could take.
            Second fei_common.infra.tem_service.api.FieldOfView represents the maximum values
            that x and y could take.
            The boolean will tell if the field of view was calibrated or not.

        :param: column_mode: (fei_common.infra.tem_service.api.ColumnMode)
        :return: Tuple of 2 fei_common.infra.tem_service.api.FieldOfView and a boolean
        """
        return self._tem.get_full_scan_field_of_view_range(column_mode)

    def set_full_scan_field_of_view(self, fov):
        """ Set the STEM full-scan field of view.
            Accepts the following types: Tuple of 2 floats,list of 2 floats or
            fei_common.infra.tem_service.api.FieldOfView
            Values out of range will be coerced to the nearest value supported.

        :param fov: fei_common.infra.tem_service.api.FieldOfView
        """
        return self._tem.set_full_scan_field_of_view(fov)

    def is_alignments_custom_path_supported(self) -> bool:
        """
        Returns whether saving and loading optical alignments from the custom path is supported
        :return: True if save + load from custom path is supported
        """
        return self._tem.is_alignments_custom_path_supported()

    def subscribe_column_mode_changed(self, handler: Callable[[ColumnMode], None]) -> Subscription:
        """
        Subscribe to ColumnModeChanged events.
        :param handler: event handler
        :return: Subcription object (unmanaged C++). It is crucial to call Subcription.unsubscribe()
         when the subcription is no longer needed.
        """
        return self._tem.subscribe_column_mode_changed(handler)

    def is_beam_current_calibrations_supported(self) -> bool:
        """
        Returns whether retrieving and writing beam current calibrations is supported
        :return: True if TEM server contains IOpticsAlignments6 interface and version is at
        least 7.11.
        """
        return self._tem.is_beam_current_calibrations_supported()

    def get_available_beam_current_calibrations(self):
        """
        Get the available beam current calibrations
        :return: [BeamCurrentCalibrations]
        """
        omp_available_beam_current_calibrations = (
            self._tem.get_available_beam_current_calibrations())
        available_beam_current_calibrations = []
        for omp_beam_current_calibration_data in omp_available_beam_current_calibrations:
            # convert omp_beam_current_calibration_data to Python object.
            available_beam_current_calibrations.append(
                BeamCurrentCalibrationData.from_omp(omp_beam_current_calibration_data))
        return available_beam_current_calibrations

    def set_beam_current_calibrations_reference_beam_current(self, value):
        """
        Set the reference beam current, which results in the creation of a beam current calibration.
        """
        self._tem.set_beam_current_calibrations_reference_beam_current(value)

    def remove_beam_current_calibration(
            self,
            calibration: BeamCurrentCalibrationData):
        """
        Removes beam current calibration.
        """

        # access omp_reference field of class instance
        self._tem.remove_beam_current_calibration(calibration.omp_reference)

    def is_gun_lens_dependent_tilt_correction_supported(self):
        return self._tem.is_gun_lens_dependent_tilt_correction_supported()

    def reset_all_gun_lens_dependent_tilt_corrections(self):
        self._tem.reset_all_gun_lens_dependent_tilt_corrections()

    def get_gun_lens_dependent_gun_tilt_correction(self):
        return self._tem.get_gun_lens_dependent_gun_tilt_correction()

    def set_gun_lens_dependent_gun_tilt_correction(self, x, y=None):
        self._perform_tuple_function(self._tem.set_gun_lens_dependent_gun_tilt_correction, x, y)

    def is_gun_lens_dependent_shift_correction_supported(self):
        return self._tem.is_gun_lens_dependent_tilt_correction_supported()

    def reset_all_gun_lens_dependent_shift_corrections(self):
        self._tem.reset_all_gun_lens_dependent_shift_corrections()

    def get_gun_lens_dependent_gun_shift_correction(self):
        return self._tem.get_gun_lens_dependent_gun_shift_correction()

    def set_gun_lens_dependent_gun_shift_correction(self, x, y=None):
        self._perform_tuple_function(self._tem.set_gun_lens_dependent_gun_shift_correction, x, y)

    def is_gun_lens_dependent_gun_crossover_offset_supported(self):
        return self._tem.is_gun_lens_dependent_gun_crossover_offset_supported()

    def reset_all_gun_lens_dependent_gun_crossover_offsets(self):
        self._tem.reset_all_gun_lens_dependent_gun_crossover_offsets()

    def get_gun_lens_dependent_gun_crossover_offset(self):
        return self._tem.get_gun_lens_dependent_gun_crossover_offset()

    def set_gun_lens_dependent_gun_crossover_offset(self, offset):
        self._tem.set_gun_lens_dependent_gun_crossover_offset(offset)

    def is_gun_lens_dependent_gun_stigmator_correction_supported(self):
        return self._tem.is_gun_lens_dependent_gun_stigmator_correction_supported()

    def reset_gun_lens_dependent_gun_stigmator_corrections(self):
        self._tem.reset_gun_lens_dependent_gun_stigmator_corrections()

    def get_gun_lens_dependent_gun_stigmator_correction(self):
        return self._tem.get_gun_lens_dependent_gun_stigmator_correction()

    def set_gun_lens_dependent_gun_stigmator_correction(self, x, y=None):
        self._perform_tuple_function(
            self._tem.set_gun_lens_dependent_gun_stigmator_correction, x, y)
