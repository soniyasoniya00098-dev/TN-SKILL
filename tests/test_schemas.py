from app.schemas import PromptRequest


def test_prompt_request_accepts_valid_input():

    data = PromptRequest(

        story_prompt=(
            "A fox explores "
            "a magical forest."
        ),

        character_name="Luna",

        setting="Forest",

        tone="Funny",

        art_style="Comic Book",
    )


    assert (
        data.character_name
        == "Luna"
    )