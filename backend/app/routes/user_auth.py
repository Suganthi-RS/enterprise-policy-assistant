from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserLogin
from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models import User, UserRole
from app.dependencies import get_current_user, require_role, require_role

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.get("/health")
def auth_health():
    return {
        "message": "Authentication routes are working"
    }

@router.post("/register")
def register_user(

    user: UserCreate,

    db: Session = Depends(get_db)

):

    password_hash = hash_password(user.password)

    new_user = User(

        name=user.name,

        email=user.email,

        password_hash=password_hash,

        role=user.role

    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return {

        "message": "User registered successfully",

        "id": new_user.id,

        "name": new_user.name,

        "email": new_user.email,

        "role": new_user.role.value

    }

@router.post("/login")
def login_user(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": str(existing_user.id),
            "email": existing_user.email,
            "role": existing_user.role.value
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role.value
    }



@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_role(UserRole.ADMIN)
    )
):
    return {
        "message": "Admin access successful",
        "user": current_user.email
    }


@router.get("/user-test")
def user_test(
    current_user: User = Depends(
        require_role(UserRole.USER)
    )
):
    return {
        "message": "User access successful",
        "user": current_user.email
    }