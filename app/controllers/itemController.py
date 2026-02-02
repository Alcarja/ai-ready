from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def create_item(db: Session, item: ItemCreate) -> Item:
    """Create a new item in the database"""
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item



def get_itemById(db: Session, item_id: int):
    """Get item with specific columns only"""
    stmt = select(
        Item.id, 
        Item.name
        ).where(Item.id == item_id)
    return db.execute(stmt).first()


def get_items(db: Session, skip: int = 0, limit: int = 10) -> list[Item]:
    """Get all items with pagination"""
    return db.query(Item).offset(skip).limit(limit).all()


def update_itemById(db: Session, item_id: int, item_update: ItemUpdate) -> Item | None:
    """Update an existing item"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return None

    # Update only provided fields
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    """Delete an item by ID"""
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        return False

    db.delete(db_item)
    db.commit()
    return True