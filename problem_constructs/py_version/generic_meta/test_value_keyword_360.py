#  Copyright (c) 2020 by Thermo Fisher Scientific
#  All rights reserved. This file includes confidential and proprietary information
#  of Thermo Fisher Scientific
import pytest

from .value_keyword_360 import (
    FringeFreeIlluminationKeyWord, GunLensKeyWord, ImageCorrectorKeyWord, ProbeCorrectorKeyWord,
    MagnificationIndexKeyWord, SpotSizeKeyWord, MagnificationKeyWord, MicroscopeTypeKeyWord,
    ValueKeyWord)


class TestValueKeyWord:
    def test_abstract_base_class(self):
        with pytest.raises(TypeError):
            ValueKeyWord(9)

    @pytest.mark.parametrize("first, second", [
        (FringeFreeIlluminationKeyWord(True), FringeFreeIlluminationKeyWord(True)),
        (FringeFreeIlluminationKeyWord(False), FringeFreeIlluminationKeyWord(False)),
        (GunLensKeyWord(0), GunLensKeyWord(0)),
        (MagnificationIndexKeyWord(5), MagnificationIndexKeyWord(5)),
        (SpotSizeKeyWord(3), SpotSizeKeyWord(3)),
    ])
    def test_equals(self, first, second):
        assert first == second

    @pytest.mark.parametrize("first, second", [
        (FringeFreeIlluminationKeyWord(True), FringeFreeIlluminationKeyWord(False)),
        (FringeFreeIlluminationKeyWord(False), FringeFreeIlluminationKeyWord(True)),

        (GunLensKeyWord(0), GunLensKeyWord(9)),
        (GunLensKeyWord(0), MagnificationIndexKeyWord(0)),
        (GunLensKeyWord(0), SpotSizeKeyWord(0)),

        (MagnificationIndexKeyWord(5), MagnificationIndexKeyWord(6)),
        (MagnificationIndexKeyWord(5), GunLensKeyWord(5)),
        (MagnificationIndexKeyWord(5), SpotSizeKeyWord(5)),

        (SpotSizeKeyWord(3), SpotSizeKeyWord(5)),
        (SpotSizeKeyWord(3), GunLensKeyWord(3)),
        (SpotSizeKeyWord(3), MagnificationIndexKeyWord(3)),
    ])
    def test_not_equals(self, first, second):
        assert first != second

    @pytest.mark.parametrize("class_, length", [
        (FringeFreeIlluminationKeyWord, 2),
        (GunLensKeyWord, 8),
        (SpotSizeKeyWord, 11),
        (MagnificationIndexKeyWord, 16),
    ])
    def test_type_length(self, class_, length):
        assert length == len(class_)

    @pytest.mark.parametrize("json_string, structure, expected_result", [
        ("True", FringeFreeIlluminationKeyWord, FringeFreeIlluminationKeyWord(True)),
        ("2.5", GunLensKeyWord, GunLensKeyWord(2.5)),
        ("True", ImageCorrectorKeyWord, ImageCorrectorKeyWord(True)),
        ("True", ProbeCorrectorKeyWord, ProbeCorrectorKeyWord(True)),
        ("1", SpotSizeKeyWord, SpotSizeKeyWord(1)),
        ("1", MagnificationIndexKeyWord, MagnificationIndexKeyWord(1)),
        ("1.2", MagnificationKeyWord, MagnificationKeyWord(1.2)),
        ("MicroscopeType", MicroscopeTypeKeyWord, MicroscopeTypeKeyWord("MicroscopeType")),
    ])
    def test_json_decode(self, json_string, structure, expected_result):
        assert structure.json_decode(json_string, dict()) == expected_result

    def test_json_encode(self):
        assert SpotSizeKeyWord(5).json_encode() == "SpotSizeKeyWord::5"

    @pytest.mark.parametrize("fringe_free_illumination, exepected_result", [
        (True, "FringeFreeIlluminationKeyWord::True"),
        (False, "FringeFreeIlluminationKeyWord::False")])
    def test_fringe_free_illumination_json_encode(self, fringe_free_illumination, exepected_result):
        assert (exepected_result
                == FringeFreeIlluminationKeyWord(fringe_free_illumination).json_encode())
