# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeMatch 1.0  
A rule-based music recommender that scores songs against a user's taste profile and returns the top 5 best fits.

---

## 2. Intended Use  

VibeMatch is designed to suggest songs that match a listener's current mood, preferred genre, and energy level. It is built for classroom exploration — not for production use in a real app.

It assumes the user can describe their taste with three simple inputs: a genre, a mood word, and an energy number between 0 and 1. It works best when those preferences match words that actually appear in the song catalog.


---

## 3. How the Model Works  

Every song in the catalog gets a score from 0 to 6.5. Higher score = better fit for the user.

The score is built from four pieces:

- Genre match (+1.0): If the song's genre exactly matches what the user asked for, it gets a point. No partial credit — "rock" and "metal" are treated as completely different.
- Mood match (+1.0): Same idea. If the mood tag matches exactly, it gets a point.
- Energy closeness (0 – 4.0):** The closer the song's energy is to the user's target, the more points it earns. A perfect match gives 4.0. A song that's 0.5 away gives 2.0. This is the biggest factor.
- Acoustic preference (0 – 0.5): If the user likes acoustic-sounding music, songs with high acousticness get rewarded. If not, low-acousticness songs get rewarded instead.

All four numbers are added up. The five songs with the highest totals are returned as recommendations.

The energy weight was doubled (from 2.0 to 4.0) and the genre weight was halved (from 2.0 to 1.0) compared to the original starter code, to reduce genre over-dominance.

---

## 4. Data  

The catalog contains 20 songs. Each song has: title, artist, genre, mood, energy (0–1), tempo in BPM, valence, danceability, and acousticness.

Genres covered: pop, lofi, rock, metal, ambient, jazz, synthwave, indie pop, hip hop, classical, country, reggae, latin, r&b, folk, afrobeats, drum and bass.

Moods covered: happy, chill, intense, focused, moody, relaxed, reflective, confident, nostalgic, uplifting, rebellious, romantic, playful, earthy, joyful, driven.

Limits: Most genres appear only once. No genre has more than two songs. Moods like "sad," "angry," "anxious," or "epic" are missing entirely. The dataset was not modified — no songs were added or removed.

---

## 5. Strengths  

The system works best when a user's preferences are clear and the catalog has songs that match all three inputs at once.

- The Chill Lofi profile scored a near-perfect 6.43/6.5 for its #1 result. Genre, mood, energy, and acousticness all lined up — exactly what a good recommender should do.
- The High-Energy Pop profile also returned an intuitive #1 (*Sunrise City*). The scoring correctly identified that a genre + mood + close energy all together beats a closer energy match with no mood.
- The explanation output (the "Why" breakdown) makes it easy to see exactly why each song ranked where it did. That transparency is genuinely useful for learning how scoring works.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

Findings from system evaluation: The most significant bias discovered is a genre-driven filter bubble caused by the small 20-song catalog. Because most genres appear only once or twice, any user whose preferred genre has a single catalog match will always receive that song as #1 regardless of how poorly it fits their energy or mood preferences — the genre bonus alone is enough to guarantee the top spot. The energy gap formula treats overshooting and undershooting a target equally (`|song_energy − target_energy|`), but these are not musically equivalent: a user who wants high-energy music at 0.9 would likely tolerate a song at 0.95 far more than one at 0.85, yet both are penalized identically. The system also uses exact-string genre matching, which means semantically adjacent genres — such as "rock", "metal", and "drum and bass" — receive zero shared credit, causing genuinely relevant songs in neighboring genres to score lower than off-genre songs that happen to match the user's mood. Finally, when a user specifies a genre or mood that does not exist anywhere in the catalog (a "ghost preference"), the scorer silently returns confident-looking scores (e.g., 4.1 / 6.5) with no indication that none of the stated preferences were actually matched — a user inspecting only the score column would have no way to know the results are essentially random.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Profiles tested: Six user profiles were run against the full 20-song catalog: three standard profiles (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three adversarial edge cases (Energy 0.9 + nonexistent mood "sad," Acoustic Lover wanting Intense Rock, and a Ghost Genre "opera" with no catalog matches). For each profile the top 5 scored songs were inspected, with attention to whether the #1 result felt musically appropriate, whether scores bunched together or spread out, and whether any obviously wrong songs appeared in the top 5.

What was looked for: The main questions were: Does the right song reach #1? Does a song that clearly shouldn't be there sneak into the top 5? And does the scoring system give any warning signal when it has no good answer (e.g., ghost genre)?

What was surprising: The most unexpected result came from the Deep Intense Rock profile. A pop song — Gym Hero by Max Pulse — ranked #2 above Iron Anthem (metal), which is the most sonically intense song in the entire catalog. This happened because Gym Hero shares the mood tag "intense" with the user's request, earning a +1.0 bonus that Iron Anthem cannot get (its mood is "rebellious"). The scorer does not know that metal and rock belong to the same sonic family — it only reads labels exactly, so it treats them as strangers. A second surprise was the ghost genre test: even though zero preferences matched, the system returned scores around 4.0/6.5, which look convincingly normal. There is no warning anywhere in the output that the results are meaningless.

---

## 8. Future Work  

1. Add a "no good match" warning.**  
If the top-scoring song still has a low score (e.g., below 2.5/6.5), the system should say so — something like "No strong matches found for your genre." Right now it silently returns whatever it has, even when all preferences missed.

2. Allow partial genre credit for related genres.**  
Rock, metal, and punk are clearly related. A simple lookup table of adjacent genres ("rock" → also reward "metal" at +0.5) would fix the Iron Anthem problem without requiring machine learning.

3. Expand the catalog.**  
With only 1–2 songs per genre, the system almost always has one "correct" answer locked in before scoring even starts. Adding 5–10 songs per genre would let energy and mood actually determine the winner instead of genre alone.

---

## 9. Personal Reflection  

Biggest learning moment: The ghost genre test. I asked for "opera" knowing it wasn't in the catalog, and the system came back with scores around 4.1/6.5 like nothing was wrong. That was the moment I understood that a confident-looking number and a correct answer are two totally different things. The scorer had no way to say "I don't know" — it just kept doing math.

On using AI tools: Having an AI assistant help write profiles and spot edge cases saved a lot of time, especially for the adversarial tests. But I still had to read every output carefully. The tool suggested the "acoustic lover + intense rock" edge case, and I didn't fully believe it would produce interesting results until I actually ran it and watched Iron Anthem get pushed down by a pop song. You can't just trust the output — you have to check it against your own intuition.

What surprised me about simple algorithms: Four rules and twenty songs somehow felt like a real recommender. When Library Rain hit 6.43/6.5 for the Chill Lofi profile, it genuinely felt correct — like the system understood what I wanted. That's a little unsettling when you realize it's just addition. The "intelligence" is mostly an illusion created by how well the weights happen to match the data.

What I'd try next: I'd add partial genre credit for related genres (rock → metal → punk), a low-confidence warning when no genre or mood matched, and at least 5 songs per genre so energy and mood actually get to decide the winner instead of genre doing it alone before the other factors even matter.
