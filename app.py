from flask import Flask, render_template, request
from openai import OpenAI
from dotenv import load_dotenv
import json
import os


load_dotenv()

app = Flask(__name__)


SYSTEM_PROMPT = """
You write museum wall labels in exaggerated International Art English (IAE).

Always follow these rules:

1. Stay materially precise. Preserve the submitted object's real colour,
   material, damage, shape, and ordinary function. Do not transform it into a
   fantasy object. The humour comes from the gap between the mundane object and
   the inflated interpretation.

2. Exaggerate IAE through abstract nominalizations such as materiality,
   relationality, circulation, spatiality, permeability, and potentiality.
   Include at least one tension, threshold, or space "between" two conditions.

3. Give the object agency: it may activate, trouble, negotiate, stage, insist,
   or destabilize. Use a serious, confident institutional voice rather than
   punchlines or random surrealism.

4. Invent the artist, biography, theorist, book, provenance, and credit line.
   Never borrow the name, quotation, reputation, or style of a real artist,
   critic, curator, institution, or theorist.

5. Include every requested tombstone field. The medium may combine real
   materials with one or two abstractions. Dimensions must be clear enough to
   control the visible scale of the installation image.

6. The extended label must contain 80–120 words and cite one invented theorist
   and one invented book title.

Return only valid JSON. Do not add Markdown fences or explanatory text.
"""


REQUIRED_FIELDS = {
    "artist",
    "bio",
    "title",
    "year",
    "medium",
    "dimensions",
    "provenance",
    "credit_line",
    "extended_label",
}


def get_openai_client():
    """Create the client only when the user submits the form."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file, then restart the app."
        )

    return OpenAI(api_key=api_key)


def parse_label(response_text):
    """Convert the model's JSON text into a validated Python dictionary."""
    cleaned_text = response_text.strip()

    if cleaned_text.startswith("```"):
        lines = cleaned_text.splitlines()
        cleaned_text = "\n".join(lines[1:-1])

    label = json.loads(cleaned_text)

    if not REQUIRED_FIELDS.issubset(label):
        raise ValueError("The generated label is missing required fields.")

    return label


def generate_label(client, object_description, setting):
    user_prompt = f"""
The submitted object is:
{object_description}

The required curatorial setting is:
{setting}

Return this exact JSON structure:
{{
  "artist": "invented artist name",
  "bio": "invented birth and lives-and-works line",
  "title": "invented artwork title",
  "year": "year",
  "medium": "real materials mixed with abstractions",
  "dimensions": "clear dimensions with units, or dimensions variable",
  "provenance": "invented ownership history",
  "credit_line": "invented credit line",
  "extended_label": "80–120 words citing one invented theorist and book"
}}
"""

    # A second attempt is used only if the model misses the required word range.
    for attempt in range(2):
        response = client.responses.create(
            model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1"),
            instructions=SYSTEM_PROMPT,
            input=user_prompt,
        )

        label = parse_label(response.output_text)
        word_count = len(label["extended_label"].split())

        if 80 <= word_count <= 120:
            label["word_count"] = word_count
            return label

        user_prompt += f"""

Correction: the previous extended label had {word_count} words. Rewrite the
complete JSON response so the extended label contains 80–120 words.
"""

    raise ValueError("The model did not produce an 80–120 word extended label.")


def build_image_prompt(label, setting):
    """Build the image prompt only from the completed label."""
    return f"""
Create a square, photorealistic exhibition photograph of a contemporary artwork
installed in a {setting}.

Artist: {label['artist']}
Artwork: {label['title']}, {label['year']}
Medium: {label['medium']}
Dimensions: {label['dimensions']}
Curatorial interpretation: {label['extended_label']}

Show the mundane object described by the label accurately. Do not replace it
with a fantasy or symbolic object. Let the stated dimensions determine its
visible scale. If the work is monumental, show it occupying the architecture
and include subtle human scale cues. If its dimensions are variable, show a
deliberate repeated or distributed arrangement.

Use restrained museum architecture, realistic shadows, careful gallery
lighting, and professional exhibition-catalogue photography. Do not include
readable labels, logos, watermarks, or references to real artists.
"""


@app.route("/", methods=["GET", "POST"])
def index():
    label = None
    image_url = None
    error = None
    object_description = ""
    setting = "white cube"

    if request.method == "POST":
        object_description = request.form.get("prompt", "").strip()
        setting = request.form.get("setting", "white cube")

        if not object_description:
            error = "Please describe an object before generating the exhibition."
        elif len(object_description) > 500:
            error = "Please keep the object description under 500 characters."
        else:
            try:
                client = get_openai_client()

                # First call: write the label.
                label = generate_label(client, object_description, setting)

                # Second call: derive the image from the label, not raw input.
                image_prompt = build_image_prompt(label, setting)
                image_response = client.images.generate(
                    model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
                    prompt=image_prompt,
                    size="1024x1024",
                    quality="medium",
                    n=1,
                )

                image_base64 = image_response.data[0].b64_json
                image_url = f"data:image/png;base64,{image_base64}"

            except json.JSONDecodeError:
                error = "The wall label was not formatted correctly. Please try again."
            except Exception as exception:
                print(f"Generation error: {exception}")
                error = str(exception)

    return render_template(
        "index.html",
        label=label,
        image_url=image_url,
        error=error,
        prompt=object_description,
        setting=setting,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")

