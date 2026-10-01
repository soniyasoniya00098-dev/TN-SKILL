import json
import time

from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    MOCK_AI,
)

from app.schemas import ComicOutline


# ============================================================
# GEMINI CLIENT
# ============================================================

client = None

if not MOCK_AI:

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env"
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# TEXT MODELS
# ============================================================

TEXT_MODELS = [
    GEMINI_OUTLINE_MODEL,
]

TEXT_MODELS = list(
    dict.fromkeys(TEXT_MODELS)
)


# ============================================================
# CLEAN GEMINI JSON
# ============================================================

def _clean_json_text(text: str) -> str:

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


# ============================================================
# MOCK OUTLINE
# ============================================================

def _create_mock_outline(
    prompt: str,
    character: str = "",
    setting: str = "",
    tone: str = "",
    art_style: str = "",
) -> ComicOutline:

    print("=" * 50)
    print("MOCK_AI=true")
    print("Skipping Gemini outline generation.")
    print("Creating local 5-panel comic outline...")
    print("=" * 50)

    character = character.strip() if character else "Maya"
    setting = setting.strip() if setting else "a floating fantasy kingdom"
    tone = tone.strip() if tone else "adventure and fantasy"
    art_style = art_style.strip() if art_style else "colorful comic book"

    panels = [
        {
            "panel_number": 1,
            "title": "The Magical Discovery",
            "scene_description": (
                f"{character} discovers a mysterious glowing book "
                f"in an old magical library. The book begins to glow "
                f"and opens a magical portal."
            ),
            "image_prompt": (
                f"{character} discovering a mysterious glowing magical book "
                f"in an ancient fantasy library, magical blue light, "
                f"glowing particles, surprised expression, cinematic "
                f"composition, {art_style}, detailed fantasy illustration"
            ),
        },
        {
            "panel_number": 2,
            "title": "The Floating Kingdom",
            "scene_description": (
                f"{character} is transported through the magical portal "
                f"and arrives in {setting}. Beautiful floating islands "
                f"and castles surround the character."
            ),
            "image_prompt": (
                f"{character} standing in {setting}, floating islands, "
                f"beautiful magical castles in the clouds, glowing sky, "
                f"fantasy landscape, colorful atmosphere, "
                f"{art_style}, detailed comic illustration"
            ),
        },
        {
            "panel_number": 3,
            "title": "Meeting Spark",
            "scene_description": (
                f"{character} meets Spark, a small friendly glowing dragon "
                f"who explains that the kingdom is facing a mysterious problem."
            ),
            "image_prompt": (
                f"{character} meeting Spark, a small cute friendly glowing "
                f"dragon with bright magical light, fantasy kingdom in "
                f"the background, warm friendship scene, expressive faces, "
                f"{art_style}, detailed comic illustration"
            ),
        },
        {
            "panel_number": 4,
            "title": "The Great Challenge",
            "scene_description": (
                f"{character} and Spark travel through an enchanted forest "
                f"and face a dangerous shadow creature protecting the "
                f"missing Crystal of Light."
            ),
            "image_prompt": (
                f"{character} and Spark facing a mysterious shadow creature "
                f"in an enchanted fantasy forest, glowing Crystal of Light, "
                f"dramatic lighting, magical trees, action scene, "
                f"adventure atmosphere, {art_style}, detailed comic artwork"
            ),
        },
        {
            "panel_number": 5,
            "title": "A Happy Ending",
            "scene_description": (
                f"{character} discovers that the shadow creature is lonely "
                f"rather than evil. Through kindness, the Crystal of Light "
                f"is restored and the kingdom becomes bright again."
            ),
            "image_prompt": (
                f"{character} and Spark restoring a glowing Crystal of Light "
                f"while a friendly shadow creature watches peacefully, "
                f"magical kingdom glowing brightly in the background, "
                f"happy emotional ending, colorful fantasy atmosphere, "
                f"{art_style}, beautiful detailed comic illustration"
            ),
        },
    ]

    try:
        outline = ComicOutline.model_validate(
            {
                "title": "Maya and Spark's Magical Adventure",
                "panels": panels,
            }
        )

        print(f"Mock outline created successfully: {len(outline.panels)} panels")
        print("=" * 50)

        return outline

    except Exception as exc:
        raise RuntimeError(
            f"Failed to create mock ComicOutline: {exc}"
        ) from exc

    print(
        f"Mock outline created successfully: "
        f"{len(outline.panels)} panels"
    )

    return outline


