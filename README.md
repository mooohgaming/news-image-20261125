# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/mooohgaming/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/mooohgaming/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

`main.py` draws one newspaper page — "The World in One Page" — summing up
Wednesday 25 November 2026 in a single 1024x1024 PNG. Six stories, each with
a headline, three lines of text, a drawn illustration and a source line:

1. **Britain to licence all knife sales** — the Home Office unveils the
   world's first licensing scheme for every knife sale: shops, online and
   private sellers. (GOV.UK / The Guardian)
2. **Met still failing on race, review finds** — a 389-page independent
   review finds no "good" progress on any Casey reform and warns new
   scandals are highly likely. (The Guardian / The Times)
3. **Australia signs historic Pacific treaty** — Canberra becomes the
   Solomon Islands' defence partner of choice as the islands let their
   China pact lapse. (Reuters / AAP)
4. **Frailty gap widest in England, study finds** — the poorest
   50-year-olds in England are frailer than the richest by the widest
   margin of 31 countries. (The Guardian / BMC Medicine)
5. **Coasts get 11m pounds to fight erosion** — twelve council projects
   get funding for drone surveys, dune restoration and moving roads
   inland. (The Guardian)
6. **Australia says sorry to LGBTQ veterans** — Defence Minister Marles
   apologises in parliament for decades of "witch hunts" that forced gay
   personnel out of the services. (Reuters / defence.gov.au)

The program uses only the Python standard library: it draws the page with its
own canvas code and a built-in 5x7 bitmap font, and encodes the PNG by hand
(zlib + struct). No network, no clock, no randomness — two runs produce
byte-identical output.

## Run it

```sh
python3 main.py
```

That writes `/output/entry.png`. To write elsewhere, set
`MAKEFUN_OUTPUT_DIR`:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
