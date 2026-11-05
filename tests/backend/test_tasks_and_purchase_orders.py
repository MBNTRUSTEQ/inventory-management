"""
Tests for task and purchase order API endpoints.
"""
import pytest

import main


@pytest.fixture(autouse=True)
def reset_in_memory_state():
    """Tasks and purchase orders are module-level lists that persist across
    requests; snapshot and restore them (in place, since main holds references)
    so each test starts from the same state."""
    saved_tasks = list(main.tasks)
    saved_pos = list(main.purchase_orders)
    main.tasks.clear()
    main.purchase_orders.clear()
    yield
    main.tasks[:] = saved_tasks
    main.purchase_orders[:] = saved_pos


def valid_po_payload(backlog_item_id="1"):
    return {
        "backlog_item_id": backlog_item_id,
        "supplier_name": "Acme Components",
        "quantity": 350,
        "unit_cost": 12.5,
        "expected_delivery_date": "2025-12-01",
        "notes": "Expedite",
    }


class TestTasksEndpoints:
    """Test suite for task endpoints."""

    def test_get_all_tasks_empty(self, client):
        """Test that the task list starts empty."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_task(self, client):
        """Test creating a task returns it with an id and pending status."""
        response = client.post(
            "/api/tasks",
            json={"title": "Review stock", "priority": "high", "dueDate": "2025-12-01"},
        )
        assert response.status_code == 201

        task = response.json()
        assert isinstance(task["id"], str)
        assert task["title"] == "Review stock"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-12-01"
        assert task["status"] == "pending"

    def test_create_task_appears_first_in_list(self, client):
        """Test that newly created tasks are listed newest first."""
        client.post("/api/tasks", json={"title": "First", "dueDate": "2025-12-01"})
        client.post("/api/tasks", json={"title": "Second", "dueDate": "2025-12-02"})

        titles = [t["title"] for t in client.get("/api/tasks").json()]
        assert titles == ["Second", "First"]

    def test_create_task_default_priority(self, client):
        """Test that priority defaults to medium."""
        response = client.post("/api/tasks", json={"title": "No priority", "dueDate": "2025-12-01"})
        assert response.status_code == 201
        assert response.json()["priority"] == "medium"

    @pytest.mark.parametrize("payload", [
        {"title": "", "dueDate": "2025-12-01"},
        {"title": "Bad date", "dueDate": "12/01/2025"},
        {"title": "Impossible date", "dueDate": "2025-02-30"},
        {"title": "Bad priority", "priority": "urgent", "dueDate": "2025-12-01"},
        {"dueDate": "2025-12-01"},
    ])
    def test_create_task_invalid_input(self, client, payload):
        """Test that invalid task input is rejected."""
        response = client.post("/api/tasks", json=payload)
        assert response.status_code == 422

    def test_toggle_task(self, client):
        """Test that PATCH toggles status pending -> completed -> pending."""
        task_id = client.post("/api/tasks", json={"title": "Toggle me", "dueDate": "2025-12-01"}).json()["id"]

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

        response = client.patch(f"/api/tasks/{task_id}")
        assert response.json()["status"] == "pending"

    def test_delete_task(self, client):
        """Test deleting a task removes it from the list."""
        task_id = client.post("/api/tasks", json={"title": "Delete me", "dueDate": "2025-12-01"}).json()["id"]

        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert client.get("/api/tasks").json() == []

    @pytest.mark.parametrize("method", ["patch", "delete"])
    def test_nonexistent_task(self, client, method):
        """Test toggling or deleting an unknown task returns 404."""
        response = getattr(client, method)("/api/tasks/nonexistent-999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestPurchaseOrderEndpoints:
    """Test suite for purchase order endpoints."""

    def test_create_purchase_order(self, client):
        """Test creating a purchase order for a backlog item."""
        response = client.post("/api/purchase-orders", json=valid_po_payload())
        assert response.status_code == 201

        po = response.json()
        assert isinstance(po["id"], str)
        assert po["backlog_item_id"] == "1"
        assert po["supplier_name"] == "Acme Components"
        assert po["quantity"] == 350
        assert abs(po["unit_cost"] - 12.5) < 0.01
        assert po["expected_delivery_date"] == "2025-12-01"
        assert po["status"] == "pending"
        assert po["notes"] == "Expedite"
        # created_date is ISO YYYY-MM-DD
        assert len(po["created_date"]) == 10 and po["created_date"][4] == "-"

    def test_get_purchase_order_by_backlog_item(self, client):
        """Test fetching a created PO by its backlog item id."""
        created = client.post("/api/purchase-orders", json=valid_po_payload()).json()

        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 200
        assert response.json() == created

    def test_get_nonexistent_purchase_order(self, client):
        """Test fetching a PO for a backlog item without one returns 404."""
        response = client.get("/api/purchase-orders/1")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_purchase_order_unknown_backlog_item(self, client):
        """Test creating a PO for an unknown backlog item returns 404."""
        response = client.post("/api/purchase-orders", json=valid_po_payload("nonexistent-999"))
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_duplicate_purchase_order(self, client):
        """Test that a backlog item can only have one PO."""
        client.post("/api/purchase-orders", json=valid_po_payload())
        response = client.post("/api/purchase-orders", json=valid_po_payload())
        assert response.status_code == 409

    @pytest.mark.parametrize("override", [
        {"quantity": 0},
        {"unit_cost": -1},
        {"supplier_name": ""},
        {"expected_delivery_date": "next week"},
        {"expected_delivery_date": "2025-13-45"},
    ])
    def test_create_purchase_order_invalid_input(self, client, override):
        """Test that invalid PO input is rejected."""
        response = client.post("/api/purchase-orders", json={**valid_po_payload(), **override})
        assert response.status_code == 422

    def test_backlog_purchase_order_id(self, client):
        """Test that /api/backlog reports the PO id once one is created."""
        backlog = client.get("/api/backlog").json()
        for item in backlog:
            assert item["purchase_order_id"] is None
            assert item["has_purchase_order"] is False

        po = client.post("/api/purchase-orders", json=valid_po_payload()).json()

        backlog = {item["id"]: item for item in client.get("/api/backlog").json()}
        assert backlog["1"]["purchase_order_id"] == po["id"]
        assert backlog["1"]["has_purchase_order"] is True
        assert backlog["2"]["purchase_order_id"] is None
