from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum
import pandas as pd
import io

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Configuration
JWT_SECRET = "laboratory_inventory_secret_key_2025"
JWT_ALGORITHM = "HS256"
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_number: str
    password_hash: str
    role: UserRole
    full_name: str
    email: str
    section: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    employee_number: str
    password: str
    role: UserRole
    full_name: str
    email: str
    section: str

class UserLogin(BaseModel):
    employee_number: str
    password: str

class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_name: str
    category: str
    sub_category: Optional[str] = None
    location: str
    manufacturer: str
    supplier: str
    model: str
    uom: str  # Unit of Measurement
    catalogue_no: str
    quantity: int
    target_stock_level: int
    reorder_level: int
    validity: Optional[datetime] = None
    use_case: str
    added_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class InventoryItemCreate(BaseModel):
    item_name: str
    category: str
    sub_category: Optional[str] = None
    location: str
    manufacturer: str
    supplier: str
    model: str
    uom: str
    catalogue_no: str
    quantity: int
    target_stock_level: int
    reorder_level: int
    validity: Optional[datetime] = None
    use_case: str

class WithdrawalRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str
    item_name: str
    requested_quantity: int
    purpose: str
    requested_by: str
    requested_by_name: str
    status: RequestStatus = RequestStatus.PENDING
    admin_comments: Optional[str] = None
    processed_by: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WithdrawalRequestCreate(BaseModel):
    item_id: str
    requested_quantity: int
    purpose: str

class WithdrawalRequestProcess(BaseModel):
    request_id: str
    action: str  # "approve" or "reject"
    comments: Optional[str] = None

class EmailConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    is_active: bool = True
    added_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmailConfigCreate(BaseModel):
    email: str

# Authentication Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Initialize admin user
async def create_default_admin():
    admin_exists = await db.users.find_one({"employee_number": "ADMIN001"})
    if not admin_exists:
        admin_user = User(
            employee_number="ADMIN001",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            full_name="System Administrator",
            email="admin@company.com",
            section="IT Administration"
        )
        await db.users.insert_one(admin_user.dict())
        print("Default admin user created - Employee Number: ADMIN001, Password: admin123")

# Routes
@api_router.post("/register")
async def register_user(user_data: UserCreate, admin: User = Depends(get_admin_user)):
    existing_user = await db.users.find_one({"employee_number": user_data.employee_number})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee number already registered"
        )
    
    user = User(
        employee_number=user_data.employee_number,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        full_name=user_data.full_name,
        email=user_data.email,
        section=user_data.section
    )
    
    await db.users.insert_one(user.dict())
    return {"message": "User registered successfully"}

@api_router.post("/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"employee_number": login_data.employee_number})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee number or password"
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "employee_number": user["employee_number"],
            "full_name": user["full_name"],
            "role": user["role"],
            "section": user["section"]
        }
    }

@api_router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "employee_number": current_user.employee_number,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "email": current_user.email,
        "section": current_user.section
    }

# Inventory Management Routes
@api_router.post("/inventory", response_model=InventoryItem)
async def add_inventory_item(item_data: InventoryItemCreate, admin: User = Depends(get_admin_user)):
    item = InventoryItem(**item_data.dict(), added_by=admin.employee_number)
    await db.inventory.insert_one(item.dict())
    return item

@api_router.get("/inventory", response_model=List[InventoryItem])
async def get_inventory(current_user: User = Depends(get_current_user)):
    items = await db.inventory.find().to_list(1000)
    return [InventoryItem(**item) for item in items]

@api_router.get("/inventory/{item_id}", response_model=InventoryItem)
async def get_inventory_item(item_id: str, current_user: User = Depends(get_current_user)):
    item = await db.inventory.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return InventoryItem(**item)

