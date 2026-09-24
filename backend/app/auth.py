from fastapi import Header, HTTPException, status


def current_user_id(x_user_id: str | None = Header(default=None)) -> str:
    """Require an authenticated workspace identity for every document operation."""
    if not x_user_id or len(x_user_id) > 128 or any(char.isspace() for char in x_user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return x_user_id
