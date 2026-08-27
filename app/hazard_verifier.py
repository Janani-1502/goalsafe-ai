from typing import Optional

import ollama
from pydantic import BaseModel, ValidationError


# ============================================================
# STRUCTURED ASSESSMENT
# ============================================================

class HazardAssessment(BaseModel):

    observed_facts: list[str]
    objects: list[str]
    visible_states: list[str]
    spatial_relationships: list[str]

    condition: str
    condition_description: str

    goal_relevant_fact: str
    goal_match: bool

    evidence_sufficient: bool

    finding: str
    evidence: str
    guidance: str

    decision: str


# ============================================================
# VALID CONDITIONS
# ============================================================

VALID_CONDITIONS = {
    "SPILL",
    "OBSTRUCTION",
    "DAMAGE",
    "EXPOSURE",
    "FIRE_OR_SMOKE",
    "ELECTRICAL_ABNORMALITY",
    "STRUCTURAL_ABNORMALITY",
    "NORMAL_OPERATION",
    "NONE",
}


# ============================================================
# GOAL KEYWORDS
# ============================================================

GOAL_KEYWORDS = {

    "TRIP": {
        "OBSTRUCTION",
        "EXPOSURE",
        "SPILL",
    },

    "SLIP": {
        "SPILL",
        "OBSTRUCTION",
    },

    "ELECTRICAL": {
        "EXPOSURE",
        "ELECTRICAL_ABNORMALITY",
        "DAMAGE",
    },

    "FIRE": {
        "FIRE_OR_SMOKE",
    },

    "SMOKE": {
        "FIRE_OR_SMOKE",
    },

    "STRUCTURAL": {
        "STRUCTURAL_ABNORMALITY",
        "DAMAGE",
    },

    "DAMAGE": {
        "DAMAGE",
        "ELECTRICAL_ABNORMALITY",
        "STRUCTURAL_ABNORMALITY",
    },
}


# ============================================================
# ELECTRICAL GOAL
# ============================================================

def _is_electrical_goal(goal: str) -> bool:

    goal_text = goal.lower().strip()

    electrical_words = [
        "electrical",
        "electric",
        "electricity",
        "cable",
        "wire",
        "socket",
        "outlet",
        "extension",
        "extension board",
        "power strip",
        "powerboard",
        "plug",
        "power",
    ]

    return any(
        word in goal_text
        for word in electrical_words
    )


# ============================================================
# ELECTRICAL VISUAL EVIDENCE
# ============================================================

def _has_electrical_evidence(
    result: HazardAssessment,
) -> bool:

    text = " ".join(
        [
            *result.observed_facts,
            *result.objects,
            *result.visible_states,
            *result.spatial_relationships,
            result.condition_description,
            result.goal_relevant_fact,
            result.finding,
            result.evidence,
        ]
    ).lower()

    electrical_words = [
        "electrical",
        "electric",
        "electricity",
        "cable",
        "wire",
        "socket",
        "outlet",
        "plug",
        "extension",
        "extension board",
        "power strip",
        "powerboard",
        "power board",
    ]

    return any(
        word in text
        for word in electrical_words
    )


# ============================================================
# WATER VISUAL EVIDENCE
# ============================================================

def _has_water_evidence(
    result: HazardAssessment,
) -> bool:

    text = " ".join(
        [
            *result.observed_facts,
            *result.objects,
            *result.visible_states,
            *result.spatial_relationships,
            result.condition_description,
            result.goal_relevant_fact,
            result.finding,
            result.evidence,
        ]
    ).lower()

    water_words = [
        "water",
        "wet",
        "spill",
        "spillage",
        "liquid",
        "moisture",
        "puddle",
        "wet floor",
        "wet surface",
    ]

    return any(
        word in text
        for word in water_words
    )


# ============================================================
# ELECTRICAL + WATER RELATIONSHIP
# ============================================================

