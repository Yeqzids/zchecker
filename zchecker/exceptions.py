# Licensed under a 3-clause BSD style license - see LICENSE.rst
class ZCheckerError(Exception):
    pass

class DownloadError(ZCheckerError):
    pass

class DateRangeError(ZCheckerError):
    pass

class EphemerisError(ZCheckerError):
    pass
