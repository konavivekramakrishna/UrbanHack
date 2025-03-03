import heapq
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..schemas import UserCreate, UserUpdateInterests
from ..models import User
from ..database import get_db
from ..utils.bitmask_utils import compute_bitmask, decode_bitmask, hamming_similarity
from ..cache.user_cache import get_user_cache, set_user_cache, invalidate_user_cache
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/users", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if user.gender not in ("M", "F"):
        raise HTTPException(status_code=400, detail="Gender must be 'M' or 'F'.")
    bitmask = compute_bitmask(user.interests)
    new_user = User(
        name=user.name,
        email=user.email,
        gender=user.gender,
        city=user.city,
        interest_bitmask=bitmask,
    )
    db.add(new_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user.")
    db.refresh(new_user)
    return {"user_id": new_user.id, "message": "User created successfully."}

@router.put("/users/{user_id}/interests/", response_model=dict)
async def update_user_interests(
    user_id: int,
    update: UserUpdateInterests,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    new_mask = compute_bitmask(update.interests)
    user.interest_bitmask = new_mask

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating interests for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating interests.")
    
    # Prepare the updated user data
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender,
        "city": user.city,
        "interests": decode_bitmask(user.interest_bitmask)
    }
    # Schedule cache update in the background.
    redis_client = request.app.state.redis
    background_tasks.add_task(set_user_cache, redis_client, user_id, user_data)
    
    return {"user_id": user_id, "message": "User interests updated successfully."}

@router.get("/users", response_model=dict)
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    if skip < 0 or limit <= 0:
        raise HTTPException(status_code=400, detail="Invalid pagination parameters.")
    users = db.query(User).offset(skip).limit(limit).all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "gender": user.gender,
            "city": user.city,
            "interests": decode_bitmask(user.interest_bitmask)
        })
    return {"users": result}

@router.get("/users/{user_id}", response_model=dict)
async def read_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    redis_client = request.app.state.redis
    cached_user = await get_user_cache(redis_client, user_id)
    if cached_user:
        return cached_user

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "gender": user.gender,
        "city": user.city,
        "interests": decode_bitmask(user.interest_bitmask)
    }
    # Update the cache (this can be done synchronously since it happens after reading from the DB).
    await set_user_cache(redis_client, user_id, user_data)
    return user_data

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.delete(user)
    db.commit()

    # Schedule cache invalidation in the background.
    redis_client = request.app.state.redis
    background_tasks.add_task(invalidate_user_cache, redis_client, user_id)
    
    return {"message": "User deleted successfully."}

@router.get("/{user_id}/matches/", response_model=dict)
async def get_user_matches(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    # Retrieve the current user; if not found, return 404.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Retrieve all candidate users (users of opposite gender).
    candidates = db.query(User).filter(User.gender != user.gender, User.id != user_id).all()
    
    top_matches = heapq.nlargest(
        limit,
        ((hamming_similarity(user.interest_bitmask, candidate.interest_bitmask), candidate)
         for candidate in candidates),
        key=lambda x: x[0]
    )
    
    result = []
    for similarity, candidate in top_matches:
        candidate_info = {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "gender": candidate.gender,
            "city": candidate.city,
            "interests": decode_bitmask(candidate.interest_bitmask)
        }
        result.append({
            "candidate": candidate_info,
            "similarity": similarity
        })
    
    return {"matches": result}