@api_router.put("/inventory/{item_id}")
async def update_inventory_item(item_id: str, item_data: InventoryItemCreate, admin: User = Depends(get_admin_user)):
    update_data = item_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.inventory.update_one(
        {"id": item_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return {"message": "Item updated successfully"}

@api_router.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str, admin: User = Depends(get_admin_user)):
    result = await db.inventory.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# Withdrawal Request Routes
@api_router.post("/withdrawal-requests", response_model=WithdrawalRequest)
async def create_withdrawal_request(request_data: WithdrawalRequestCreate, current_user: User = Depends(get_current_user)):
    # Check if item exists and has sufficient quantity
    item = await db.inventory.find_one({"id": request_data.item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["quantity"] < request_data.requested_quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient stock. Available: {item['quantity']}, Requested: {request_data.requested_quantity}"
        )
    
    withdrawal_request = WithdrawalRequest(
        **request_data.dict(),
        item_name=item["item_name"],
        requested_by=current_user.id,
        requested_by_name=current_user.full_name
    )
    
    await db.withdrawal_requests.insert_one(withdrawal_request.dict())
    return withdrawal_request

@api_router.get("/withdrawal-requests", response_model=List[WithdrawalRequest])
async def get_withdrawal_requests(current_user: User = Depends(get_current_user)):
    if current_user.role == UserRole.ADMIN:
        requests = await db.withdrawal_requests.find().to_list(1000)
    else:
        requests = await db.withdrawal_requests.find({"requested_by": current_user.id}).to_list(1000)
    
    return [WithdrawalRequest(**request) for request in requests]

@api_router.post("/withdrawal-requests/process")
async def process_withdrawal_request(process_data: WithdrawalRequestProcess, admin: User = Depends(get_admin_user)):
    request = await db.withdrawal_requests.find_one({"id": process_data.request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request["status"] != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    update_data = {
        "status": RequestStatus.APPROVED if process_data.action == "approve" else RequestStatus.REJECTED,
        "admin_comments": process_data.comments,
        "processed_by": admin.employee_number,
        "processed_at": datetime.utcnow()
    }
    
    # If approved, reduce inventory quantity
    if process_data.action == "approve":
        item = await db.inventory.find_one({"id": request["item_id"]})
        new_quantity = item["quantity"] - request["requested_quantity"]
        
        await db.inventory.update_one(
            {"id": request["item_id"]},
            {"$set": {"quantity": new_quantity, "updated_at": datetime.utcnow()}}
        )
    
    await db.withdrawal_requests.update_one(
        {"id": process_data.request_id},
        {"$set": update_data}
    )
    
    return {"message": f"Request {process_data.action}d successfully"}

# Dashboard Analytics Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    # Get inventory stats
    total_items = await db.inventory.count_documents({})
    low_stock_items = await db.inventory.count_documents({"$expr": {"$lte": ["$quantity", "$reorder_level"]}})
    
    # Get items expiring in next 30 days
    next_month = datetime.utcnow() + timedelta(days=30)
    expiring_soon = await db.inventory.count_documents({
        "validity": {"$lte": next_month, "$gte": datetime.utcnow()}
    })
    
    # Get expired items
    expired_items = await db.inventory.count_documents({
        "validity": {"$lt": datetime.utcnow()}
    })
    
    # Get pending requests
    pending_requests = await db.withdrawal_requests.count_documents({"status": RequestStatus.PENDING})
    
    return {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "expiring_soon": expiring_soon,
        "expired_items": expired_items,
        "pending_requests": pending_requests
    }

@api_router.get("/dashboard/category-stats")
async def get_category_stats(current_user: User = Depends(get_current_user)):
    pipeline = [
        {"$group": {
            "_id": "$category",
            "total_items": {"$sum": 1},
            "total_quantity": {"$sum": "$quantity"}
        }}
    ]
    
    result = await db.inventory.aggregate(pipeline).to_list(100)
    return result

@api_router.get("/dashboard/low-stock-items")
async def get_low_stock_items(current_user: User = Depends(get_current_user)):
    items = await db.inventory.find({"$expr": {"$lte": ["$quantity", "$reorder_level"]}}).to_list(100)
    return [InventoryItem(**item) for item in items]

@api_router.get("/dashboard/expiring-items")
async def get_expiring_items(current_user: User = Depends(get_current_user)):
    next_month = datetime.utcnow() + timedelta(days=30)
    items = await db.inventory.find({
        "validity": {"$lte": next_month, "$gte": datetime.utcnow()}
    }).to_list(100)
    return [InventoryItem(**item) for item in items]

# Email Configuration Routes (Admin only)
@api_router.post("/email-config")
async def add_email_config(email_data: EmailConfigCreate, admin: User = Depends(get_admin_user)):
    email_config = EmailConfig(**email_data.dict(), added_by=admin.employee_number)
    await db.email_configs.insert_one(email_config.dict())
    return {"message": "Email added successfully"}

@api_router.get("/email-config")
async def get_email_configs(admin: User = Depends(get_admin_user)):
    configs = await db.email_configs.find({"is_active": True}).to_list(100)
    return [EmailConfig(**config) for config in configs]

@api_router.delete("/email-config/{email_id}")
async def delete_email_config(email_id: str, admin: User = Depends(get_admin_user)):
    result = await db.email_configs.delete_one({"id": email_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email config not found")
    return {"message": "Email configuration deleted successfully"}

# User Management Routes (Admin only)
@api_router.get("/users")
async def get_all_users(admin: User = Depends(get_admin_user)):
    users = await db.users.find().to_list(1000)
    # Remove password_hash and _id from response
    for user in users:
        user.pop('password_hash', None)
        user.pop('_id', None)
    return users

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: User = Depends(get_admin_user)):
    # Prevent admin from deleting themselves
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await create_default_admin()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()