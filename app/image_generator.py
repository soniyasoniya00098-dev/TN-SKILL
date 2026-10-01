import base64

from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_IMAGE_MODEL,
    PANELS_DIR,
    MOCK_AI,
)


# ============================================================
# GEMINI IMAGE GENERATION
# ============================================================

def _generate_gemini_image(
    prompt: str,
    panel_number: int,
) -> str:

    print(
        f"Generating Gemini AI image for panel "
        f"{panel_number}..."
    )

    print(
        f"Image model: {GEMINI_IMAGE_MODEL}"
    )

    # --------------------------------------------------------
    # Check API key
    # --------------------------------------------------------

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in .env"
        )

    # --------------------------------------------------------
    # Gemini client
    # --------------------------------------------------------

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    # --------------------------------------------------------
    # Image prompt
    # --------------------------------------------------------

    final_prompt = f"""
Create a high-quality comic-book illustration.

Scene:
{prompt}

Visual requirements:

- colorful comic book illustration
- cinematic lighting
- detailed characters
- expressive faces
- fantasy adventure atmosphere
- professional digital artwork
- vibrant colors
- clear composition
- consistent character appearance
- detailed fantasy environment
- suitable for a children's fantasy comic
- no captions
- no speech bubbles
- no text
- no watermark
"""

    # --------------------------------------------------------
    # Generate image
    # --------------------------------------------------------

    interaction = client.interactions.create(
        model=GEMINI_IMAGE_MODEL,
        input=final_prompt,
        response_format={
            "type": "image",
            "mime_type": "image/jpeg",
            "aspect_ratio": "3:2",
            "image_size": "1K",
        },
    )

    # --------------------------------------------------------
    # Check response
    # --------------------------------------------------------

    if not interaction.output_image:
        output_text = getattr(
            interaction,
            "output_text",
            "",
        )

        raise RuntimeError(
            "Gemini returned no image.\n"
            f"Output: {output_text}"
        )

    # --------------------------------------------------------
    # Decode image
    # --------------------------------------------------------

    image_data = interaction.output_image.data

    if not image_data:
        raise RuntimeError(
            "Gemini returned empty image data."
        )

    image_bytes = base64.b64decode(
        image_data
    )

    # --------------------------------------------------------
    # Create panels directory
    # --------------------------------------------------------

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Save JPEG image
    # --------------------------------------------------------

    output_path = (
        PANELS_DIR
        / f"panel_{int(panel_number)}.jpg"
    )

    with open(
        output_path,
        "wb",
    ) as image_file:

        image_file.write(
            image_bytes
        )

    print(
        f"Image saved: {output_path}"
    )

    return str(output_path)


# ============================================================
# PLACEHOLDER IMAGE
# ============================================================

def _create_placeholder(
    prompt: str,
    panel_number: int,
) -> str:

    from PIL import Image, ImageDraw

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        PANELS_DIR
        / f"panel_{int(panel_number)}.jpg"
    )

    width = 768
    height = 512

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        [10, 10, width - 10, height - 10],
        outline="black",
        width=3,
    )

    draw.text(
        (30, 30),
        f"COMIC PANEL {panel_number}",
        fill="black",
    )

    draw.text(
        (30, 80),
        prompt[:500],
        fill="black",
    )

    image.save(
        output_path,
        "JPEG",
    )

    print(
        f"Placeholder image saved: {output_path}"
    )

    return str(output_path)


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def generate_image(
    prompt: str,
    panel_number: int = 1,
) -> str:

    panel_number = int(
        panel_number
    )

    # --------------------------------------------------------
    # Mock mode
    # --------------------------------------------------------

    if MOCK_AI:

        print(
            "MOCK_AI=true - "
            "using placeholder image."
        )

        return _create_placeholder(
            prompt,
            panel_number,
        )

    # --------------------------------------------------------
    # Real Gemini image generation
    # --------------------------------------------------------

    return _generate_gemini_image(
        prompt,
        panel_number,
    )