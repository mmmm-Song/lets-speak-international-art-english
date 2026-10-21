# let's speak international art english

A Flask web application that turns an ordinary user-submitted object into a fictional contemporary artwork. The application first generates a complete museum wall label in International Art English (IAE), then derives an OpenAI Images API prompt from that label.

## IAE features and prompt rules

The prompt is based on features discussed by Alix Rule and David Levine in “International Art English.” I chose to exaggerate:

- abstract nominalizations such as *materiality*, *relationality*, *circulation*, and *permeability*;
- inanimate agency, allowing the object to “activate,” “trouble,” “stage,” or “negotiate” an idea;
- spatial language involving thresholds, tensions, and spaces “between” conditions;
- long, confident institutional sentences; and
- theory used as authority through one invented theorist and invented book.

These features are translated into six explicit rules in `SYSTEM_PROMPT` in `app.py`. The first rule requires material precision: the model must preserve the ordinary object's real physical characteristics. The comedy should come from the contrast between the object and its inflated interpretation.

## How the image prompt is derived from the label

The image model never receives the raw object description. The app first generates a structured label containing the artist, title, year, medium, dimensions, provenance, credit line, and extended text. `build_image_prompt()` then uses only that label and the selected curatorial setting.

The label controls the image's scale. A work measuring 600 × 400 cm should occupy the gallery architecture, while “dimensions variable” should create a repeated or distributed arrangement. This ensures that the image is a visualization of the wall label rather than a separate interpretation of the user's input.

## User guide

1. Describe an ordinary object precisely.
2. Choose a white cube, museum vitrine, spotlit plinth, or biennale pavilion.
3. Select **Elevate this object**.
4. Wait while the wall label and installation image are generated.
5. View the image and label together as a gallery display.

Image generation may take approximately one minute.

## Local setup

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Open `.env` and replace `your_api_key_here` with your own OpenAI API key. Never commit `.env`.

Run the application:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

Run the automated tests:

```bash
python -m pytest -q
```

The tests do not call OpenAI or spend API credits.

## Render deployment

This repository includes `render.yaml` and a `Procfile`.

1. Push the project to a new public GitHub repository.
2. In Render, create a Blueprint or Python Web Service from that repository.
3. Add `OPENAI_API_KEY` as a secret environment variable in Render.
4. If configuring manually, use `pip install -r requirements.txt` as the build command and `gunicorn app:app` as the start command.
5. Deploy and visit `/health`; a working service returns `{"status":"ok"}`.

## Reflection: why is a language model so fluent in this dialect?

International Art English is repetitive, formulaic, and widely circulated through exhibition texts, press releases, catalogues, grant applications, and criticism. A language model learns statistical patterns across large collections of text, so it can reproduce recognizable combinations of abstract nouns, theoretical references, institutional confidence, and claims about what an object “activates.” It does not need to believe those claims or understand the institution behind them to mimic the dialect convincingly.

That fluency makes the model useful for studying IAE. When the same rhetoric is applied to a receipt, sock, or broken umbrella, the dialect's structure becomes easier to see. The project therefore uses the model both as a generator and as a critical mirror. Its fluency is not the same as understanding, which is why the prompt insists on preserving the object's concrete physical details.

## References

- Rule, Alix, and David Levine. 2012. [“International Art English.”](https://tc3.canopycanopycanopy.com/series/international_art_english/contents/international_art_english) *Triple Canopy*, no. 16.
- [OpenAI Python API documentation](https://developers.openai.com/api/reference/python)
- [OpenAI image-generation documentation](https://developers.openai.com/api/reference/python/resources/images/methods/generate)

