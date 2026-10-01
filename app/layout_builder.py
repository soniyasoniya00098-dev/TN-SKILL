from pathlib import Path


def build_comic_layout(story, image_paths):

    layout = []

    for index, panel in enumerate(story.panels):

        image_path = Path(
            image_paths[index]
        )

        layout.append(
            {
                "panel_number": panel.panel_number,

                "title": getattr(
                    panel,
                    "title",
                    f"Panel {panel.panel_number}",
                ),

                "narration": panel.narration,

                "dialogue": panel.dialogue,

                "image_prompt": panel.image_prompt,

                # Keep the real filesystem path
                "image_path": str(
                    image_path.resolve()
                ),
            }
        )

    return layout