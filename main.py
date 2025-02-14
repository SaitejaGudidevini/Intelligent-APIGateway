from fastapi import FastAPI, Request, Depends, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from loguru import logger
import time
from sqlalchemy.orm import Session
from app.core.security import (
    create_access_token, Token, verify_password, 
    ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
)
from app.core.database import SessionLocal
from app.core.auth import (
    authenticate_user, get_user_by_email,
    create_new_user, get_user_by_username
)
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from datetime import timedelta
from typing import Optional

# Authentication scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scheme_name="Bearer Authentication",
    description="Enter your Bearer token in the format: Bearer <token>"
)

# Create FastAPI instance
app = FastAPI(
    title="Intelligent API Gateway",
    description="""
    A secure and scalable API Gateway for microservices.
    
    ## Authentication
    1. First get your token by using the /token endpoint with your credentials
    2. Click the 'Authorize' button at the top right
    3. In the value field enter: Bearer <your_token>
    4. Click Authorize
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Operations for authentication and user management"
        },
        {
            "name": "system",
            "description": "System health and status endpoints"
        }
    ]
)

# Create test user on startup
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        test_user = get_user_by_email(db, "test@example.com")
        if not test_user:
            test_user = UserCreate(
                email="test@example.com",
                username="testuser",
                password="testpass123"
            )
            create_new_user(db=db, user=test_user)
            logger.info("Created test user: test@example.com / testpass123")
    finally:
        db.close()

# Database dependency
def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React development server
        "http://localhost:8000",  # FastAPI server
        # Add your production domains here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Duration: {duration:.2f}s Status: {response.status_code}"
    )
    return response

# Authentication endpoints
@app.post("/token", response_model=Token, tags=["authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=UserSchema, tags=["authentication"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_new_user(db=db, user=user)

# Get current user helper
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Protected user info endpoint
@app.get("/users/me", response_model=UserSchema, tags=["authentication"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Protected health check endpoint
@app.get("/health", dependencies=[Depends(oauth2_scheme)], tags=["system"])
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
