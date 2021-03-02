from .form460 import FORM_460
from .form461 import FORM_461
from .form700 import FORM_700
from .form803 import FORM_803

# ... etc ...


FORMS = [
    FORM_460,
    FORM_461,
    FORM_700,
    FORM_803,
]

FORM_TYPES = {f.get("name"): f.get("title") for f in FORMS}

FORM_TYPE_IDS = FORM_TYPES.keys()
