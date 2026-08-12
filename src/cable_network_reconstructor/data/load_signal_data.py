def get_test_case(model_name):
    """
    Get test case from database.

    Args:
        model_name: Name of the model

    Returns:
        Test case data
    """
    from .sql_interface import SQLInterface

    dbi = SQLInterface("database.db")
    test_case = dbi.get_test_case(model_name)
    dbi.close_db()
    return test_case


def circular_translate(lst, shift):
    """
    Circularly translate a list by shift positions.

    Args:
        lst: List to translate
        shift: Number of positions to shift

    Returns:
        Translated list
    """
    n = len(lst)
    shift = shift % n  # Ensure the shift is within the vector length
    return lst[-shift:] + lst[:-shift]
