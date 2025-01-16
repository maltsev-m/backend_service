from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from database import SessionLocal
from table_feed import Feed
from table_post import Post
from table_user import User
from schema import UserGet, PostGet, FeedGet

app = FastAPI()

def get_db():
    with SessionLocal() as db:
        return db

def limit(limit: int = 10):
    return limit

@app.get("/user/{id}", response_model=UserGet)
def get_user(id: int, db: Session = Depends(get_db)):
    result = db.execute(select(User).where(User.id == id)).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404)
    return result

@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_user_feed(id: int, limit: int = Depends(limit), db: Session = Depends(get_db)):
    result = db.execute(
        select(Feed)
        .where(Feed.user_id == id)
        .order_by(desc(Feed.time))
        .limit(limit)
    ).scalars().all()
    return result

@app.get("/post/{id}", response_model=PostGet)
def det_post(id: int, db: Session = Depends(get_db)):
    result = db.query(Post).filter(Post.id == id).one_or_none()
    if result is None:
        raise HTTPException(status_code=404)
    return result

@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_user_feed(id: int, limit: int = Depends(limit), db: Session = Depends(get_db)):
    result = (
        db.query(Feed)
        .filter(Feed.post_id == id)
        .order_by(Feed.time.desc())
        .limit(limit)
        .all()
    )
    return result

@app.get("/post/recommendations/", response_model=List[PostGet])
def get_post_recom(id: int, limit: int = Depends(limit), db: Session = Depends(get_db)):
    result = db.execute(
        select(Post.id, Post.text, Post.topic, func.count(Feed.post_id).label("count"))
        .join(Post)
        .where(Feed.action == "like")
        .group_by(Post.id)
        .order_by(desc("count"))
        .limit(limit)
    ).all()
    return(result)

if __name__ == '__main__':
    uvicorn.run(app)