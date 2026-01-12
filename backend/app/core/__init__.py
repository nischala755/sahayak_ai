# Core module exports
from app.core.config import settings, get_settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    require_role
)
