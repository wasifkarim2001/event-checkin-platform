def test_client_side_routes_get_index_html(client, settings, tmp_path):
    (tmp_path / "index.html").write_text('<div id="root"></div>')
    settings.FRONTEND_DIST = tmp_path
    response = client.get("/staff/events/1/checkin")
    assert response.status_code == 200
    assert response["Cache-Control"] == "no-cache"
    assert b'id="root"' in b"".join(response.streaming_content)


def test_404_when_the_frontend_is_not_built(client, settings, tmp_path):
    settings.FRONTEND_DIST = tmp_path
    assert client.get("/staff").status_code == 404


def test_unknown_api_and_asset_paths_are_not_sent_to_the_frontend(client, settings, tmp_path):
    (tmp_path / "index.html").write_text("app")
    settings.FRONTEND_DIST = tmp_path
    assert client.get("/api/does-not-exist/").status_code == 404
    assert client.get("/assets/missing.js").status_code == 404
