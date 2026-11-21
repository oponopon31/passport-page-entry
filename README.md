[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/oponopon31/passport-page-entry/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/oponopon31/passport-page-entry/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

# Passport of the Republic of Velmora

An open passport spread for a country that does not exist: the
Republic of Velmora (Respublika Velmora), a small republic famous
for its lakeside casinos, capital Velmar. The holder is Korban
Slot, a 24-year-old slot player, born 14 June 2001 in Velmar,
licence S-0771. Passport VEL077777 — 777, the jackpot number —
issued 14 March 2024 in Velmar, valid to 13 March 2034.

Built for the [make.fun bounty the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

## How it works

A program at the repository root draws the image procedurally and writes it to `/output/entry.png` — no network, fully deterministic, standard library only. Two runs produce a byte-identical PNG (1024×1024). The holder's photograph is a real photograph supplied by the holder, shipped as `assets/holder-photo.png` and loaded at run time with a small stdlib PNG decoder in the program (no PIL at run time); the asset was prepared at build time only as a tight passport-style head-and-shoulders crop, with the face untouched.

## Why the document holds together

- **One document, one type system.** Bilingual labels (Velmoran / English), one header style, one rule weight, one margin grid across both pages; the paper carries the same fine guilloche throughout, with a maroon header and a gold 777 emblem in a ring.
- **Dates agree.** The passport was issued 14 March 2024 in Velmar and runs to 13 March 2034. Every stamp is dated after issue, and the trips pair up: out of Velmora and into the neighbour, then back out and home again — Zoraville, Tarnovia (June 2024), Lumina, Ostara (August–September 2025). Red ink is Velmora, blue ink is Tarnovia, green ink is Ostara.
- **The visa fits the travel.** One Ostara visitor visa, type C single entry, 30 days, valid 1 August – 30 September 2025, fee 40 VEL, issued in Velmar 18 July 2025, covers the Ostara trip.
- **The portrait belongs to the place.** A slot player's passport photograph, with a smaller second copy on the data page, beside the slot licence noted in the observations.
- **The telling detail.** The visa page carries a slot credit endorsement: the holder is a registered slot player, casino credit limited to 500 VEL per visit, winnings above 1,000 VEL must be declared at the border. A round casino-tax stamp (40 VEL paid, Port of Velmar, 3 June 2024 — the day of his first departure) sits beside it.
- **The machine-readable zone is real.** Both MRZ lines are 44 characters in ICAO 9303 TD3 format, and every check digit is computed by the 7-3-1 algorithm in the program, not typed in by hand.

The country, its people and its neighbours are invented. The photograph is the holder's own, supplied for this entry.
