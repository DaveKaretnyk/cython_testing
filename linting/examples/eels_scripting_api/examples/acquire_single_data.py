# Copyright (c) 2012-2021 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.


from tfs_eels.scripting_api.eels_min_scripting import EelsMinScripting


if __name__ == '__main__':
    eels_min_script = None
    try:
        eels_min_script = EelsMinScripting(log_to_console=False, log_to_file=True,
                                           log_file_name=r'c:\temp\eels_min_scripting_test')

        np_data, meta_data = eels_min_script.acquire_single_data(
            exposure_time=0.4, target_sensor=0, prepare_system=True)

        print("Received data with shape {}".format(np_data.shape))
    finally:
        if eels_min_script is not None:
            eels_min_script.release()
