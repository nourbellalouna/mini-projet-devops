
from app.app import create_app


def create_test_app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db")
    })


def test_ajouter_incident(tmp_path):
    app = create_test_app(tmp_path)
    client = app.test_client()

    response = client.post("/ajouter", data={
        "titre": "Panne Internet",
        "description": "Connexion impossible",
        "lieu": "Salle B12",
        "priorite": "Élevée"
    })

    assert response.status_code == 302

    response = client.get("/")

    assert b"Panne Internet" in response.data


def test_consulter_incident(tmp_path):
    app = create_test_app(tmp_path)
    client = app.test_client()

    client.post("/ajouter", data={
        "titre": "Panne ordinateur",
        "description": "Ordinateur ne demarre pas",
        "lieu": "Salle A1",
        "priorite": "Moyenne"
    })

    response = client.get("/incident/1")

    assert response.status_code == 200
    assert b"Panne ordinateur" in response.data


def test_modifier_statut(tmp_path):
    app = create_test_app(tmp_path)
    client = app.test_client()

    client.post("/ajouter", data={
        "titre": "Probleme reseau",
        "description": "Reseau indisponible",
        "lieu": "Laboratoire",
        "priorite": "Faible"
    })

    response = client.post("/modifier/1", data={
        "statut": "En cours"
    })

    assert response.status_code == 302

    response = client.get("/incident/1")

    assert b"En cours" in response.data


def test_supprimer_incident(tmp_path):
    app = create_test_app(tmp_path)
    client = app.test_client()

    client.post("/ajouter", data={
        "titre": "Incident a supprimer",
        "description": "Test de suppression",
        "lieu": "Salle B2",
        "priorite": "Faible"
    })

    response = client.post("/supprimer/1")

    assert response.status_code == 302

    response = client.get("/")

    assert b"Incident a supprimer" not in response.data


def test_incident_introuvable(tmp_path):
    app = create_test_app(tmp_path)
    client = app.test_client()

    response = client.get("/incident/999")

    assert response.status_code == 404
