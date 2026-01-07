import json

def explain_simplified(concept: str):
    """
    Produce a structured, simple explanation of a complex concept
    using the Ladder of Abstraction:
    1. Analogy
    2. Simple explanation
    3. Technical definition
    """

    analogy = (
        f"Think of '{concept}' like a familiar everyday situation that helps "
        f"illustrate how it works."
    )

    simple_explanation = (
        f"In simple terms, '{concept}' is a concept that can be understood by "
        f"breaking it down into its basic purpose or behavior."
    )

    technical_definition = (
        f"Formally, '{concept}' refers to a more precise or structured idea "
        f"used in technical or academic contexts."
    )

    return {
        "concept": concept,
        "analogy": analogy,
        "simple_explanation": simple_explanation,
        "technical_definition": technical_definition
    }
