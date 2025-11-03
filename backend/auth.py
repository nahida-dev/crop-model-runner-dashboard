from fastapi import Header, HTTPException

def get_current_user(x_user_id: str | None = Header(default=None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Unauthorized: missing x-user-id")
    return x_user_id
