from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to int/float."""
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []

    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": int(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )

    print(f"Loaded songs: {len(songs)}")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences (+2 genre, +1 mood, 0-2 energy, 0-0.5 acoustic); return (score, reasons)."""
    score: float = 0.0
    reasons: List[str] = []

    # Genre match
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += 2.0
        reasons.append(f"genre match: {song['genre']} (+2.0)")

    # Mood match
    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += 1.0
        reasons.append(f"mood match: {song['mood']} (+1.0)")

    # Energy similarity: closer to target = higher points (0.0 – 2.0)
    target_energy: float = float(user_prefs.get("energy", 0.5))
    energy_distance: float = abs(song["energy"] - target_energy)
    energy_points: float = round(2.0 * (1.0 - energy_distance), 3)
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} "
        f"(+{energy_points:.2f})"
    )

    # Acoustic preference: rewards high acousticness if user likes it, low if not
    likes_acoustic: bool = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_points: float = round(0.5 * song["acousticness"], 3)
        reasons.append(
            f"acoustic match: acousticness {song['acousticness']:.2f} (+{acoustic_points:.2f})"
        )
    else:
        acoustic_points = round(0.5 * (1.0 - song["acousticness"]), 3)
        reasons.append(
            f"low-acoustic match: acousticness {song['acousticness']:.2f} (+{acoustic_points:.2f})"
        )
    score += acoustic_points

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top-k as (song, score, explanation) tuples."""
    target_energy: float = float(user_prefs.get("energy", 0.5))

    # Score every song in one readable pass using a list comprehension.
    # Each element is (song_dict, score, reasons_list).
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]

    # sorted() creates a brand-new ranked list; the original `songs` catalog is
    # never modified.  .sort() would sort in place and destroy the original order.
    # Tie-break 1: smaller energy distance  Tie-break 2: lower id (stable output)
    ranked = sorted(
        scored,
        key=lambda x: (-x[1], abs(x[0]["energy"] - target_energy), x[0]["id"]),
    )

    # Build final output: join each song's reason list into one explanation string.
    return [
        (song, score, " | ".join(reasons))
        for song, score, reasons in ranked[:k]
    ]
