import json

import app as art_app


SAMPLE_LABEL = {
    "artist": "Mara Venn",
    "bio": "b. 1997, lives and works between Verdun and the cloud",
    "title": "Receipt for a Minor Weather System",
    "year": "2026",
    "medium": "Thermal paper, coffee, deferred accountability",
    "dimensions": "600 × 400 × 2 cm",
    "provenance": "Found beside a campus printer, 2026; private collection of an overnight cashier",
    "credit_line": "Gift of the artist's backpack",
    "extended_label": (
        "Enlarged beyond the scale of its disposable origin, Venn's receipt stages a tension "
        "between proof and disappearance. Its coffee ring activates the administrative surface "
        "as both stain and unofficial seal, while the missing corner troubles the fantasy of a "
        "complete transaction. In The Soft Ledger, invented theorist Elian Quorb calls this "
        "condition transactional permeability: the point at which an object remembers being "
        "handled more clearly than what it was meant to record. Here, thermal paper negotiates "
        "with architecture, insisting that minor evidence can occupy institutional space."
    ),
}


def test_homepage_and_health_route():
    client = art_app.app.test_client()

    page = client.get("/")
    health = client.get("/health")

    assert page.status_code == 200
    assert b"let's speak international art english" in page.data
    assert health.get_json() == {"status": "ok"}


def test_blank_description_does_not_call_openai():
    client = art_app.app.test_client()
    response = client.post("/", data={"prompt": "", "setting": "white cube"})

    assert response.status_code == 200
    assert b"Please describe an object" in response.data


def test_label_parser_requires_all_fields():
    parsed = art_app.parse_label(json.dumps(SAMPLE_LABEL))
    assert parsed["artist"] == "Mara Venn"


def test_image_prompt_uses_label_and_not_raw_description():
    prompt = art_app.build_image_prompt(SAMPLE_LABEL, "white cube")

    assert SAMPLE_LABEL["title"] in prompt
    assert SAMPLE_LABEL["dimensions"] in prompt
    assert SAMPLE_LABEL["extended_label"] in prompt
    assert "white cube" in prompt
    assert "RAW-USER-DESCRIPTION" not in prompt

