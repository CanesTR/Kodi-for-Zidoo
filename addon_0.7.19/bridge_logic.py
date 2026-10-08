"""Pure validation and update policy for the native player's final result."""
import math


def checked_resume(pending, result):
    if result.get('schema') != 1 or result.get('helper_version') not in ('0.2.0', '0.2.1', '0.2.2', '0.2.3', '0.2.4', '0.2.5', '0.2.6', '0.2.7'):
        raise ValueError('Unsupported helper result')
    if result.get('session') != pending['session']:
        raise ValueError('Result belongs to a different playback session')
    if result.get('path') != pending['path'] or result.get('returned_path') != pending['path']:
        raise ValueError('Native result does not match the selected movie path')
    if result.get('status') != 'completed' or result.get('result_code') != -1:
        raise ValueError(result.get('error', 'Native player did not return a successful result'))
    if not result.get('end_by'):
        raise ValueError('Native result has no end reason')
    position, total = result.get('position_ms'), result.get('duration_ms')
    if type(position) is not int or type(total) is not int or not 0 <= position <= total or total <= 0:
        raise ValueError('Invalid native position/duration')
    if not all(math.isfinite(x / 1000.0) for x in (position, total)):
        raise ValueError('Non-finite playback time')
    # Automatic marking uses final position, including seeking, not elapsed viewing time.
    watched = position / total >= 0.95
    return {'position': 0.0 if watched else position / 1000.0,
            'total': 0.0 if watched or position == 0 else total / 1000.0}, watched