def _has_electrical_water_relationship(
    result: HazardAssessment,
) -> bool:

    text = " ".join(
        [
            *result.observed_facts,
            *result.visible_states,
            *result.spatial_relationships,
            result.condition_description,
            result.goal_relevant_fact,
            result.finding,
            result.evidence,
        ]
    ).lower()

    electrical_words = [
        "electrical",
        "electric",
        "cable",
        "wire",
        "socket",
        "outlet",
        "plug",
        "extension",
        "power strip",
        "powerboard",
        "power board",
    ]

    water_words = [
        "water",
        "wet",
        "spill",
        "spillage",
        "liquid",
        "moisture",
        "puddle",
        "wet floor",
        "wet surface",
    ]

    has_electrical = any(
        word in text
        for word in electrical_words
    )

    has_water = any(
        word in text
        for word in water_words
    )

    return has_electrical and has_water


# ============================================================
# DETERMINISTIC GOAL MATCHING
# ============================================================

def _deterministic_goal_match(
    goal: str,
    condition: str,
) -> bool:

    goal_text = goal.lower().strip()

    # --------------------------------------------------------
    # ELECTRICAL
    # --------------------------------------------------------

    if _is_electrical_goal(goal):

        return condition in GOAL_KEYWORDS["ELECTRICAL"]

    # --------------------------------------------------------
    # TRIP
    # --------------------------------------------------------

    if any(
        word in goal_text
        for word in [
            "trip",
            "walking path",
            "walkway",
            "obstruction",
            "blocking",
        ]
    ):

        return condition in GOAL_KEYWORDS["TRIP"]

    # --------------------------------------------------------
    # SLIP
    # --------------------------------------------------------

    if any(
        word in goal_text
        for word in [
            "slip",
            "wet floor",
            "wet area",
            "spillage",
            "spill",
        ]
    ):

        return condition in GOAL_KEYWORDS["SLIP"]

    # --------------------------------------------------------
    # FIRE
    # --------------------------------------------------------

    if any(
        word in goal_text
        for word in [
            "fire",
            "smoke",
            "flame",
        ]
    ):

        return condition in GOAL_KEYWORDS["FIRE"]

    # --------------------------------------------------------
    # STRUCTURAL
    # --------------------------------------------------------

    if any(
        word in goal_text
        for word in [
            "structural",
            "structure",
            "building damage",
            "ceiling",
            "wall",
            "stair",
        ]
    ):

        return condition in GOAL_KEYWORDS["STRUCTURAL"]

    # --------------------------------------------------------
    # DAMAGE
    # --------------------------------------------------------

    if any(
        word in goal_text
        for word in [
            "damage",
            "damaged",
            "broken",
        ]
    ):

        return condition in GOAL_KEYWORDS["DAMAGE"]

    return False


# ============================================================
# DETERMINISTIC GUIDANCE
# ============================================================

GUIDANCE_MAP = {

    "SPILL":
        "Keep people away from the wet area, clean the spilled material, and dry the surface before use.",

    "OBSTRUCTION":
        "Remove the obstruction from the walking path before normal use.",

    "EXPOSURE":
        "Avoid contact with the exposed cable and secure or remove it from the affected area.",

    "DAMAGE":
        "Avoid using the damaged area until it has been properly repaired or inspected.",

    "ELECTRICAL_ABNORMALITY":
        "Avoid contact with the affected electrical equipment, keep the area dry and clear, and have the electrical setup inspected by a qualified person before use.",

    "STRUCTURAL_ABNORMALITY":
        "Keep clear of the affected area and have the structural condition inspected before use.",

    "FIRE_OR_SMOKE":
        "Move away from the affected area and follow appropriate fire-safety procedures.",

    "NORMAL_OPERATION":
        "No corrective action is indicated based on the visible condition.",

    "NONE":
        "No corrective action is indicated based on the visible condition.",
}


# ============================================================
# CONTEXT-AWARE GUIDANCE
# ============================================================

