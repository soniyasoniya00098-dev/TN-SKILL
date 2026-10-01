from pydantic import ValidationError

from app.config import (
    GEMINI_API_KEY,
    GEMINI_STORY_MODEL,
    MOCK_AI,
)

from app.schemas import (
    ComicOutline,
    ComicStory,
)


# ============================================================
# MOCK STORY
# ============================================================

def _mock_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
) -> ComicStory:

    panels = []

    for panel in outline.panels:

        panels.append(
            {
                "panel_number": panel.panel_number,

                "title": panel.title,

                "scene_description":
                    panel.scene_description,

                "caption":
                    f"[Panel {panel.panel_number}] "
                    f"The story moves forward.",

                "narration":
                    f"{character_name} takes another step, "
                    f"determined to face what comes next.",

                "dialogue":
                    f"{character_name}: "
                    f"Let's see where this leads!",

                "image_prompt":
                    panel.image_prompt,
            }
        )

    return ComicStory(
        panels=panels
    )


# ============================================================
# STORY GENERATOR
# ============================================================

def generate_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
) -> ComicStory:

    # --------------------------------------------------------
    # MOCK MODE
    # --------------------------------------------------------

    if MOCK_AI:

        return _mock_story(
            outline,
            character_name,
            tone,
        )


    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured. "
            "Add it to .env or set MOCK_AI=true."
        )


    # Lazy import
    from google import genai
    from google.genai import types


    # --------------------------------------------------------
    # CLIENT
    # --------------------------------------------------------

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


    # --------------------------------------------------------
    # OUTLINE JSON
    # --------------------------------------------------------

    outline_json = outline.model_dump_json(
        indent=2
    )


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = f"""
Expand the following comic outline into a polished
comic book script.

MAIN CHARACTER:
{character_name}

TONE:
{tone}

OUTLINE:

{outline_json}

For every panel create:

- panel_number
- title
- scene_description
- caption
- narration
- dialogue
- image_prompt

Rules:

1. Do not change the panel count.

2. Keep character identity consistent.

3. Keep the setting consistent.

4. Make the story flow naturally from panel to panel.

5. Caption should be short.

6. Narration should be concise and suitable for comics.

7. Dialogue should sound natural.

8. Image prompt should preserve visual continuity.

9. Do not add unnecessary panels.

10. Return only structured data.
"""


    # --------------------------------------------------------
    # GEMINI REQUEST
    # --------------------------------------------------------

    response = client.models.generate_content(

        model=GEMINI_STORY_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.85,

            response_mime_type="application/json",

            response_schema=ComicStory,
        ),
    )


    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    try:

        return ComicStory.model_validate_json(
            response.text
        )

    except (
        ValidationError,
        ValueError,
        TypeError,
    ) as exc:

        raise RuntimeError(
            f"Gemini returned an invalid story: {exc}"
        ) from exc