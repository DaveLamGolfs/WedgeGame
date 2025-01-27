from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "wedge_master_secret"  # Secret key for session handling


@app.route("/")
def index():
    # Initialize game session data if not already present
    if "current_round" not in session:
        session["current_round"] = 1
        session["total_score"] = 0
        session["rounds"] = []

    # Redirect to the game-over page if all 10 rounds are complete
    if session["current_round"] > 10:
        return redirect(url_for("game_over"))

    # Generate a random target yardage for the current round
    if "yardage" not in session:
        session["yardage"] = random.randint(30, 110)

    return render_template(
        "index.html",
        round=session["current_round"],
        yardage=session["yardage"],
        rounds=session["rounds"],
    )


@app.route("/submit", methods=["POST"])
def submit():
    user_yardage = request.form.get("user_yardage")
    # Validate user input
    if not user_yardage or not user_yardage.isdigit():
        return redirect(url_for("index"))

    user_yardage = int(user_yardage)
    yardage = session["yardage"]
    score = calculate_score(yardage, user_yardage)
    feedback = feedback_message(score)

    # Save the round details
    round_data = {
        "original_yardage": yardage,
        "user_yardage": user_yardage,
        "score": score,
        "feedback": feedback,
    }
    session["rounds"].append(round_data)
    session["total_score"] += score
    session["current_round"] += 1

    # Generate a new target yardage for the next round or clear it if the game is over
    if session["current_round"] <= 10:
        session["yardage"] = random.randint(30, 110)
    else:
        session.pop("yardage", None)

    return redirect(url_for("index"))


@app.route("/game_over")
def game_over():
    total_score = session.get("total_score", 0)
    rounds = session.get("rounds", [])
    return render_template("game_over.html", total_score=total_score, rounds=rounds)


@app.route("/restart")
def restart():
    session.clear()  # Clear the session to start a new game
    return redirect(url_for("index"))


def calculate_score(original, user):
    diff = abs(original - user)
    if diff <= 1:  # Perfect or almost perfect
        return 10
    if diff <= 3:  # Very close (harder score)
        return 9
    if diff <= 7:  # Close (harder score)
        return 8
    if diff <= 12:  # Fairly close (harder score)
        return 7
    if diff <= 17:  # Within a decent margin
        return 6
    if diff <= 22:  # Adjusted range for score 5
        return 5
    if diff <= 27:  # Adjusted range for score 4
        return 4
    if diff <= 35:  # Needs improvement
        return 3
    if diff <= 45:  # A little far off
        return 2
    return 1  # Way off

def feedback_message(score):
    """
    Provide feedback based on the score.
    """
    if score >= 9:
        return "Amazing shot!"
    if score >= 7:
        return "Great shot!"
    if score >= 5:
        return "Not bad!"
    return "Better luck next time."


if __name__ == "__main__":
    app.run(debug=True)
