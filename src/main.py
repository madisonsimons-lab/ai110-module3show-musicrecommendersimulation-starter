"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from recommender import load_songs, recommend_songs       # python3 src/main.py
except ModuleNotFoundError:
    from src.recommender import load_songs, recommend_songs  # python3 -m src.main

try:
    from tabulate import tabulate
except ModuleNotFoundError:
    tabulate = None


def print_results(label: str, user_prefs: dict, recommendations: list) -> None:
    """Print a formatted table for one user profile, including reasons."""
    acoustic_flag = user_prefs.get("likes_acoustic", False)
    mode = user_prefs.get("mode", "genre_first")
    print("\n" + "=" * 60)
    print(f"  {label}")
    print("=" * 60)
    print(
        f"  mode={mode}  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
        f"energy={user_prefs['energy']}  likes_acoustic={acoustic_flag}"
    )
    print("-" * 60)

    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append(
            [
                rank,
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                f"{song['energy']:.2f}",
                f"{score:.2f}",
                explanation,
            ]
        )

    headers = ["#", "Title", "Artist", "Genre", "Mood", "Energy", "Score", "Reasons"]
    if tabulate is not None:
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        header_line = " | ".join(headers)
        print(header_line)
        print("-" * len(header_line))
        for row in rows:
            print(" | ".join(str(col) for col in row))

    print("\n" + "=" * 60 + "\n")


def main() -> None:
    songs = load_songs("data/songs.csv")

    # ── Standard User Profiles ────────────────────────────────────────────────
    profiles = [
        (
            "Standard Profile 1 - High-Energy Pop (Genre-First)",
            {
                "mode": "genre_first",
                "genre": "pop",
                "mood": "happy",
                "energy": 0.9,
                "likes_acoustic": False,
                "popularity_bias": "mainstream",
                "preferred_decade": 2010,
                "preferred_mood_tags": ["uplifting", "anthemic", "bright"],
                "tempo_target": 128,
                "likes_instrumental": False,
            },
        ),
        (
            "Standard Profile 2 - Chill Lofi (Mood-First)",
            {
                "mode": "mood_first",
                "genre": "lofi",
                "mood": "chill",
                "energy": 0.35,
                "likes_acoustic": True,
                "popularity_bias": "underground",
                "preferred_decade": 2020,
                "preferred_mood_tags": ["study", "soft", "warm"],
                "tempo_target": 78,
                "likes_instrumental": True,
            },
        ),
        (
            "Standard Profile 3 - Deep Intense Rock (Energy-Focused)",
            {
                "mode": "energy_focused",
                "genre": "rock",
                "mood": "intense",
                "energy": 0.95,
                "likes_acoustic": False,
                "popularity_bias": "any",
                "preferred_decade": 2000,
                "preferred_mood_tags": ["aggressive", "driving", "anthemic"],
                "tempo_target": 160,
                "likes_instrumental": False,
            },
        ),
        # ── Adversarial / Edge-Case Profiles ─────────────────────────────────
        # EDGE CASE 1: Conflicting energy + mood
        #   energy=0.9 implies high-intensity songs, but "sad" does not exist in
        #   the catalog → the mood +1.0 bonus never fires.  Does the scorer
        #   silently fall back to ranking by energy/genre alone?
        (
            "Edge Case 1 - Conflicting Energy 0.9 + mood sad",
            {
                "mode": "mood_first",
                "genre": "pop",
                "mood": "sad",
                "energy": 0.9,
                "likes_acoustic": False,
                "popularity_bias": "mainstream",
                "preferred_decade": 2010,
                "preferred_mood_tags": ["heartbreak", "somber"],
                "tempo_target": 120,
                "likes_instrumental": False,
            },
        ),
        # EDGE CASE 2: Acoustic lover who also wants intense rock
        #   likes_acoustic=True rewards quiet/folk songs (acousticness ~0.8-0.9),
        #   but genre=rock + energy=0.95 should favour loud, electric tracks.
        #   The two reward signals pull in opposite directions—watch for
        #   unexpected mid-range songs floating to the top.
        (
            "Edge Case 2 - Acoustic Lover Wanting Intense Rock",
            {
                "mode": "genre_first",
                "genre": "rock",
                "mood": "intense",
                "energy": 0.95,
                "likes_acoustic": True,
                "popularity_bias": "underground",
                "preferred_decade": 1990,
                "preferred_mood_tags": ["raw", "aggressive", "dark"],
                "tempo_target": 150,
                "likes_instrumental": True,
            },
        ),
        # EDGE CASE 3: Ghost genre + ghost mood (zero catalog matches)
        #   Neither "opera" nor "epic" appear in songs.csv, so genre (+2) and
        #   mood (+1) bonuses are always 0.  The entire ranking collapses to
        #   energy proximity + acoustic penalty, surfacing the scorer's
        #   pure-numeric fallback behaviour.
        (
            "Edge Case 3 - Ghost Genre opera + mood epic",
            {
                "mode": "energy_focused",
                "genre": "opera",
                "mood": "epic",
                "energy": 0.5,
                "likes_acoustic": False,
                "popularity_bias": "any",
                "preferred_decade": 1980,
                "preferred_mood_tags": ["epic", "cinematic"],
                "tempo_target": 100,
                "likes_instrumental": False,
            },
        ),
    ]

    for label, user_prefs in profiles:
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_results(label, user_prefs, recommendations)


if __name__ == "__main__":
    main()
