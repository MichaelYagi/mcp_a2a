import json

def concept_contextualizer(concept: str):
    """
    Provide big-picture context for a concept:
    - Why it matters
    - What problem it solves
    - How it fits into a larger system
    - Related concepts
    """

    return {
        "concept": concept,
        "why_it_matters": (
            f"'{concept}' is important because it addresses a meaningful need "
            f"or challenge within its domain."
        ),
        "problem_it_solves": (
            f"'{concept}' exists to solve a specific problem or limitation "
            f"that earlier approaches could not handle effectively."
        ),
        "how_it_fits_in": (
            f"'{concept}' is part of a broader system or framework, interacting "
            f"with other components to achieve a larger goal."
        ),
        "related_concepts": [
            f"{concept} (foundational idea)",
            f"{concept} (applied use case)",
            f"{concept} (adjacent field)"
        ]
    }
