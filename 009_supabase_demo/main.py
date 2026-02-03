import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from starlette.responses import JSONResponse
from supabase import create_client, Client
from storage3.exceptions import StorageApiError
from fastapi.responses import Response

from db_types import (
    PublicInstruments,
    PublicInstrumentsInsert,
    PublicInstrumentsUpdate,
    PublicUserProfiles,
)

load_dotenv()

app = FastAPI()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Pydantic models for auth
class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: str
    email: str
    avatar: str | None = None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Validate token and return current user from Supabase."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Use Supabase's get_user method with the access token
        user_response = supabase.auth.get_user(token)
        if user_response is None or user_response.user is None:
            raise credentials_exception
        return user_response.user
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception


UserDep = Annotated[dict | None, Depends(get_current_user)]


@app.post("/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """OAuth2 compatible token login with Supabase."""
    user_response = supabase.auth.sign_in_with_password(
        {"email": form_data.username, "password": form_data.password}
    )

    if user_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return the access token from Supabase session
    return {"access_token": user_response.session.access_token, "token_type": "bearer"}


@app.post("/auth/signup", response_model=UserResponse)
async def signup(email: str, password: str):
    """Register a new user."""
    response = supabase.auth.sign_up({"email": email, "password": password})
    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
        )
    return {"id": response.user.id, "email": response.user.email}


@app.post("/auth/logout")
async def logout(current_user: UserDep):
    """Log out the current user."""
    supabase.auth.sign_out()
    return {"message": "Successfully logged out"}


@app.get("/instruments", response_model=list[PublicInstruments])
async def list_instruments(current_user: UserDep):
    """List all instruments (authenticated)."""
    response = supabase.table("instruments").select("*").execute()
    return [PublicInstruments.model_validate(item) for item in response.data]


@app.post("/instruments", response_model=PublicInstruments, status_code=201)
async def add_instrument(instrument: PublicInstrumentsInsert, current_user: UserDep):
    """Add a new instrument (authenticated)."""
    response = (
        supabase.table("instruments")
        .insert(instrument.model_dump(by_alias=True))
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to insert instrument")
    return PublicInstruments.model_validate(response.data[0])


@app.delete("/instruments/{instrument_id}", status_code=204)
async def delete_instrument(instrument_id: int, current_user: UserDep):
    """Delete an instrument by ID (authenticated)."""
    response = supabase.table("instruments").delete().eq("id", instrument_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return None


@app.put("/instruments/{instrument_id}", response_model=PublicInstruments)
async def update_instrument(
    instrument_id: int, instrument: PublicInstrumentsUpdate, current_user: UserDep
):
    """Update an instrument by ID (authenticated)."""
    update_data = instrument.model_dump(by_alias=True, exclude_unset=True)
    response = (
        supabase.table("instruments")
        .update(update_data)
        .eq("id", instrument_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return PublicInstruments.model_validate(response.data[0])


@app.get("/avatars/{user_id}")
async def read_avatar(user_id: str):
    """Get a user's avatar file from avatars bucket by user_id."""
    avatar_path = f"{user_id}.png"

    try:
        # Download the file from Supabase Storage
        file_response = supabase.storage.from_("avatars").download(avatar_path)

        if file_response is None:
            raise HTTPException(status_code=404, detail="Avatar not found")

        # Return the file with appropriate content type
        return Response(
            content=file_response,
            media_type="image/png",  # Adjust based on your image type or detect it
        )
    except StorageApiError as e:
        raise HTTPException(status_code=400, detail=f"Storage error: {str(e)}")


@app.get("/users/me/avatar")
async def read_user_avatar(current_user: UserDep):
    """Get current user's avatar file from avatars bucket."""
    avatar_path = f"{current_user.id}.png"

    try:
        # Download the file from Supabase Storage
        file_response = supabase.storage.from_("avatars").download(avatar_path)

        # Return the file with appropriate content type
        return Response(
            content=file_response,
            media_type="image/png",  # Adjust based on your image type or detect it
        )
    except StorageApiError as e:
        raise HTTPException(status_code=400, detail=f"Storage error: {str(e)}")


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserDep):
    """Get current user info."""
    return {"id": current_user.id, "email": current_user.email, "avatar": avatar}


@app.get("/users/hello")
async def hello_me(current_user: UserDep):
    """Get current user info."""
    response = supabase.functions.invoke(
        "hello-world",
        invoke_options={"responseType": "json", "body": {"name": f"{current_user.id}"}}
    )
    return response



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
