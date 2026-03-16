# =============================================================================
# test_main.py - Unit tests for the FastAPI TODO List application
# =============================================================================
# Run these tests with:
#   cd src
#   pytest tests/ -v
# =============================================================================

import sys
import os

# Add the src directory to the Python path so we can import main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from main import app, reset_state

# Create a test client for our FastAPI application
client = TestClient(app)


# =============================================================================
# FIXTURES - Setup and teardown for tests
# =============================================================================

@pytest.fixture(autouse=True)
def clear_todos():
    """
    This fixture runs before EACH test to clear the database.
    This ensures tests don't interfere with each other.
    """
    reset_state()
    yield
    reset_state()


# =============================================================================
# TESTS FOR ROOT ENDPOINT
# =============================================================================

def test_root():
    """Test the root endpoint returns a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Welcome" in data["message"]


# =============================================================================
# TESTS FOR HEALTH ENDPOINT
# =============================================================================

def test_health_check():
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data


# =============================================================================
# TESTS FOR METRICS ENDPOINT
# =============================================================================

def test_metrics_empty():
    """Test metrics endpoint when no todos exist."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_todos"] == 0
    assert data["completed"] == 0
    assert data["pending"] == 0
    assert data["completion_rate"] == 0


def test_metrics_with_todos():
    """Test metrics endpoint with some todos."""
    # Create 3 todos
    client.post("/todos", json={"title": "Todo 1", "status": "pending"})
    client.post("/todos", json={"title": "Todo 2", "status": "pending"})
    client.post("/todos", json={"title": "Todo 3", "status": "pending"})

    # Complete one todo (we need the ID from the first creation)
    response = client.get("/todos")
    todos = response.json()["todos"]
    first_id = todos[0]["id"]
    client.put(f"/todos/{first_id}/complete")

    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_todos"] == 3
    assert data["completed"] == 1
    assert data["pending"] == 2


# =============================================================================
# TESTS FOR TODO CRUD OPERATIONS
# =============================================================================

def test_list_todos_empty():
    """Test listing todos when database is empty."""
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["todos"] == []


def test_create_todo():
    """Test creating a new TODO item."""
    todo_data = {
        "title": "Learn FastAPI",
        "description": "Study the FastAPI documentation",
        "status": "pending"
    }
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "TODO created successfully"
    assert data["todo"]["title"] == "Learn FastAPI"
    assert data["todo"]["description"] == "Study the FastAPI documentation"
    assert data["todo"]["status"] == "pending"
    assert "id" in data["todo"]
    assert "created_at" in data["todo"]


def test_create_todo_minimal():
    """Test creating a TODO with only the required title field."""
    response = client.post("/todos", json={"title": "Minimal TODO"})
    assert response.status_code == 201
    data = response.json()
    assert data["todo"]["title"] == "Minimal TODO"
    assert data["todo"]["status"] == "pending"  # default value
    assert data["todo"]["description"] == ""  # default value


def test_get_todo():
    """Test getting a specific TODO by ID."""
    # First create a todo
    create_response = client.post("/todos", json={"title": "Test TODO"})
    todo_id = create_response.json()["todo"]["id"]

    # Then get it
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["todo"]["id"] == todo_id
    assert data["todo"]["title"] == "Test TODO"


def test_get_todo_not_found():
    """Test getting a TODO that doesn't exist returns 404."""
    response = client.get("/todos/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_todo():
    """Test updating an existing TODO."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "Original Title"})
    todo_id = create_response.json()["todo"]["id"]

    # Update it
    update_data = {
        "title": "Updated Title",
        "description": "Updated description",
        "status": "in_progress"
    }
    response = client.put(f"/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "TODO updated successfully"
    assert data["todo"]["title"] == "Updated Title"
    assert data["todo"]["status"] == "in_progress"


def test_update_todo_not_found():
    """Test updating a TODO that doesn't exist returns 404."""
    update_data = {"title": "Updated", "description": "", "status": "pending"}
    response = client.put("/todos/9999", json=update_data)
    assert response.status_code == 404


def test_delete_todo():
    """Test deleting a TODO item."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "To be deleted"})
    todo_id = create_response.json()["todo"]["id"]

    # Delete it
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()

    # Verify it's gone
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404


def test_delete_todo_not_found():
    """Test deleting a TODO that doesn't exist returns 404."""
    response = client.delete("/todos/9999")
    assert response.status_code == 404


def test_complete_todo():
    """Test marking a TODO as completed."""
    # Create a todo
    create_response = client.post("/todos", json={"title": "To be completed"})
    todo_id = create_response.json()["todo"]["id"]

    # Complete it
    response = client.put(f"/todos/{todo_id}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["todo"]["status"] == "completed"
    assert "completed" in data["message"].lower()


def test_complete_todo_not_found():
    """Test completing a TODO that doesn't exist returns 404."""
    response = client.put("/todos/9999/complete")
    assert response.status_code == 404


def test_list_todos_after_create():
    """Test that listing todos shows all created todos."""
    # Create multiple todos
    client.post("/todos", json={"title": "Todo 1"})
    client.post("/todos", json={"title": "Todo 2"})
    client.post("/todos", json={"title": "Todo 3"})

    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["todos"]) == 3
