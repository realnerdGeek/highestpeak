# EarWorm source

Everything used to build and test EarWorm (formerly HighestPeak). The live app is the files at the top of this repo (`index.html`, `sw.js`, `manifest.webmanifest`, icons), served by GitHub Pages at https://realnerdgeek.github.io/highestpeak/. This folder is the source that produces them. Nothing in here changes the live app until it's built and copied up.

## Layout
```
source/
  app/
    v7-backup.html      the base page every build starts from
    v6-index-head.txt   page head used for the test copy (app/index.html)
    v8/build.py         applies the patches below, in order, and checks the JavaScript parses
    v8/lib.py           patch helpers (rep asserts the exact match count, cut, before, after)
    v8/p5_home.py ... p15_v13.py   one patch file per version (p10 = home screen app storage, p11 = V10, p12 = V10.1, p13 = V11, p14 = V12, p15 = V13)
    test1.js ... test18.js         one test file per version (test16 = V11 sync, test17 = V12, test18 = V13)
    legacy.js           loaded by tests 1 to 16: shows every Settings section on one page and marks the sync invite as seen
    mocksb.js           a stand-in for Supabase (accounts, docs table rules, files, usernames, two-step sign-in, delete account)
    pw.js               finds Playwright (PW_PATH, the Claude workspace copy, or npm)
    media/              test files that are safe to be public (made with ffmpeg)
    logo/               earworm-icon.svg and earworm-icon-1024.png (the app icons come from this), plus the old HighestPeak logo
  pwa/build_pwa.py      turns app/gym-tapes.html into the home screen site in pwa/site
  sql/                  the Supabase setup pastes (setup.sql, setup12.sql, fix12.sql) and the local Postgres test files
```

## Build
```
python3 source/app/v8/build.py        # makes app/gym-tapes.html (the page) and app/index.html (test copy)
python3 source/pwa/build_pwa.py       # makes pwa/site (index.html, sw.js, manifest, icons)
```
Rebuilding from this source gives exactly what's live (checked October 19, 2026, V13).

### Making a new version
1. Add `app/v8/p16_v14.py` with an `apply(d)` function (copy the style of p15_v13.py), and add `'p16_v14'` to the module list in `build.py`.
2. Build, then test (below).
3. Add `test19.js` for the new version.
4. Deploy (below).

## Test
Needs Node with Playwright and Chromium, ffmpeg, Python 3 with Pillow, and for the SQL tests Postgres 16.
```
cd source/app
mkdir -p out shots
node test18.js          # each test prints PASS/FAIL lines and "N passed, M failed"
```
- Run three at a time at most. test9's waveform check can flake under heavy load; it passes on its own.
- test13 needs `out/four.zip`, which test10 makes. Run test10 first.
- Chromium in Playwright can't play H.264/AAC, so tests use VP9 and Opus copies where sound has to play.

### Private test videos (not in this repo)
Most older tests use copies of real saved videos (other people's TikToks and Matthew's own .mov uploads). Those can't go in a public repo, so they're kept in a separate zip Matthew has (EarWorm-private-test-videos.zip). Unzip it into `source/` and the files land here (all gitignored):
- `app/media/`: 33966784-v29025g50000datbdifog65qur5e1a6g.mp4, blue-scene.mp4, clip-with-ending.mp3, moov-at-end.mp4, opus-clip.mp4, qt.mov, silent.mp4
- `vtest/`: tt-vp9.mp4, big.mp4
- `photo/`: p1.mov, p2.mov, p3.mov
- `app/seed/`: workout-loop.mp4 and its files
- `app/out/four.zip`

Without the zip, test18 runs fully. With it, all 18 run.

### SQL tests
Run Postgres 16 locally, load `sql/mock.sql` and `sql/mock12b.sql` (a stand-in for Supabase's auth and storage schemas; signed-in users can't read the sign-in factors table, like the real one), then `setup.sql`, `setup12.sql`, `fix12.sql`, then `rls12.sql`. Every check prints `t`, and every ERROR line in the output is an expected refusal.

## Deploy
```
cp -r source/pwa/site/. .            # from the repo root
git add -A && git commit -m "V14: ..." && git push
```
GitHub Pages redeploys in about a minute (repo Actions tab). The app checks for the new version each time it opens with a connection.

## Supabase
Project pkibuxnxnirvjznmcnyo (https://pkibuxnxnirvjznmcnyo.supabase.co). The publishable key in the app is meant to be public. Never put the secret key, service_role key or database password in this repo.
