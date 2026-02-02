# Adding SQLAlchemy and Pydantic to FastAPI

This guide continues from the FASTAPI_SETUP.md file and shows how to add database support using SQLAlchemy with a local SQLite database and Pydantic for data validation.

## Prerequisites

- FastAPI project already set up from FASTAPI_SETUP.md
- Virtual environment activated: `source venv/bin/activate`
- Uvicorn running locally (you can stop it for this setup)

## What Each Component Does

### SQLAlchemy

SQLAlchemy is an Object-Relational Mapping (ORM) library that:

- Maps Python classes to database tables
- Handles database queries and operations
- Manages database connections
- Works with multiple databases (SQLite, PostgreSQL, MySQL, etc.)

### Pydantic

Pydantic is a data validation library that:

- Validates incoming request data
- Converts data to correct types
- Generates automatic API documentation
- Handles serialization/deserialization

### SQLite

SQLite is a lightweight, file-based SQL database that:

- Stores data in a single file (`database.db`)
- Requires no server setup
- Perfect for development and small applications
- Easy to backup and distribute

## Step-by-Step Setup

### 1. Add Dependencies

Make sure your virtual environment is activated, then add SQLAlchemy:

```bash
poetry add sqlalchemy
```

Pydantic is typically already installed with FastAPI, but verify it's installed:

```bash
poetry add pydantic
```

### 2. Create Project Structure

This is the **industry-standard structure** for FastAPI projects. Organize your project like this:

```
my-fastapi-project/
├── venv/
├── main.py                                # Entry point - imports and runs everything
├──
├── app/                                   # Application package
│   ├── __init__.py                        # Makes app a package
│   ├── database.py                        # Database configuration and session
│   │
│   ├── models/                            # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── item.py                        # Item model (example)
│   │
│   ├── schemas/                           # Pydantic validation schemas
│   │   ├── __init__.py
│   │   └── item.py                        # Item request/response schemas (example)
│   │
│   ├── crud/                              # Database operations (CRUD)
│   │   ├── __init__.py
│   │   └── item.py                        # Item CRUD functions (example)
│   │
│   └── routes/                            # API routes (routers)
│       ├── __init__.py
│       └── items.py                       # Items router/controller (example)
│
├── pyproject.toml
├── poetry.lock
└── .gitignore
```

**What each folder does:**

- **`app/`** - Contains all application code, organized by concern
- **`app/models/`** - SQLAlchemy ORM model classes (database table definitions)
- **`app/schemas/`** - Pydantic models (request/response validation)
- **`app/crud/`** - Database operations (Create, Read, Update, Delete functions)
- **`app/routes/`** - API route handlers using FastAPI's APIRouter
- **`main.py`** - Entry point that creates the FastAPI app and includes routes

This structure separates concerns and scales well as your project grows.

### 3. Create Database Configuration File

Create `app/database.py` to set up the database connection and session management:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

# Database URL - SQLite file in the project root
DATABASE_URL = "sqlite:///./database.db"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all models inherit from
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes.
    Provides a database session to routes that need it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables defined in models.
    Only creates tables that don't already exist.
    """
    Base.metadata.create_all(bind=engine)
```

**Key components:**

- **DATABASE_URL** - Points to your SQLite database file
- **engine** - Manages database connections
- **SessionLocal** - Factory that creates new database sessions
- **Base** - All your models inherit from this
- **get_db()** - FastAPI dependency that provides database sessions to routes
- **create_tables()** - Call this once on app startup to create all tables

### 4. Create SQLAlchemy Models

Create model files in `app/models/` folder (e.g., `app/models/item.py`):

```python
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**Key components:**

- **`__tablename__`** - Name of the database table
- **`id`** - Primary key with auto-increment, indexed for fast lookups
- **`name`** - String column, indexed for searching
- **`description`** - Optional string column (nullable=True)
- **`created_at`** - DateTime column with default current timestamp
- **`Base`** - All models inherit from this (defined in database.py)

**Column types you'll use:**
- `Integer` - Whole numbers
- `String` - Text (specify max length if needed: `String(100)`)
- `Boolean` - True/False
- `DateTime` - Date and time
- `Float` - Decimal numbers
- `Text` - Long text (no length limit)

### 5. Create Pydantic Schemas

Create schema files in `app/schemas/` folder (e.g., `app/schemas/item.py`):

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ItemCreate(BaseModel):
    """Schema for creating a new item - client sends this"""
    name: str
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item - client sends this"""
    name: Optional[str] = None
    description: Optional[str] = None


