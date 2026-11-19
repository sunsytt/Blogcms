BLOG = {"name": "Frontend Diary", "slug": "frontend-diary", "description": "Apuntes de frontend"}

POST = {
    "title": "Bienvenido a Frontend Diary",
    "slug": "bienvenida",
    "description": "Por qué empecé este blog.",
    "body_markdown": "Primer artículo.",
    "category": "Frontend",
    "tags": ["astro", "blog"],
    "pub_date": "2026-09-21",
    "draft": False,
}

LANDING = {
    "site_title": "Katia · Desarrollo Frontend",
    "hero_title": "Interfaces claras, construidas paso a paso",
    "about_paragraphs": ["Primero", "Segundo"],
    "tech_groups": [
        {"name": "Web", "items": ["React", "Tailwind"]},
        {"name": "Aprendiendo ahora", "is_learning_now": True, "items": ["Kotlin"]},
    ],
    "timeline_entries": [{"date_label": "2025–2026", "title": "Funlish", "description": "Frontend"}],
    "links": [{"label": "GitHub", "url": "https://github.com/sunsytt", "detail": "github.com/sunsytt"}],
}


def make_blog(client) -> int:
    response = client.post("/api/blogs", json=BLOG)
    assert response.status_code == 201
    return response.json()["id"]


def test_blog_crud_and_duplicate_slug(client):
    blog_id = make_blog(client)
    assert client.get(f"/api/blogs/{blog_id}").json()["slug"] == "frontend-diary"
    assert client.post("/api/blogs", json=BLOG).status_code == 409

    updated = client.put(f"/api/blogs/{blog_id}", json={"name": "Otro nombre"})
    assert updated.status_code == 200 and updated.json()["name"] == "Otro nombre"

    assert client.delete(f"/api/blogs/{blog_id}").status_code == 204
    assert client.get(f"/api/blogs/{blog_id}").status_code == 404


def test_post_description_limit_and_slug_rules(client):
    blog_id = make_blog(client)

    too_long = {**POST, "description": "x" * 161}
    assert client.post(f"/api/blogs/{blog_id}/posts", json=too_long).status_code == 422

    bad_slug = {**POST, "slug": "No Es Slug"}
    assert client.post(f"/api/blogs/{blog_id}/posts", json=bad_slug).status_code == 422

    created = client.post(f"/api/blogs/{blog_id}/posts", json=POST)
    assert created.status_code == 201
    assert created.json()["tags"] == ["astro", "blog"]

    assert client.post(f"/api/blogs/{blog_id}/posts", json=POST).status_code == 409
    assert client.post("/api/blogs/999/posts", json=POST).status_code == 404


def test_post_update_and_draft_filter(client):
    blog_id = make_blog(client)
    post_id = client.post(f"/api/blogs/{blog_id}/posts", json=POST).json()["id"]
    client.post(
        f"/api/blogs/{blog_id}/posts", json={**POST, "slug": "borrador", "draft": True}
    )

    assert len(client.get(f"/api/blogs/{blog_id}/posts").json()) == 2
    published = client.get(f"/api/blogs/{blog_id}/posts", params={"include_drafts": False}).json()
    assert [p["slug"] for p in published] == ["bienvenida"]

    # Solo cambia lo enviado; un null en un campo obligatorio se ignora.
    changed = client.put(f"/api/posts/{post_id}", json={"title": "Nuevo título", "category": None})
    assert changed.json()["title"] == "Nuevo título"
    assert changed.json()["category"] == "Frontend"
    assert client.put(f"/api/posts/{post_id}", json={"description": "y" * 161}).status_code == 422


def test_project_crud(client):
    blog_id = make_blog(client)
    project = {
        "title": "Funlish",
        "description": "Plataforma de inglés",
        "technologies": ["React", "Javalin"],
        "featured": True,
    }
    created = client.post(f"/api/blogs/{blog_id}/projects", json=project)
    assert created.status_code == 201
    project_id = created.json()["id"]
    assert client.get(f"/api/blogs/{blog_id}/projects").json()[0]["technologies"] == ["React", "Javalin"]
    assert client.delete(f"/api/projects/{project_id}").status_code == 204
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_landing_upsert_replaces_lists(client):
    blog_id = make_blog(client)
    assert client.get(f"/api/blogs/{blog_id}/landing").status_code == 404

    first = client.put(f"/api/blogs/{blog_id}/landing", json=LANDING)
    assert first.status_code == 200
    body = first.json()
    assert body["tech_groups"][0] == {"name": "Web", "is_learning_now": False, "items": ["React", "Tailwind"]}
    assert body["tech_groups"][1]["is_learning_now"] is True
    assert body["timeline_entries"][0]["date_label"] == "2025–2026"

    # Segundo PUT: la lista anterior se reemplaza, no se acumula.
    second = client.put(
        f"/api/blogs/{blog_id}/landing",
        json={**LANDING, "tech_groups": [{"name": "Solo uno", "items": ["Astro"]}], "links": []},
    )
    assert second.json()["id"] == body["id"]
    assert [g["name"] for g in second.json()["tech_groups"]] == ["Solo uno"]
    assert second.json()["links"] == []

    assert client.delete(f"/api/blogs/{blog_id}/landing").status_code == 204


def test_build_with_mock_builder_records_result(client):
    blog_id = make_blog(client)
    client.post(f"/api/blogs/{blog_id}/posts", json=POST)
    client.post(f"/api/blogs/{blog_id}/posts", json={**POST, "slug": "borrador", "draft": True})
    client.put(f"/api/blogs/{blog_id}/landing", json=LANDING)

    response = client.post("/api/build", json={"blogId": blog_id})
    assert response.status_code == 200
    build = response.json()
    assert build["blogId"] == blog_id
    assert build["status"] == "success"
    assert build["result"]["publishedPosts"] == 1

    assert client.get(f"/api/build/{build['id']}").json()["status"] == "success"
    assert len(client.get(f"/api/blogs/{blog_id}/builds").json()) == 1
    assert client.post("/api/build", json={"blogId": 999}).status_code == 404


def test_build_failure_is_recorded_and_returns_502(client, failing_builder):
    blog_id = make_blog(client)
    response = client.post("/api/build", json={"blogId": blog_id})
    assert response.status_code == 502

    builds = client.get(f"/api/blogs/{blog_id}/builds").json()
    assert builds[0]["status"] == "failed"
    assert builds[0]["error"] == "Builder caído"


def test_metrics_with_mock_client(client):
    blog_id = make_blog(client)
    response = client.get(f"/api/metrics/{blog_id}")
    assert response.status_code == 200
    assert set(response.json()) == {"blogId", "visitas", "visitantesUnicos"}
    assert client.get("/api/metrics/999").status_code == 404
