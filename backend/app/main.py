from fastapi import FastAPI
from app.models import UserRole  
from fastapi import FastAPI
from app.models import UserRole
from app.routes.user_auth import router as auth_router
from app.routes.documents import router as document_router
from app.database import Base, engine
from app.models import User

app = FastAPI(
    title="Enterprise Policy Assistant",
    description="AI-powered enterprise policy question answering system",
    version="1.0.0"
)


Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(document_router)

@app.get("/")
def root():
    return {
        "message": "Enterprise Policy Assistant API is running"
    }

@app.get("/roles")

def get_roles():

    return {

        "roles": [role.value for role in UserRole]

    }