# =============================================================================
# main.py - FastAPI TODO List Application
# =============================================================================
# This is the main application file for our DevOps project.
# It provides a REST API for managing TODO items.
#
# Endpoints:
#   GET  /         - Welcome message
#   GET  /health   - Health check (used by Kubernetes)
#   GET  /metrics  - Prometheus-style metrics
#   GET  /todos    - List all TODOs
#   POST /todos    - Create a new TODO
#   GET  /todos/{id}        - Get a specific TODO
#   PUT  /todos/{id}        - Update a TODO
#   DELETE /todos/{id}      - Delete a TODO
#   PUT  /todos/{id}/complete - Mark a TODO as completed
# =============================================================================

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Create the FastAPI application with metadata for Swagger UI
app = FastAPI(
    title="TODO List API",
    description="""
## DevOps Learning Project - TODO List API

This API demonstrates a complete DevOps workflow including:
- **CI/CD** with GitHub Actions
- **Containerization** with Docker
- **Orchestration** with Kubernetes
- **Monitoring** with Prometheus metrics

### Features
- Create, Read, Update, Delete TODO items
- Health check endpoint for Kubernetes probes
- Metrics endpoint for monitoring
""",
    version="1.0.0",
    contact={
        "name": "DevOps Student",
        "email": "student@example.com",
    },
)


# =============================================================================
# DATA MODELS (Pydantic schemas)
# =============================================================================

class Todo(BaseModel):
    """Model for creating or updating a TODO item."""
    title: str
    description: str = ""
    status: str = "pending"

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Learn FastAPI",
                "description": "Study the FastAPI documentation",
                "status": "pending"
            }
        }
    }


class TodoResponse(BaseModel):
    """Model for TODO item responses."""
    id: int
    title: str
    description: str
    status: str
    created_at: str


# =============================================================================
# IN-MEMORY DATABASE (for learning purposes)
# In production, you would use a real database like PostgreSQL
# Note: This counter is not thread-safe. In production with multiple workers,
# use a database sequence or UUID for unique IDs instead.
# =============================================================================

todos_db: List[dict] = []  # List to store TODO items
todo_counter: int = 0       # Counter to generate unique IDs


def reset_state() -> None:
    """Reset the application state (used in testing)."""
    global todo_counter
    todos_db.clear()
    todo_counter = 0


# =============================================================================
# ROUTES / ENDPOINTS
# =============================================================================

@app.get(
    "/",
    summary="Welcome message",
    description="Returns a welcome message with a link to the API documentation."
)
def root():
    """Welcome endpoint - entry point of the API."""
    return {
        "message": "Welcome to TODO List API",
        "docs": "Visit http://localhost:8000/docs for Swagger UI",
        "version": "1.0.0"
    }


@app.get(
    "/health",
    summary="Health check",
    description="Used by Kubernetes liveness and readiness probes to check if the app is running.",
    tags=["Monitoring"]
)
def health_check():
    """
    Health check endpoint.

    Returns the current status and timestamp.
    Kubernetes uses this to know if the pod is healthy.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "todo-api"
    }


@app.get(
    "/metrics",
    summary="Application metrics",
    description="Returns Prometheus-style metrics about the TODO items.",
    tags=["Monitoring"]
)
def metrics():
    """
    Metrics endpoint for monitoring.

    Returns counts of todos by status.
    In a real project, you would use the prometheus_client library.
    """
    completed_count = len([t for t in todos_db if t["status"] == "completed"])
    pending_count = len([t for t in todos_db if t["status"] == "pending"])
    in_progress_count = len([t for t in todos_db if t["status"] == "in_progress"])

    return {
        "total_todos": len(todos_db),
        "completed": completed_count,
        "pending": pending_count,
        "in_progress": in_progress_count,
        "completion_rate": round(completed_count / len(todos_db) * 100, 2) if todos_db else 0
    }


@app.get(
    "/todos",
    summary="List all TODOs",
    description="Returns a list of all TODO items in the database.",
    tags=["TODOs"]
)
def list_todos():
    """Get all TODO items."""
    return {
        "count": len(todos_db),
        "todos": todos_db
    }


@app.get(
    "/todos/{todo_id}",
    summary="Get a specific TODO",
    description="Returns a single TODO item by its ID.",
    tags=["TODOs"]
)
def get_todo(todo_id: int):
    """
    Get a specific TODO by ID.

    Raises a 404 error if the TODO is not found.
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return {"todo": todo}

    # If not found, return 404 error
    raise HTTPException(
        status_code=404,
        detail=f"TODO with id {todo_id} not found"
    )


@app.post(
    "/todos",
    status_code=201,
    summary="Create a new TODO",
    description="Creates a new TODO item and returns it.",
    tags=["TODOs"]
)
def create_todo(todo: Todo):
    """
    Create a new TODO item.

    Returns the created TODO with its generated ID.
    """
    global todo_counter
    todo_counter += 1

    new_todo = {
        "id": todo_counter,
        "title": todo.title,
        "description": todo.description,
        "status": todo.status,
        "created_at": datetime.now().isoformat()
    }
    todos_db.append(new_todo)

    return {
        "message": "TODO created successfully",
        "todo": new_todo
    }


@app.put(
    "/todos/{todo_id}",
    summary="Update a TODO",
    description="Updates an existing TODO item by its ID.",
    tags=["TODOs"]
)
def update_todo(todo_id: int, todo: Todo):
    """
    Update an existing TODO item.

    Raises a 404 error if the TODO is not found.
    """
    for i, t in enumerate(todos_db):
        if t["id"] == todo_id:
            # Update the todo while keeping the original id and created_at
            updated = {
                **t,
                "title": todo.title,
                "description": todo.description,
                "status": todo.status
            }
            todos_db[i] = updated
            return {
                "message": "TODO updated successfully",
                "todo": updated
            }

    raise HTTPException(
        status_code=404,
        detail=f"TODO with id {todo_id} not found"
    )


@app.delete(
    "/todos/{todo_id}",
    summary="Delete a TODO",
    description="Deletes a TODO item by its ID.",
    tags=["TODOs"]
)
def delete_todo(todo_id: int):
    """
    Delete a TODO item.

    Raises a 404 error if the TODO is not found.
    """
    for i, t in enumerate(todos_db):
        if t["id"] == todo_id:
            deleted = todos_db.pop(i)
            return {
                "message": "TODO deleted successfully",
                "deleted_todo": deleted
            }

    raise HTTPException(
        status_code=404,
        detail=f"TODO with id {todo_id} not found"
    )


@app.put(
    "/todos/{todo_id}/complete",
    summary="Mark a TODO as completed",
    description="Marks a specific TODO item as completed.",
    tags=["TODOs"]
)
def complete_todo(todo_id: int):
    """
    Mark a TODO as completed.

    Raises a 404 error if the TODO is not found.
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            todo["status"] = "completed"
            return {
                "message": "TODO marked as completed",
                "todo": todo
            }

    raise HTTPException(
        status_code=404,
        detail=f"TODO with id {todo_id} not found"
    )
