import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_session
from repositories_auth import authenticate_user, create_user
from schemas_auth import LoginRequest, SignupRequest, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/auth/signup", response_model=UserResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_session)) -> UserResponse:
    try:
        user = create_user(
            db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            organization=payload.organization,
        )
        return UserResponse.model_validate(user, from_attributes=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error during signup", exc_info=exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("/auth/login", response_model=UserResponse)
def login(payload: LoginRequest, db: Session = Depends(get_session)) -> UserResponse:
    user = authenticate_user(db, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserResponse.model_validate(user, from_attributes=True)