class ItemRead(BaseModel):
    """Schema for reading/returning an item - API sends this"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read from SQLAlchemy models
```

**Key components:**

- **`ItemCreate`** - What client sends when creating (no ID, no timestamp)
- **`ItemUpdate`** - What client sends when updating (all fields optional)
- **`ItemRead`** - What API returns to client (includes ID and timestamp)
- **`Optional[str]`** - Field can be string or None
- **`from_attributes = True`** - Lets Pydantic convert SQLAlchemy models to JSON

**Validation features (automatic):**
- Type checking: `name: str` means name must be a string
- Required vs optional: Fields without `Optional` are required
- Default values: `description: Optional[str] = None` defaults to None
- Custom validation available with `@field_validator`

### 6. Create Database Operations

Create CRUD files in `app/crud/` folder (e.g., `app/crud/item.py`):

```python
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def create_item(db: Session, item: ItemCreate) -> Item:
    """Create a new item in the database"""
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_item(db: Session, item_id: int) -> Item | None:
    """Get a single item by ID"""
    return db.query(Item).filter(Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 10) -> list[Item]:
    """Get all items with pagination"""
    return db.query(Item).offset(skip).limit(limit).all()


def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> Item | None:
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
```

**Key components:**

- **`db: Session`** - Database session from `get_db()` dependency
- **`db.add()`** - Add object to session (not saved yet)
- **`db.commit()`** - Save changes to database
- **`db.refresh()`** - Reload object with updated data (like ID, timestamps)
- **`db.query()`** - Create query to fetch data
- **`.filter()`** - Add WHERE clause condition
- **`.first()`** - Get first result or None
- **`.all()`** - Get all results as list
- **`model_dump(exclude_unset=True)`** - Only get fields that were actually set

### 7. Create Route Handlers

Create route files in `app/routes/` folder (e.g., `app/routes/items.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.item import ItemCreate, ItemUpdate, ItemRead
from app.crud import item as crud_item


# Create a router for items
# prefix="/items" means all routes start with /items
# tags are used in API documentation
router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemRead)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item"""
    return crud_item.create_item(db=db, item=item)


