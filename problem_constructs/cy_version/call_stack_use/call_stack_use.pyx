import inspect


EXPECTED_MODULE_NAME = 'start_auto_sim_control'


def is_auto_sim_control_app():
    """ Is this code running in the AutoStar simulation control application.

    Done by walking the stack frame. Assumption is that application can be
    determined via the module name of the application, see constant
    EXPECTED_MODULE_NAME.

    :return boolean
    """
    is_auto_sim_app = False
    for frame in inspect.stack():
        try:
            frame_info = inspect.getframeinfo(frame[0])
            print(f">>>frame_info: {frame_info[2]}")
            if EXPECTED_MODULE_NAME in frame_info.filename:
                is_auto_sim_app = True
                break
        finally:
            # See inspect module docs, this eliminates possible reference counting issues.
            del frame

    return is_auto_sim_app


def get_aaa(aaa):
    result = aaa
    if is_auto_sim_control_app():
        aaa *= 100
    return result


def get_aa(aa):
    return get_aaa(aa)


def get_a(a):
    return get_aa(a)
