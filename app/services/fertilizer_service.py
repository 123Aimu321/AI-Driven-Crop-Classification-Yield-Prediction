ALLOWED_CROPS = {
    "wheat",
    "rice",
    "ragi",
}


CROP_GUIDANCE = {
    "wheat": {
        "primary_nutrient": "Nitrogen",
        "fertilizer_focus": [
            "Nitrogen-containing fertilizer",
            "Phosphorus-containing fertilizer",
            "Potassium-containing fertilizer",
        ],
        "guidance": (
            "Wheat generally requires balanced "
            "nitrogen, phosphorus and potassium "
            "management throughout the crop cycle."
        ),
    },

    "rice": {
        "primary_nutrient": "Nitrogen",
        "fertilizer_focus": [
            "Nitrogen-containing fertilizer",
            "Phosphorus-containing fertilizer",
            "Potassium-containing fertilizer",
        ],
        "guidance": (
            "Rice generally requires balanced "
            "nutrient management, with particular "
            "attention to nitrogen during crop growth."
        ),
    },

    "ragi": {
        "primary_nutrient": "Nitrogen and Phosphorus",
        "fertilizer_focus": [
            "Nitrogen-containing fertilizer",
            "Phosphorus-containing fertilizer",
            "Potassium-containing fertilizer",
        ],
        "guidance": (
            "Ragi requires balanced nutrient "
            "management, with nitrogen and phosphorus "
            "being important considerations."
        ),
    },
}


def recommend_fertilizer(
    crop,
    state=None,
):
    """
    Provides crop-level fertilizer guidance.

    This does not calculate an exact fertilizer dose.
    Exact fertilizer requirements require soil testing
    and local agronomic recommendations.
    """

    crop = (
        str(crop)
        .strip()
        .lower()
    )

    if crop not in ALLOWED_CROPS:
        raise ValueError(
            "Unsupported crop. "
            "Only Wheat, Rice and Ragi "
            "are supported."
        )

    guidance = CROP_GUIDANCE[crop]

    return {
        "success": True,

        "crop": crop.title(),

        "state": state,

        "primary_nutrient_focus": (
            guidance["primary_nutrient"]
        ),

        "fertilizer_focus": (
            guidance["fertilizer_focus"]
        ),

        "guidance": guidance["guidance"],

        "recommendation_type": (
            "Crop-level guidance"
        ),

        "notice": (
            "This system does not calculate an "
            "exact fertilizer dose because automatic "
            "soil N, P, K and pH measurements are "
            "not available. Use a soil test and local "
            "agronomic recommendation before applying "
            "fertilizer."
        ),
    }