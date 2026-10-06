from datetime import datetime


def create_emergency_alert(
    user_name,
    location,
    emergency_type="SOS"
):
    """
    Creates an emergency alert message.
    """

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    message = f"""
🚨 SAFEHER AI EMERGENCY ALERT 🚨

Emergency Type: {emergency_type}

User: {user_name}

Time: {current_time}

Location:
{location}

The user may require immediate assistance.

Please contact the user or emergency services
if necessary.
"""

    return message


def prepare_sms_alert(
    user_name,
    phone,
    location,
    emergency_type="SOS"
):
    """
    Prepares an SMS-ready emergency message.
    """

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    sms_message = (
        f"🚨 SAFEHER AI EMERGENCY ALERT 🚨\n\n"
        f"Emergency: {emergency_type}\n"
        f"User: {user_name}\n"
        f"Time: {current_time}\n"
        f"Location: {location}\n\n"
        f"Please contact the user immediately "
        f"or call emergency services if necessary."
    )

    return {
        "phone": phone,
        "message": sms_message,
        "time": current_time
    }