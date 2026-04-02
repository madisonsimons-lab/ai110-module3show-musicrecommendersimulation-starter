# Reflection: Profile Comparisons

A plain-language comparison of each pair of user profiles tested, explaining what changed
between their outputs and why that makes sense.

---

## Pair 1 — High-Energy Pop vs. Chill Lofi

These two profiles are almost perfect opposites, and the results reflect that clearly.

The High-Energy Pop profile asked for upbeat, loud, danceable music (energy 0.9, genre pop,
mood happy). The top result was *Sunrise City* — a bright pop track sitting at 0.82 energy
with a "happy" mood tag. That's a strong match on all three preferences at once, so it
deserved #1.

The Chill Lofi profile asked for something completely different: quiet, mellow background
music for studying or relaxing (energy 0.35, genre lofi, mood chill, likes acoustic sounds).
*Library Rain* reached a near-perfect score of 6.43/6.5 because its energy was an exact
match at 0.35, its genre and mood were right, and it has a very high acousticness (0.86 —
meaning it sounds organic and instrument-heavy, not electronic).

The key takeaway: when a user's preferences all point in the same direction and the catalog
has a song that checks every box, the system works exactly as intended. Both #1 results here
felt musically correct.

---

## Pair 2 — High-Energy Pop vs. Edge Case 1 (Energy 0.9 + mood "sad")

This comparison reveals a quiet flaw in the system.

The High-Energy Pop profile asked for `mood: happy`. Its #1 result was *Sunrise City* —
which is genuinely a happy-sounding pop song. Makes sense.

The Edge Case 1 profile changed only one thing: `mood: sad`. No song in the catalog has a
"sad" mood tag, so that preference is silently ignored — the system never awards the +1.0
mood bonus to anyone. Because of that, the #1 result flipped from *Sunrise City* to
*Gym Hero*. Why? *Gym Hero* has a slightly better energy match (0.93 vs. target 0.90),
which gave it a thin edge once the mood bonus was removed from the equation.

In plain language: asking for "sad pop" and asking for "happy pop" should produce very
different results, but here they produce nearly identical top-5 lists, just with the top two
swapped. The system has no concept of "no good mood match found" — it just keeps going as
if mood was never part of the request.

---

## Pair 3 — Deep Intense Rock vs. Edge Case 2 (Acoustic Lover + Intense Rock)

This pair shows what happens when two preferences fight each other.

The Deep Intense Rock profile asked for loud, electric rock (genre rock, mood intense,
energy 0.95, does not like acoustic sounds). The system correctly ranked *Storm Runner* #1
— it's the only actual rock song (genre match = +1.0), it's genuinely intense (mood match
= +1.0), and its energy is close to the target.

Edge Case 2 changed only one thing: `likes_acoustic: True`. This tells the scorer to reward
songs that sound organic and instrument-driven — which describes folk, classical, and
ambient music, not rock. Suddenly the scorer is pulling in two opposite directions: genre
and energy say "loud electric rock," but the acoustic preference says "quiet wooden guitars."

*Storm Runner* still wins at #1, but its score drops noticeably. More importantly,
*Iron Anthem* (the metal song) — which should intuitively be close to an intense rock
request — falls further down the list because metal is almost entirely non-acoustic.
A user who set `likes_acoustic: True` by accident while trying to find hard rock would
get results that quietly drift toward softer, more acoustic-sounding songs.

---

## Pair 4 — Deep Intense Rock vs. Edge Case 3 (Ghost Genre "opera")

This pair is the most instructive because one of them is a completely broken request —
but you'd never know it from looking at the scores.

The Deep Intense Rock profile produced a top result (*Storm Runner*) with a score of
6.29/6.5. That's a high score, and it makes sense: genre, mood, and energy all matched.

The Ghost Genre "opera" profile asked for a genre and mood that don't exist anywhere in the
20-song catalog. The system can't match either preference, so the +1.0 genre bonus and
+1.0 mood bonus are never awarded to any song. Yet the top result (*Dusty Highway*, a
country song) still scored 4.17/6.5. That looks like a decent score — but it means nothing.
The system picked a country song as the "best opera" recommendation simply because its
energy (0.51) happened to be closest to 0.50.

The important lesson: a high score from this system doesn't always mean the result is good.
It can mean the system ran out of real signals and ranked by whatever was left (energy
proximity), producing a confident-looking answer to a question it had no ability to answer.

---

## Why Does "Gym Hero" Keep Showing Up?

*Gym Hero* (pop, intense, energy 0.93) appears in the top 5 for almost every high-energy
profile, even profiles that have nothing to do with pop or intensity. Here's the plain reason:

The catalog has only 20 songs. Of those, only two are pop — *Sunrise City* and *Gym Hero*.
Any user who prefers pop automatically has a small pool to draw from. But *Gym Hero* also
has the second-highest energy in the entire catalog (0.93), which means it ranks highly on
energy proximity for anyone targeting 0.9 or above — even if genre and mood don't match.

Think of it this way: if you asked a friend to recommend a happy pop song and they only
owned three pop albums, one of them would keep coming up no matter what you asked for.
That's the filter bubble at work. The system isn't broken — it's doing exactly what the
math says — but the catalog is too small to give genuinely different answers to different
questions.
