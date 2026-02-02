from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.item import ItemCreate, ItemUpdate, ItemRead
from app.controllers.itemController import (
    create_item as create_item_db,
    get_itemById as get_itemById_db,
    get_items as get_items_db,
    update_itemById as update_itemById_db,
    delete_item as delete_item_db
)

# Create a router for items
# prefix="/items" means all routes start with /items
# tags are used in API documentation
router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    return create_item_db(db=db, item=item)


@router.get("/", response_model=list[ItemRead])
def get_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all items with pagination"""
    return get_items_db(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    db_item = get_itemById_db(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    db_item = update_itemById_db(db=db, item_id=item_id, item_update=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    success = delete_item_db(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}