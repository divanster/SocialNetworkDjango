# backend/utils/group_names.py

def get_user_group_name(user_id):
    """
    Generate the WebSocket group name for a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        str: The generated group name.
    """
    return f"user_{user_id}"


def get_general_group_name():
    """
    Generate a general WebSocket group name.

    Returns:
        str: The general group name.
    """
    return "general"
