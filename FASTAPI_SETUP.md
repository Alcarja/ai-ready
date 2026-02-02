# FastAPI Project Setup Guide

This guide explains how to create and set up a basic FastAPI project with Poetry, Python virtual environments, and Uvicorn.

## Prerequisites

- Python 3.8 or higher installed
- pip (comes with Python)
- Git (optional, for version control)

## What Each Component Does

### Poetry

Poetry is a Python dependency management and packaging tool. It:

- Manages project dependencies in a `pyproject.toml` file
- Creates and manages virtual environments automatically
- Locks dependency versions in `poetry.lock` for reproducible builds
- Provides an easy way to install, update, and remove packages

### venv (Virtual Environment)

A virtual environment is an isolated Python environment on your machine that:

- Keeps project dependencies separate from system Python
- Prevents dependency conflicts between projects
- Ensures complete isolation - only packages you explicitly install are available
- Makes it clear exactly what's in your project's environment

You create it with `python -m venv` and activate it with `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows). All dependencies are installed exclusively in this folder.

### Uvicorn

Uvicorn is an ASGI (Asynchronous Server Gateway Interface) web server that:

- Runs FastAPI applications
- Handles HTTP requests and responses
- Supports async/await for high-performance applications
- Includes auto-reload for development

### FastAPI

FastAPI is a modern Python web framework that:

- Builds REST APIs quickly and easily
- Provides automatic API documentation (Swagger UI)
- Validates request data with Pydantic models
- Supports async operations for better performance

---

## Step-by-Step Setup

### 1. Create a New Project Directory

```bash
mkdir my-fastapi-project
cd my-fastapi-project
```

### 2. Create a Virtual Environment

Create an isolated Python virtual environment for your project:

```bash
python3 -m venv venv
```

This creates a `venv` directory containing an isolated Python environment.

### 3. Activate the Virtual Environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows:**

```bash
venv\Scripts\activate
```

You should see `(venv)` appear in your terminal prompt, indicating the virtual environment is active.

### 4. Install Poetry (in the Virtual Environment)

Now that your virtual environment is active, install Poetry:

```bash
pip install poetry
```

Verify installation:

```bash
poetry --version
```

Poetry is now installed only in your virtual environment, not system-wide.

### 5. Initialize a Poetry Project

Initialize a new Poetry project:

```bash
poetry init
```

Poetry will ask you a series of questions. Here are recommended answers:

- **Project name**: `my-fastapi-project` (or your project name)
- **Version**: `0.1.0` (default)
- **Description**: `A basic FastAPI project` (or your description)
- **Author**: Your name and email (optional)
- **License**: `MIT` (or your choice)
- **Compatible Python versions**: `^3.8` (or your minimum version)
- **Would you like to define your main dependencies interactively?**: `no` (we'll add them next)

This creates:

- `pyproject.toml` - Project metadata and dependencies
- `poetry.lock` will be created automatically when you run `poetry add` for the first time

### 6. Add Dependencies

With your virtual environment still active, add FastAPI:

```bash
poetry add fastapi
```

This command will:

- Add FastAPI to `pyproject.toml`
- Create `poetry.lock` with exact versions (first time only)
- Install FastAPI in your virtual environment

Add Uvicorn:

```bash
poetry add uvicorn
```

All dependencies are being installed exclusively in your active virtual environment (`venv`).

### 7. Install Dependencies

Install all dependencies from `pyproject.toml` into your virtual environment:

```bash
poetry install
```

This:

- Installs all dependencies in your activated virtual environment only
- Creates/updates `poetry.lock` with exact versions
- Ensures complete isolation from system Python packages

### 8. Create Your First API

Create a file named `main.py` in your project root:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

### 9. Run the Application

Start the development server:

```bash
poetry run uvicorn main:app --reload
```

Breaking this down:

- `poetry run` - Runs a command in the project's virtual environment
- `uvicorn` - The ASGI server
- `main:app` - Imports the `app` object from the `main.py` file
- `--reload` - Auto-reloads the server when code changes (for development only)

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Started reloader process [12346]
```

## Reproducing in Another Environment

### On a New Machine

1. **Clone the project** (if using Git):

   ```bash
   git clone <repository-url>
   cd my-fastapi-project
   ```

2. **Create and activate a virtual environment**:

   **On macOS/Linux:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **On Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Poetry** (in the virtual environment):

   ```bash
   pip install poetry
   ```

4. **Install dependencies**:

   ```bash
   poetry install
   ```

   This installs exact versions from `poetry.lock` into your virtual environment.

5. **Run the application**:

   ```bash
   uvicorn main:app --reload
   ```

   Since you're in the activated virtual environment, you can run `uvicorn` directly without `poetry run`.
