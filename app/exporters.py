from pathlib import Path

from fpdf import FPDF

from app.config import EXPORTS_DIR


# ============================================================
# CLEAN TEXT FOR FPDF
# ============================================================

def _clean_text(text: str) -> str:
    """
    Convert text into a form that FPDF can safely render.
    """

    if text is None:
        return ""

    text = str(text)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "-",
        "\u2728": "*",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove characters outside basic Latin
    text = text.encode(
        "latin-1",
        errors="replace"
    ).decode("latin-1")

    return text


# ============================================================
# SAFE MULTI-CELL
# ============================================================

def _safe_multicell(
    pdf: FPDF,
    text: str,
):
    """
    Safely render text without causing
    'Not enough horizontal space' errors.
    """

    text = _clean_text(text)

    if not text.strip():
        return

    # Make sure we are not sitting at an invalid position.
    pdf.set_x(pdf.l_margin)

    # Use full available width.
    width = (
        pdf.w
        - pdf.l_margin
        - pdf.r_margin
    )

    if width <= 0:
        width = 170

    pdf.multi_cell(
        width,
        7,
        text,
        border=0,
        align="L",
    )


# ============================================================
# SAVE COMIC AS PDF
# ============================================================

def save_pdf(
    layout,
    title: str = "ComicCraft Comic",
) -> str:

    # --------------------------------------------------------
    # Create exports directory
    # --------------------------------------------------------

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Create PDF
    # --------------------------------------------------------

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        20,
    )

    pdf.cell(
        0,
        12,
        _clean_text(title),
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )

    pdf.ln(5)

    # --------------------------------------------------------
    # Panels
    # --------------------------------------------------------

    for index, item in enumerate(layout):

        image_path = Path(
            item["image_path"]
        )

        narration = _clean_text(
            item.get(
                "narration",
                "",
            )
        )

        dialogue = _clean_text(
            item.get(
                "dialogue",
                "",
            )
        )

        panel_number = item.get(
            "panel_number",
            index + 1,
        )

        # ----------------------------------------------------
        # Panel heading
        # ----------------------------------------------------

        pdf.set_font(
            "Helvetica",
            "B",
            13,
        )

        pdf.cell(
            0,
            8,
            f"Panel {panel_number}",
            new_x="LMARGIN",
            new_y="NEXT",
        )

        # ----------------------------------------------------
        # Panel image
        # ----------------------------------------------------

        if image_path.exists():

            image_width = 170

            image_height = 105

            pdf.image(
                str(image_path),
                x=20,
                y=pdf.get_y(),
                w=image_width,
                h=image_height,
            )

            pdf.set_y(
                pdf.get_y()
                + image_height
                + 5
            )

        # ----------------------------------------------------
        # Narration
        # ----------------------------------------------------

        if narration:

            pdf.set_font(
                "Helvetica",
                "B",
                10,
            )

            pdf.cell(
                0,
                7,
                "Narration:",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            _safe_multicell(
                pdf,
                narration,
            )

            pdf.ln(2)

        # ----------------------------------------------------
        # Dialogue
        # ----------------------------------------------------

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                10,
            )

            pdf.cell(
                0,
                7,
                "Dialogue:",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            pdf.set_font(
                "Helvetica",
                "",
                10,
            )

            _safe_multicell(
                pdf,
                dialogue,
            )

        # ----------------------------------------------------
        # Space after panel
        # ----------------------------------------------------

        pdf.ln(5)

    # --------------------------------------------------------
    # Create unique PDF filename
    # --------------------------------------------------------

    safe_title = _clean_text(
        title
    )

    safe_title = (
        safe_title
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    pdf_path = (
        EXPORTS_DIR
        / f"{safe_title}.pdf"
    )

    # --------------------------------------------------------
    # Save PDF
    # --------------------------------------------------------

    pdf.output(
        str(pdf_path)
    )

    return str(pdf_path)