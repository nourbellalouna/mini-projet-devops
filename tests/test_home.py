from app.app import create_app


def test_home_accessible(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db")
    })

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"Liste des incidents" in response.data