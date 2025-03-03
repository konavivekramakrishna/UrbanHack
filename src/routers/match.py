import heapq
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from ..models import User
from ..database import get_db
from ..utils.bitmask_utils import hamming_similarity, decode_bitmask
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{user_id}/matches/", response_model=dict)
async def get_user_matches(
    user_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
):
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
    
    # Build the result with full candidate details.
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