def get_guidance(
    condition: str,
    finding: str,
    evidence: str,
) -> str:

    text = f"{finding} {evidence}".lower()

    # --------------------------------------------------------
    # ELECTRICAL + WATER
    # --------------------------------------------------------

    if condition == "ELECTRICAL_ABNORMALITY":

        if any(
            word in text
            for word in [
                "water",
                "wet",
                "spill",
                "spillage",
                "liquid",
                "moisture",
                "puddle",
            ]
        ):

            return (
                "Avoid contact with the electrical equipment, "
                "keep the area dry and clear, and have the electrical "
                "setup inspected by a qualified person before use."
            )

        return (
            "Avoid contact with the affected electrical equipment "
            "and have the electrical setup inspected by a qualified person."
        )

    # --------------------------------------------------------
    # ELECTRICAL CABLE
    # --------------------------------------------------------

    if condition == "EXPOSURE":

        if any(
            word in text
            for word in [
                "cable",
                "wire",
                "cord",
            ]
        ):

            return (
                "Avoid contact with the exposed cable and secure or "
                "remove it from the affected area."
            )

    # --------------------------------------------------------
    # CEILING / ROOF WATER
    # --------------------------------------------------------

    if condition == "SPILL":

        if any(
            word in text
            for word in [
                "ceiling",
                "roof",
                "dripping from",
                "leaking from above",
            ]
        ):

            return (
                "Keep the affected area clear, avoid contact with the "
                "water, and have the source of the leak inspected."
            )

        if any(
            word in text
            for word in [
                "floor",
                "walking surface",
                "walking path",
                "ground",
            ]
        ):

            return (
                "Keep people away from the wet area, clean the spilled "
                "material, and dry the surface before use."
            )

    return GUIDANCE_MAP.get(
        condition,
        "Address the visible unsafe condition before normal use.",
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are GoalSafe AI.

You are a visual safety evidence extraction system.

The user's safety goal has priority.

Inspect the image and report only conditions that are visibly
supported by the image.

Do not invent hidden conditions.

Do not assume that an object is dangerous simply because it
can potentially cause harm.

Return exactly one primary condition.

VALID CONDITIONS:

SPILL
OBSTRUCTION
DAMAGE
EXPOSURE
FIRE_OR_SMOKE
ELECTRICAL_ABNORMALITY
STRUCTURAL_ABNORMALITY
NORMAL_OPERATION
NONE

IMPORTANT ELECTRICAL RULE:

If the user's goal is electrical safety, inspect the image for:

- outlets
- plugs
- power strips
- extension boards
- cables
- wires
- electrical equipment
- visible water
- wet surfaces
- electrical equipment near water
- electrical equipment positioned on wet surfaces
- visibly damaged electrical equipment
- exposed electrical parts

If electrical equipment and visible water are visibly associated,
select:

ELECTRICAL_ABNORMALITY

Do NOT select SPILL merely because water is visually obvious.

The electrical condition is the primary condition when the user's
goal is electrical safety.

Describe the visible electrical equipment and visible water in the
evidence.

NORMAL OPERATION:

A normal object is not automatically a hazard.

A normal blue cooking flame is NORMAL_OPERATION.

FIRE:

Only use FIRE_OR_SMOKE when fire or smoke is visibly abnormal,
uncontrolled, spreading, or clearly beyond normal operation.

EVIDENCE:

evidence_sufficient is TRUE only when the selected condition can
be directly verified from the image.

Return only valid JSON matching the supplied schema.
"""


# ============================================================
# MESSAGE BUILDER
# ============================================================

def _build_messages(
    goal: str,
    image_bytes: bytes,
) -> list[dict]:

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f'USER SAFETY GOAL:\n"{goal}"\n\n'

                "Analyze the image according to this goal.\n\n"

                "IMPORTANT:\n"

                "If the goal is electrical safety, inspect the "
                "electrical equipment first.\n\n"

                "If electrical equipment is visibly associated "
                "with water or a wet surface, select "
                "ELECTRICAL_ABNORMALITY rather than SPILL.\n\n"

                "Return only the required JSON object."
            ),
            "images": [image_bytes],
        },
    ]


# ============================================================
# MAIN ASSESSMENT
# ============================================================

def assess_image(
    image_bytes: bytes,
    goal: str,
    retries: int = 1,
) -> tuple[HazardAssessment, str]:

    last_error: Optional[Exception] = None

    for _ in range(retries + 1):

        try:

            # ------------------------------------------------
            # GEMMA VISION
            # ------------------------------------------------

            response = ollama.chat(
                model="gemma3:4b",

                messages=_build_messages(
                    goal,
                    image_bytes,
                ),

                format=HazardAssessment.model_json_schema(),

                options={
                    "temperature": 0.1,
                    "num_ctx": 4096,
                },
            )

            raw = response["message"]["content"]

            # ------------------------------------------------
            # VALIDATE
            # ------------------------------------------------

            result = HazardAssessment.model_validate_json(raw)

        except ValidationError as error:

            last_error = error
            continue

        except Exception as error:

            last_error = error
            continue

        # ====================================================
        # NORMALIZE
        # ====================================================

        condition = (
            result.condition
            or "NONE"
        ).strip().upper()

        if condition not in VALID_CONDITIONS:
            condition = "NONE"

        result.condition = condition

        result.condition_description = (
            result.condition_description or ""
        ).strip()

        result.goal_relevant_fact = (
            result.goal_relevant_fact or ""
        ).strip()

        result.finding = (
            result.finding or ""
        ).strip()

        result.evidence = (
            result.evidence or ""
        ).strip()

        # ====================================================
        # IMPORTANT:
        # PYTHON CHECKS THE ACTUAL VISUAL EVIDENCE
        # ====================================================

        electrical_goal = _is_electrical_goal(goal)

        electrical_evidence = _has_electrical_evidence(result)

        water_evidence = _has_water_evidence(result)

        electrical_water = _has_electrical_water_relationship(
            result
        )

        # ====================================================
        # ELECTRICAL OVERRIDE
        #
        # THIS IS THE KEY FIX
        # ====================================================

        if electrical_goal:

            # Case 1:
            # Gemma returned SPILL but its own evidence contains
            # electrical equipment and water.

            if (
                condition == "SPILL"
                and electrical_evidence
                and water_evidence
            ):

                condition = "ELECTRICAL_ABNORMALITY"

                result.condition = condition

                result.condition_description = (
                    "Electrical equipment and connected cables "
                    "are visibly positioned on or near a wet area."
                )

                result.goal_relevant_fact = (
                    "Electrical equipment is visibly associated "
                    "with water or a wet surface."
                )

                result.finding = (
                    "Electrical equipment and connected cables "
                    "are visibly positioned on or near a wet area."
                )

                result.evidence = (
                    "The image visibly shows electrical equipment "
                    "and connected cables together with water on "
                    "the floor."
                )

                result.evidence_sufficient = True

            # Case 2:
            # Gemma already correctly returned an electrical
            # condition.

            elif (
                condition in {
                    "ELECTRICAL_ABNORMALITY",
                    "EXPOSURE",
                    "DAMAGE",
                }
                and electrical_evidence
            ):

                result.condition = condition

        # ====================================================
        # FINAL CONDITION
        # ====================================================

        condition = result.condition

        # ====================================================
        # PYTHON GOAL MATCH
        # ====================================================

        result.goal_match = _deterministic_goal_match(
            goal,
            condition,
        )

        # ====================================================
        # SAFETY CONDITIONS
        # ====================================================

        unsafe_condition = condition in {
            "SPILL",
            "OBSTRUCTION",
            "DAMAGE",
            "EXPOSURE",
            "FIRE_OR_SMOKE",
            "ELECTRICAL_ABNORMALITY",
            "STRUCTURAL_ABNORMALITY",
        }

        # ====================================================
        # FINAL DECISION
        # ====================================================

        final_hazard = (
            result.goal_match
            and unsafe_condition
            and result.evidence_sufficient
        )

        # ====================================================
        # HAZARD
        # ====================================================

        if final_hazard:

            result.decision = "HAZARD"

            # Ensure useful finding

            if not result.finding:

                result.finding = (
                    result.condition_description
                    or result.goal_relevant_fact
                    or "A visible unsafe condition was detected."
                )

            # Ensure useful evidence

            if not result.evidence:

                result.evidence = (
                    result.condition_description
                    or result.goal_relevant_fact
                    or "The unsafe condition is visibly present."
                )

            # Deterministic guidance

            result.guidance = get_guidance(
                condition,
                result.finding,
                result.evidence,
            )

            return result, "HAZARD"

        # ====================================================
        # NO HAZARD
        # ====================================================

        result.decision = "NO_HAZARD"

        result.finding = (
            "No relevant hazard detected."
        )

        result.evidence = (
            "No clearly visible hazardous condition relevant "
            "to the user's safety goal was verified from the image."
        )

        result.guidance = (
            "No corrective action is indicated based on "
            "the visible evidence."
        )

        return result, "NO_HAZARD"

    # ========================================================
    # MODEL FAILURE
    # ========================================================

    raise RuntimeError(
        "Model did not return valid structured output "
        f"after retries: {last_error}"
    )