@router.get("/", response_model=list[ItemRead])
def get_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all items with pagination"""
    return crud_item.get_items(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific item by ID"""
    db_item = crud_item.get_item(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item"""
    db_item = crud_item.update_item(db=db, item_id=item_id, item_update=item)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item"""
    success = crud_item.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
```

**Key components:**

- **`APIRouter(prefix="/items")`** - Creates router for items, all endpoints start with /items
- **`@router.post("/", ...)`** - POST /items/ - Create new item
- **`@router.get("/", ...)`** - GET /items/ - Get all items
- **`@router.get("/{item_id}")`** - GET /items/1 - Get specific item
- **`@router.put("/{item_id}")`** - PUT /items/1 - Update item
- **`@router.delete("/{item_id}")`** - DELETE /items/1 - Delete item
- **`response_model=ItemRead`** - Tells FastAPI to return data in ItemRead format (automatic validation)
- **`Depends(get_db)`** - Injects database session into the function
- **`HTTPException`** - Return error responses (404, 400, etc.)

### 8. Create Database Tables

Create a function in `app/database.py` that creates all tables:

- Call `Base.metadata.create_all(bind=engine)` to create tables
- This should run once when the application starts
- Only creates tables that don't already exist

### 9. Update Main Application File

Update `main.py` to integrate everything:

```python
from fastapi import FastAPI
from app.database import Base, engine, create_tables
from app.routes import items  # Import your route modules


# Create FastAPI app
app = FastAPI(title="My API", version="1.0.0")


# Create all database tables on startup
@app.on_event("startup")
def startup():
    create_tables()


# Include routers from different modules
app.include_router(items.router)


# Optional: Add a root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to My API"}
```

**Key components:**

- **`FastAPI()`** - Creates the FastAPI application
- **`@app.on_event("startup")`** - Runs once when the app starts
- **`create_tables()`** - Creates all database tables
- **`app.include_router()`** - Includes a router with its endpoints
- **Main route** - Optional welcome endpoint at `/`

**Adding more routers:**
When you create new resources (e.g., users), just add more routers:

```python
from app.routes import items, users, products

app.include_router(items.router)
app.include_router(users.router)
app.include_router(products.router)
```

The key difference from basic FastAPI: you use `include_router()` to bring in routes from separate modules, keeping code organized and maintainable.

### 10. Test the Database Connection

Start your development server:

```bash
poetry run uvicorn main:app --reload
```

Check the project directory for a new `database.db` file (this is your SQLite database).

Visit the API documentation:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### 11. Test CRUD Operations

Using the Swagger UI at `/docs`, test your endpoints:

**Create an item:**

- Click the `POST /items/` endpoint
- Click "Try it out"
- Enter data in the request body (following your create schema)
- Click "Execute"
- Verify successful response

**Get all items:**

- Click the `GET /items/` endpoint
- Click "Try it out"
- Click "Execute"
- Verify items are returned

**Get specific item:**

- Click the `GET /items/{item_id}` endpoint
- Enter the item ID
- Click "Execute"
- Verify correct item is returned

**Update item:**

- Click the `PUT /items/{item_id}` endpoint
- Enter the item ID
- Enter updated data in request body
- Click "Execute"
- Verify changes are saved

**Delete item:**

- Click the `DELETE /items/{item_id}` endpoint
- Enter the item ID
- Click "Execute"
- Verify item is deleted and no longer appears in GET requests

### 12. Verify Data Persistence

Stop the server (Ctrl+C) and restart it:

```bash
poetry run uvicorn main:app --reload
```

Check that your data still exists in the database (the items you created are still there).

### 13. Add to .gitignore

Update your `.gitignore` to exclude the database file:

```
venv/
__pycache__/
*.pyc
.DS_Store
.env
database.db
*.db
```

This prevents the database file from being committed to version control (it will be recreated on each environment).

---

## Common Database Operations

### Adding a New Column to a Model

1. Add the new attribute to your SQLAlchemy model in `models.py`
2. Delete the old `database.db` file
3. Restart the application (new database with new column will be created)

**For production:** You'll want to use database migrations (Alembic) instead of deleting the database.

### Querying with Filters

CRUD functions will use filters like:

- `filter(Model.column == value)` - Exact match
- `filter(Model.column.like("%value%"))` - Partial match
- `filter(Model.column > value)` - Greater than
- `filter(Model.column < value)` - Less than

### Handling Relationships

If you have related tables (e.g., Users and Posts):

- Define foreign keys in models
- Use SQLAlchemy relationship() to navigate relationships
- Load related data in CRUD queries

---

## Troubleshooting

### Database File Not Created

Ensure your database.py file defines the correct SQLite path and that your main.py calls the function to create tables on startup.

### "Table already exists" Error

Delete `database.db` and restart the application.

### Pydantic Validation Errors

Check that your request data matches the schema defined in `schemas.py`. The API documentation at `/docs` shows the expected format.

### Foreign Key Constraint Errors

Ensure you're creating records in the correct order (parent records before child records) and that IDs actually exist.

---

---

## Project Organization Best Practices

### Is the Routes + Controllers Pattern Standard in Python?

**Yes, it's the industry-standard pattern for FastAPI projects.** Here's what each part does:

**Routes** (`app/routes/`) - These are your endpoints/controllers:
- Handle HTTP requests and responses
- Use FastAPI's `APIRouter` to group related endpoints
- Call CRUD functions to access the database
- Validate incoming data using Pydantic schemas
- Return response data to the client

**Controllers vs Routes in Python:**
In Python/FastAPI terminology, we typically use `routes` instead of `controllers`, but they serve the same purpose. The terms are used interchangeably.

**CRUD** (`app/crud/`) - These are your database operations:
- Contain all the SQL query logic (via SQLAlchemy ORM)
- Keep database code separate from HTTP logic
- Make testing easier (you can test database operations independently)
- Allow reuse across multiple routes

**Models** (`app/models/`) - Database table definitions:
- Define what data is stored and how it's structured
- Separate from business logic

**Schemas** (`app/schemas/`) - Request/response validation:
- Define what data clients can send and receive
- Separate from database models (database can have extra fields)
- Generate API documentation automatically

### Data Flow in This Architecture

```
Client Request
    ↓
main.py (FastAPI app)
    ↓
app/routes/items.py (handles HTTP request)
    ↓
app/crud/item.py (database operation)
    ↓
app/models/item.py (database interaction)
    ↓
SQLite Database
    ↓
(data returns back up the chain)
    ↓
Client Response
```

### Separation of Concerns

This structure keeps concerns separated:

- **Routes handle:** HTTP semantics (status codes, headers, endpoints)
- **CRUD handles:** Database queries and operations
- **Models handle:** Database table structure and relationships
- **Schemas handle:** Data validation and documentation

This separation makes code:
- Easier to test (test CRUD independently from routes)
- Easier to maintain (changes to database queries don't affect routes)
- Reusable (one CRUD function can be called from multiple routes)
- Scalable (adding new features doesn't require restructuring)

### Example: Adding a New Resource

To add a new resource (e.g., Users), you would:

1. Create `app/models/user.py` - Define the User table structure
2. Create `app/schemas/user.py` - Define User request/response models
3. Create `app/crud/user.py` - Write database operations (create_user, get_user, etc.)
4. Create `app/routes/users.py` - Define API endpoints using CRUD functions
5. Import the router in `main.py` and include it with `app.include_router(users.router)`

All new code goes into these modules. main.py stays simple and clean.

---

## Next Steps

1. Define your own models based on your application needs
2. Add input validation rules in your Pydantic schemas
3. Implement filtering and searching in GET endpoints
4. Add pagination for large datasets
5. Set up database migrations with Alembic
6. Move to PostgreSQL or MySQL for production
