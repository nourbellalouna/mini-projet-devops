
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, abort


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        DATABASE=os.environ.get(
            "DATABASE",
            os.path.join(app.root_path, "incidents.db")
        )
    )

    if test_config is not None:
        app.config.update(test_config)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)

        if db is not None:
            db.close()

    def init_db():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                description TEXT NOT NULL,
                lieu TEXT NOT NULL,
                priorite TEXT NOT NULL,
                statut TEXT NOT NULL DEFAULT 'Nouveau'
            )
        """)
        db.commit()

    with app.app_context():
        init_db()

    @app.route("/")
    def index():
        db = get_db()
        incidents = db.execute(
            "SELECT * FROM incidents ORDER BY id DESC"
        ).fetchall()

        return render_template("index.html", incidents=incidents)

    @app.route("/ajouter", methods=["GET", "POST"])
    def ajouter():
        if request.method == "POST":
            titre = request.form["titre"].strip()
            description = request.form["description"].strip()
            lieu = request.form["lieu"].strip()
            priorite = request.form["priorite"]

            if not titre or not description or not lieu:
                return "Tous les champs sont obligatoires.", 400

            if priorite not in ["Faible", "Moyenne", "Élevée"]:
                abort(400)

            db = get_db()
            db.execute(
                """
                INSERT INTO incidents
                (titre, description, lieu, priorite, statut)
                VALUES (?, ?, ?, ?, 'Nouveau')
                """,
                (titre, description, lieu, priorite)
            )
            db.commit()

            return redirect(url_for("index"))

        return render_template("ajouter.html")

    @app.route("/incident/<int:id>")
    def details(id):
        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (id,)
        ).fetchone()

        if incident is None:
            abort(404)

        return render_template("modifier.html", incident=incident)

    @app.route("/modifier/<int:id>", methods=["POST"])
    def modifier(id):
        statut = request.form["statut"]

        if statut not in ["Nouveau", "En cours", "Résolu"]:
            abort(400)

        db = get_db()
        incident = db.execute(
            "SELECT * FROM incidents WHERE id = ?", (id,)
        ).fetchone()

        if incident is None:
            abort(404)

        db.execute(
            "UPDATE incidents SET statut = ? WHERE id = ?",
            (statut, id)
        )
        db.commit()

        return redirect(url_for("details", id=id))

    @app.route("/supprimer/<int:id>", methods=["POST"])
    def supprimer(id):
        db = get_db()
        db.execute("DELETE FROM incidents WHERE id = ?", (id,))
        db.commit()

        return redirect(url_for("index"))

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
