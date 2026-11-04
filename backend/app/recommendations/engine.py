import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.recommendations.catalog import CAREER_PATHS


MODEL_NAME = "tfidf-profile-match-v1"


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9+#.]+", value.casefold()))


def _profile_text(profile) -> str:
    parts = [
        profile.current_role or "",
        " ".join(profile.skills or []),
        " ".join(profile.interests or []),
        " ".join(profile.goals or []),
        profile.experience_level or "",
    ]
    return " ".join(part.strip() for part in parts if part.strip())


def _experience_fit(level: str, difficulty: str) -> float:
    scores = {
        "beginner": {"beginner": 1.0, "intermediate": 0.72, "advanced": 0.38},
        "intermediate": {"beginner": 0.7, "intermediate": 1.0, "advanced": 0.78},
        "advanced": {"beginner": 0.5, "intermediate": 0.84, "advanced": 1.0},
    }
    return scores.get(level, scores["beginner"]).get(difficulty, 0.5)


def rank_paths(profile, statuses: dict[str, str], limit: int) -> list[dict]:
    profile_text = _profile_text(profile)
    item_texts = [
        " ".join(
            [
                item["title"],
                item["summary"],
                item["category"],
                " ".join(item["skills"]),
                " ".join(item["tags"]),
                " ".join(item["steps"]),
            ]
        )
        for item in CAREER_PATHS
    ]

    similarities = [0.0] * len(CAREER_PATHS)
    if profile_text.strip():
        try:
            vectors = TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                ngram_range=(1, 2),
                token_pattern=r"(?u)\b[\w+#.]+\b",
            ).fit_transform([profile_text, *item_texts])
            similarities = cosine_similarity(vectors[0:1], vectors[1:]).ravel().tolist()
        except ValueError:
            pass

    profile_terms = _tokens(profile_text)
    goal_terms = _tokens(" ".join(profile.goals or []))
    weekly_hours = float(profile.weekly_hours or 4)
    ranked = []

    for index, item in enumerate(CAREER_PATHS):
        status = statuses.get(item["id"])
        if status in {"completed", "dismissed"}:
            continue

        item_terms = _tokens(
            " ".join([item["title"], item["category"], *item["skills"], *item["tags"]])
        )
        matched_terms = sorted(
            term for term in profile_terms.intersection(item_terms) if len(term) > 2
        )
        goal_match = (
            len(goal_terms.intersection(item_terms)) / max(len(goal_terms), 1)
            if goal_terms
            else 0.0
        )
        experience = _experience_fit(profile.experience_level, item["difficulty"])
        time_fit = min(1.0, weekly_hours / item["weekly_hours"])
        score = (
            0.62 * similarities[index]
            + 0.22 * goal_match
            + 0.10 * experience
            + 0.06 * time_fit
        )

        if matched_terms:
            explanation = "Your profile overlaps with " + ", ".join(matched_terms[:3]) + "."
        elif goal_terms and goal_match:
            explanation = "This path aligns with the goals in your profile."
        else:
            explanation = "A practical option matched to your experience level and available study time."

        ranked.append(
            {
                **item,
                "score": round(score * 100),
                "explanation": explanation,
                "status": status if status == "saved" else None,
            }
        )

    ranked.sort(key=lambda item: (-item["score"], item["title"]))
    return ranked[:limit]
