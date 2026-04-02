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


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # ── Header ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 52)
    print("  🎵  Music Recommender — Top 5 Results")
    print("=" * 52)
    print(f"  Profile : genre={user_prefs['genre']}  "
          f"mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}")
    print("=" * 52)

    # ── Results ───────────────────────────────────────────────────────────────
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  "
              f"|  Energy: {song['energy']:.2f}")
        print(f"       Score: {score:.2f} / 5.50")
        print("       Why:")
        for reason in explanation.split(" | "):
            print(f"         • {reason}")

    print("\n" + "=" * 52 + "\n")


if __name__ == "__main__":
    main()
