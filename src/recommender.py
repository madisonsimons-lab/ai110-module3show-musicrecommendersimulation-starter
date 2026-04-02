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
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "mode": "genre_first",
        }
        as_dicts = [song.__dict__ for song in self.songs]
        ranked = recommend_songs(user_prefs, as_dicts, k=k)
        return [Song(**item[0]) for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
            "mode": "genre_first",
        }
        _, reasons = score_song(user_prefs, song.__dict__, mode="genre_first")
        return " | ".join(reasons)


@dataclass(frozen=True)
class RankingWeights:
    genre: float
    mood: float
    energy: float
    acoustic: float
    popularity: float
    decade: float
    mood_tags: float
    tempo: float
    instrumental: float


RANKING_STRATEGIES: Dict[str, RankingWeights] = {
    "genre_first": RankingWeights(
        genre=2.5,
        mood=1.2,
        energy=2.5,
        acoustic=0.5,
        popularity=0.6,
        decade=0.6,
        mood_tags=0.8,
        tempo=0.6,
        instrumental=0.4,
    ),
    "mood_first": RankingWeights(
        genre=1.2,
        mood=2.6,
        energy=2.2,
        acoustic=0.5,
        popularity=0.5,
        decade=0.6,
        mood_tags=1.6,
        tempo=0.6,
        instrumental=0.4,
    ),
    "energy_focused": RankingWeights(
        genre=1.0,
        mood=1.0,
        energy=4.2,
        acoustic=0.4,
        popularity=0.5,
        decade=0.5,
        mood_tags=0.7,
        tempo=1.2,
        instrumental=0.3,
    ),
}

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
                    "popularity": int(row.get("popularity", 50)),
                    "release_year": int(row.get("release_year", 2015)),
                    "release_decade": int(row.get("release_decade", 2010)),
                    "detailed_mood_tags": [
                        t.strip().lower()
                        for t in row.get("detailed_mood_tags", "").split(";")
                        if t.strip()
                    ],
                    "instrumentalness": float(row.get("instrumentalness", 0.3)),
                    "speechiness": float(row.get("speechiness", 0.2)),
                    "live_energy": float(row.get("live_energy", 0.2)),
                }
            )

    print(f"Loaded songs: {len(songs)}")
    return songs

def _get_weights(mode: str) -> RankingWeights:
    return RANKING_STRATEGIES.get(mode, RANKING_STRATEGIES["genre_first"])


def _decade_points(target_decade: int, song_decade: int, weight: float) -> float:
    decade_steps = abs(song_decade - target_decade) / 10.0
    return round(weight * max(0.0, 1.0 - (decade_steps / 4.0)), 3)


