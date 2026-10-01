# ComicCraft - AI Comic Story Creator

ComicCraft is an AI-powered web application that converts a user's story idea into a five-panel comic.

The application uses:

- FastAPI
- Jinja2
- Google Gemini
- Hugging Face
- Stable Diffusion
- Pillow
- FPDF2
- Pydantic

---

# PROJECT STRUCTURE

```text
ComicCraft/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_flash.pys
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
│
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── panels/
│   └── exports/
│
├── tests/
│   ├── test_schemas.py
│   └── test_routes.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md