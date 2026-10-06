import pandas as pd
from sklearn.tree import DecisionTreeClassifier


# =========================================================
# TRAINING DATA
# =========================================================

data = {
    "night": [
        0, 0, 0, 1, 1,
        1, 1, 1, 0, 1,
        0, 1
    ],

    "alone": [
        0, 1, 0, 1, 1,
        1, 0, 1, 1, 0,
        1, 1
    ],

    "following": [
        0, 0, 0, 0, 1,
        1, 1, 1, 0, 0,
        1, 1
    ],

    "unfamiliar_area": [
        0, 0, 1, 1, 1,
        1, 0, 1, 1, 0,
        1, 1
    ],

    "low_battery": [
        0, 1, 0, 0, 0,
        1, 1, 0, 1, 0,
        1, 0
    ],

    "risk": [
        0, 1, 1, 1, 2,
        2, 2, 2, 1, 0,
        2, 2
    ]
}


df = pd.DataFrame(data)


# =========================================================
# MODEL
# =========================================================

X = df[
    [
        "night",
        "alone",
        "following",
        "unfamiliar_area",
        "low_battery"
    ]
]

y = df["risk"]


model = DecisionTreeClassifier(
    random_state=42
)

model.fit(X, y)


# =========================================================
# PREDICTION FUNCTION
# =========================================================

def predict_safety_risk(
    night,
    alone,
    following,
    unfamiliar_area,
    low_battery
):

    input_data = pd.DataFrame(
        [
            {
                "night": int(night),
                "alone": int(alone),
                "following": int(following),
                "unfamiliar_area": int(unfamiliar_area),
                "low_battery": int(low_battery)
            }
        ]
    )

    prediction = model.predict(
        input_data
    )[0]

    if prediction == 0:

        return (
            "LOW RISK",
            "🟢",
            "The current situation appears relatively safe. "
            "Stay aware of your surroundings."
        )

    elif prediction == 1:

        return (
            "MEDIUM RISK",
            "🟡",
            "Be careful and stay connected with someone "
            "you trust. Avoid isolated areas."
        )

    else:

        return (
            "HIGH RISK",
            "🔴",
            "Your situation may be unsafe. "
            "Move to a crowded or safe location and "
            "contact a trusted person if necessary."
        )