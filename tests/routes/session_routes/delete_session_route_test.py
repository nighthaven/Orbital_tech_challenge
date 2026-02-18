class TestDeleteSessionRoute:
    def test_delete_session_route(self, client):
        create_session_return_id = client.post("/api/sessions/")
        session_id = create_session_return_id.json()["session_id"]
        responses = client.delete(f"/api/sessions/{session_id}")
        assert responses.status_code == 204

    def test_delete_session_not_found(self, client):
        response = client.delete("/api/sessions/nonexistent")
        assert response.status_code == 404
