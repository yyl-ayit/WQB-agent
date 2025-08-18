"""
A better machine lib.

PyPI: https://pypi.org/project/wqb/
GitHub: https://github.com/rocky-d/wqb
"""

__version__ = '0.2.5'


from typing import Any

GET = 'GET'
POST = 'POST'
PUT = 'PUT'
PATCH = 'PATCH'
DELETE = 'DELETE'
HEAD = 'HEAD'
OPTIONS = 'OPTIONS'

LOCATION = 'Location'
RETRY_AFTER = 'Retry-After'

EQUITY = 'EQUITY'

Alpha = Any
MultiAlpha = Any

Region = Any
Delay = Any
Universe = Any
InstrumentType = Any
DataCategory = Any
FieldType = Any
DatasetsOrder = Any
FieldsOrder = Any
Status = Any
AlphaType = Any
AlphaCategory = Any
Language = Any
Color = Any
Neutralization = Any
UnitHandling = Any
NanHandling = Any
Pasteurization = Any
AlphasOrder = Any


class Null:
    pass


NULL = Null()


from . import auto_auth_session
from . import datetime_range
from . import filter_range
from . import wqb_session
from . import wqb_urls

__all__ = (
    auto_auth_session.__all__
    + datetime_range.__all__
    + filter_range.__all__
    + wqb_session.__all__
    + wqb_urls.__all__
)


from .auto_auth_session import *
from .datetime_range import *
from .filter_range import *
from .wqb_session import *
from .wqb_urls import *