# ============================================================
# GEMINI OUTLINE
# ============================================================

def _generate_gemini_outline(
    prompt: str,
    character: str = "",
    setting: str = "",
    tone: str = "",
    art_style: str = "",
) -> ComicOutline:

    full_prompt = f"""
Create a five-panel comic outline.

Story prompt:
{prompt}

Character:
{character}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Create EXACTLY 5 panels.

For every panel provide:

- panel_number
- title
- scene_description

The scene_description must clearly describe:

- characters
- environment
- action
- important visual details
- emotions
- objects needed for the illustration

Return ONLY valid JSON.

Do NOT use Markdown.
Do NOT use code fences.
Do NOT add explanations.

Use exactly this structure:

{{
    "title": "Comic title",
    "panels": [
        {{
            "panel_number": 1,
            "title": "Panel title",
            "scene_description": "Detailed scene"
        }},
        {{
            "panel_number": 2,
            "title": "Panel title",
            "scene_description": "Detailed scene"
        }},
        {{
            "panel_number": 3,
            "title": "Panel title",
            "scene_description": "Detailed scene"
        }},
        {{
            "panel_number": 4,
            "title": "Panel title",
            "scene_description": "Detailed scene"
        }},
        {{
            "panel_number": 5,
            "title": "Panel title",
            "scene_description": "Detailed scene"
        }}
    ]
}}
"""

    last_error = None

    for model_name in TEXT_MODELS:

        print(
            f"Trying Gemini outline model: "
            f"{model_name}"
        )

        for attempt in range(1, 4):

            try:

                print(
                    f"Outline attempt "
                    f"{attempt}/3..."
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                )

                if not response:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                response_text = getattr(
                    response,
                    "text",
                    None,
                )

                if not response_text:

                    raise RuntimeError(
                        "Gemini returned no text."
                    )

                cleaned_text = _clean_json_text(
                    response_text
                )

                data = json.loads(
                    cleaned_text
                )

                outline = ComicOutline.model_validate(
                    data
                )

                if len(outline.panels) != 5:

                    raise RuntimeError(
                        "Gemini returned "
                        f"{len(outline.panels)} panels. "
                        "Exactly 5 panels are required."
                    )

                print(
                    "Gemini outline generated successfully."
                )

                return outline

            except Exception as exc:

                last_error = exc

                print(
                    f"Gemini outline error: "
                    f"{model_name}, "
                    f"attempt {attempt}/3: "
                    f"{exc}"
                )

                if attempt < 3:

                    wait_seconds = 2 * attempt

                    print(
                        f"Retrying in "
                        f"{wait_seconds} seconds..."
                    )

                    time.sleep(
                        wait_seconds
                    )

    raise RuntimeError(
        "Gemini outline generation failed. "
        f"Last error: {last_error}"
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def generate_outline(
    prompt: str,
    character: str = "",
    setting: str = "",
    tone: str = "",
    art_style: str = "",
) -> ComicOutline:

    # --------------------------------------------------------
    # MOCK MODE
    # --------------------------------------------------------

    if MOCK_AI:

        return _create_mock_outline(
            prompt=prompt,
            character=character,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

    # --------------------------------------------------------
    # REAL GEMINI MODE
    # --------------------------------------------------------

    return _generate_gemini_outline(
        prompt=prompt,
        character=character,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )