from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
)

from app.config import BASE_DIR

from app.exporters import save_pdf

from app.gemini_flash import (
    generate_outline,
)

from app.gemini_pro import (
    generate_story,
)

from app.image_generator import (
    generate_image,
)

from app.layout_builder import (
    build_comic_layout,
)

from app.schemas import (
    PromptRequest,
)


router = APIRouter()


# ============================================================
# CONVERT LOCAL PATH TO WEB PATH
# ============================================================

def _web_path(absolute_path: str) -> str:

    path = Path(absolute_path)

    try:

        relative = path.relative_to(
            BASE_DIR / "static"
        )

        return (
            "/static/"
            + relative.as_posix()
        )

    except ValueError:

        return ""


# ============================================================
# COMPLETE COMIC GENERATION PIPELINE
# ============================================================

def _generate_comic(
    payload: PromptRequest,
):

    # --------------------------------------------------------
    # STEP 1 - Generate outline
    # --------------------------------------------------------

    outline = generate_outline(
        payload.story_prompt,
        payload.character_name,
        payload.setting,
        payload.tone,
        payload.art_style,
    )

    # --------------------------------------------------------
    # STEP 2 - Generate story
    # --------------------------------------------------------

    story = generate_story(
        outline,
        payload.character_name,
        payload.tone,
    )

    # --------------------------------------------------------
    # STEP 3 - Generate images
    # --------------------------------------------------------

    image_paths = []

    for panel in story.panels:

        image_path = generate_image(
            panel.image_prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(
            image_path
        )

    # --------------------------------------------------------
    # STEP 4 - Build layout
    # --------------------------------------------------------

    layout = build_comic_layout(
        story,
        image_paths,
    )

    # --------------------------------------------------------
    # STEP 5 - Generate PDF
    # --------------------------------------------------------

    pdf_path = save_pdf(
        layout,
        title=(
            f"{payload.character_name}'s Comic"
        ),
    )

    # --------------------------------------------------------
    # STEP 6 - Convert image paths to URLs
    # --------------------------------------------------------

    public_layout = []

    for item in layout:

        public_item = dict(item)

        public_item["image_path"] = (
            _web_path(
                item["image_path"]
            )
        )

        public_layout.append(
            public_item
        )

    return (
        public_layout,
        pdf_path,
    )


# ============================================================
# HOME PAGE
# ============================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):

    return (
        request.app.state.templates.TemplateResponse(
            request=request,
            name="index.html",
            context={},
        )
    )


# ============================================================
# FORM GENERATION ROUTE
# ============================================================

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        # ----------------------------------------------------
        # Create request payload
        # ----------------------------------------------------

        payload = PromptRequest(

            story_prompt=story_prompt,

            character_name=character_name,

            setting=setting,

            tone=tone,

            art_style=art_style,
        )

        # ----------------------------------------------------
        # Run complete comic generation
        # ----------------------------------------------------

        layout, pdf_path = _generate_comic(
            payload
        )

        # ----------------------------------------------------
        # Convert PDF path to URL
        # ----------------------------------------------------

        pdf_url = _web_path(
            pdf_path
        )

        # ----------------------------------------------------
        # Show comic preview
        # ----------------------------------------------------

        return (
            request.app.state.templates.TemplateResponse(

                request=request,

                name="comic_preview.html",

                context={

                    "layout": layout,

                    "pdf_url": pdf_url,

                    "character_name":
                        payload.character_name,
                },
            )
        )

    except Exception as exc:

        # ====================================================
        # IMPORTANT DEBUG INFORMATION
        # ====================================================

        import traceback

        print("\n")
        print("=" * 70)
        print("COMIC GENERATION ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70)
        print("\n")

        # ----------------------------------------------------
        # Show error on browser
        # ----------------------------------------------------

        return (
            request.app.state.templates.TemplateResponse(

                request=request,

                name="index.html",

                context={
                    "error": str(exc)
                },

                status_code=500,
            )
        )


# ============================================================
# JSON API
# ============================================================

@router.post(
    "/generate-comic/json"
)
async def generate_json(
    payload: PromptRequest,
):

    try:

        layout, pdf_path = (
            _generate_comic(
                payload
            )
        )

        return JSONResponse(

            {
                "success": True,

                "character_name":
                    payload.character_name,

                "panels":
                    layout,

                "pdf_path":
                    _web_path(pdf_path),
            }
        )

    except Exception as exc:

        import traceback

        print("\n")
        print("=" * 70)
        print("JSON COMIC GENERATION ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70)
        print("\n")

        raise HTTPException(

            status_code=500,

            detail=str(exc),

        ) from exc


# ============================================================
# EXPORT SUCCESS PAGE
# ============================================================

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(

    request: Request,

    pdf_path: str = "",
):

    return (
        request.app.state.templates.TemplateResponse(

            request=request,

            name="export_success.html",

            context={
                "pdf_path": pdf_path
            },
        )
    )


# ============================================================
# TEST IMAGE
# ============================================================

@router.get(
    "/test-image",
    response_class=JSONResponse,
)
async def test_image(

    prompt: str =
        "A brave fox exploring "
        "an enchanted forest, "
        "comic book style",
):

    try:

        path = generate_image(

            prompt,

            panel_number=1,
        )

        return {

            "success": True,

            "image_path":
                _web_path(path),
        }

    except Exception as exc:

        import traceback

        print("\n")
        print("=" * 70)
        print("IMAGE GENERATION ERROR")
        print("=" * 70)

        traceback.print_exc()

        print("=" * 70)
        print("\n")

        raise HTTPException(

            status_code=500,

            detail=str(exc),

        ) from exc


# ============================================================
# DOWNLOAD PDF
# ============================================================

@router.get(
    "/download"
)
async def download(
    pdf_path: str,
):

    # --------------------------------------------------------
    # Security:
    # only allow files inside static/exports
    # --------------------------------------------------------

    exports_dir = (
        BASE_DIR
        / "static"
        / "exports"
    ).resolve()

    requested = (
        BASE_DIR
        / pdf_path.lstrip("/")
    ).resolve()

    if (
        exports_dir not in requested.parents
        or requested == exports_dir
    ):

        raise HTTPException(

            status_code=400,

            detail="Invalid export path.",
        )

    if not requested.exists():

        raise HTTPException(

            status_code=404,

            detail="PDF not found.",
        )

    return FileResponse(

        requested,

        media_type="application/pdf",

        filename=requested.name,
    )