def score_song(user_prefs: Dict, song: Dict, mode: str = "genre_first") -> Tuple[float, List[str]]:
    """Score one song with selectable strategy and advanced feature weights."""
    weights = _get_weights(mode)
    score: float = 0.0
    reasons: List[str] = []

    # Core profile matches
    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += weights.genre
        reasons.append(f"genre match: {song['genre']} (+{weights.genre:.2f})")

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += weights.mood
        reasons.append(f"mood match: {song['mood']} (+{weights.mood:.2f})")

    target_energy: float = float(user_prefs.get("energy", 0.5))
    energy_distance: float = abs(song["energy"] - target_energy)
    energy_points: float = round(weights.energy * max(0.0, 1.0 - energy_distance), 3)
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} "
        f"(+{energy_points:.2f})"
    )

    # Acoustic preference
    likes_acoustic: bool = user_prefs.get("likes_acoustic", False)
    if likes_acoustic:
        acoustic_points: float = round(weights.acoustic * song["acousticness"], 3)
        reasons.append(
            f"acoustic match: acousticness {song['acousticness']:.2f} (+{acoustic_points:.2f})"
        )
    else:
        acoustic_points = round(weights.acoustic * (1.0 - song["acousticness"]), 3)
        reasons.append(
            f"low-acoustic match: acousticness {song['acousticness']:.2f} (+{acoustic_points:.2f})"
        )
    score += acoustic_points

    # Advanced feature 1: popularity preference
    popularity_bias = str(user_prefs.get("popularity_bias", "any")).lower()
    pop_norm = min(max(song.get("popularity", 50) / 100.0, 0.0), 1.0)
    if popularity_bias == "mainstream":
        pop_points = round(weights.popularity * pop_norm, 3)
    elif popularity_bias == "underground":
        pop_points = round(weights.popularity * (1.0 - pop_norm), 3)
    else:
        pop_points = round(weights.popularity * (1.0 - abs(pop_norm - 0.5) * 2.0), 3)
    score += pop_points
    reasons.append(f"popularity {song.get('popularity', 50)} (+{pop_points:.2f})")

    # Advanced feature 2: release decade preference
    target_decade = int(user_prefs.get("preferred_decade", song.get("release_decade", 2010)))
    song_decade = int(song.get("release_decade", 2010))
    decade_points = _decade_points(target_decade, song_decade, weights.decade)
    score += decade_points
    reasons.append(f"decade {song_decade}s vs target {target_decade}s (+{decade_points:.2f})")

    # Advanced feature 3: detailed mood-tag overlap
    pref_tags = [t.lower() for t in user_prefs.get("preferred_mood_tags", [])]
    song_tags = set(song.get("detailed_mood_tags", []))
    if pref_tags:
        overlap = len(song_tags.intersection(pref_tags)) / float(len(pref_tags))
        tag_points = round(weights.mood_tags * overlap, 3)
        score += tag_points
        reasons.append(f"mood tags overlap {overlap:.2f} (+{tag_points:.2f})")

    # Advanced feature 4: tempo target closeness
    target_tempo = int(user_prefs.get("tempo_target", song.get("tempo_bpm", 100)))
    tempo_gap = abs(int(song.get("tempo_bpm", 100)) - target_tempo)
    tempo_points = round(weights.tempo * max(0.0, 1.0 - min(tempo_gap / 100.0, 1.0)), 3)
    score += tempo_points
    reasons.append(f"tempo {song.get('tempo_bpm', 100)} vs target {target_tempo} (+{tempo_points:.2f})")

    # Advanced feature 5: instrumentalness preference
    likes_instrumental = bool(user_prefs.get("likes_instrumental", False))
    instrumentalness = min(max(float(song.get("instrumentalness", 0.3)), 0.0), 1.0)
    if likes_instrumental:
        instr_points = round(weights.instrumental * instrumentalness, 3)
    else:
        instr_points = round(weights.instrumental * (1.0 - instrumentalness), 3)
    score += instr_points
    reasons.append(f"instrumentalness {instrumentalness:.2f} (+{instr_points:.2f})")

    return round(score, 3), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score songs with a selected strategy and apply diversity penalties during top-k selection."""
    mode = str(user_prefs.get("mode", "genre_first")).lower()
    target_energy: float = float(user_prefs.get("energy", 0.5))
    artist_penalty = float(user_prefs.get("artist_repeat_penalty", 0.6))
    genre_penalty = float(user_prefs.get("genre_repeat_penalty", 0.2))

    pool = []
    for song in songs:
        base_score, reasons = score_song(user_prefs, song, mode=mode)
        pool.append(
            {
                "song": song,
                "base": base_score,
                "reasons": reasons,
            }
        )

    selected: List[Tuple[Dict, float, str]] = []
    seen_artists = set()
    seen_genres = set()

    while pool and len(selected) < k:
        best = None
        best_adjusted = -1e9
        best_reasons: List[str] = []

        for entry in pool:
            adjusted = entry["base"]
            penalty_reasons = []
            artist = entry["song"]["artist"]
            genre = entry["song"]["genre"]

            # Diversity penalty: discourage repeated artist/genre in the top-k list.
            if artist in seen_artists:
                adjusted -= artist_penalty
                penalty_reasons.append(f"diversity penalty: repeated artist -{artist_penalty:.2f}")
            if genre in seen_genres:
                adjusted -= genre_penalty
                penalty_reasons.append(f"diversity penalty: repeated genre -{genre_penalty:.2f}")

            candidate_reasons = entry["reasons"] + penalty_reasons
            tie_key = (adjusted, -abs(entry["song"]["energy"] - target_energy), -entry["song"]["id"])
            if best is None or tie_key > (
                best_adjusted,
                -abs(best["song"]["energy"] - target_energy),
                -best["song"]["id"],
            ):
                best = entry
                best_adjusted = adjusted
                best_reasons = candidate_reasons

        selected.append((best["song"], round(best_adjusted, 3), " | ".join(best_reasons)))
        seen_artists.add(best["song"]["artist"])
        seen_genres.add(best["song"]["genre"])
        pool.remove(best)

    return selected
