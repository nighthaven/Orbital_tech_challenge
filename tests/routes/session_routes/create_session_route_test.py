class TestCreateSessionRoutes:

    def test_create_session_route(self, client):
        response = client.post("/api/sessions/")
        assert response.status_code == 200
        assert "session_id" in response.json()
