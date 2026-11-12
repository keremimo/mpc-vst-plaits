# MPC Plaits

**Mutable Instruments Plaits as a native instrument for Akai MPC standalone devices and for
[Melodee](https://github.com/keremimo/melodee-sample) on the MPC Sample.**

All 24 Plaits models, up to 8 voices, LFOs, envelopes and two modulation matrices, synced to the tempo, with an MPC
screen page, Q-Link pages and 25 factory sounds. It loads from the MPC's own plugin browser like any other instrument,
and on a PLUGIN track in Melodee.

This is a fork of [poloq-instruments/mpc-vst-plaits](https://github.com/poloq-instruments/mpc-vst-plaits). The sound
engine is poloq's port. This fork adds:

- an **aarch64 build** (Gen2 MPC OS devices and the MPC Sample) next to the armv7 one;
- **Slide and Tie** from a sequencer (CC 84 and CC 68, as Melodee sends for its Slide and Tie steps);
- a **page in Melodee's look** (NIGHT palette, Rubik), laid out so each three Q-Links are one row of K1-K3 in Melodee;
- **25 factory sounds** in the PRESET menu (Melodee: PRESETS).

The name, uid (`MiPl`), `plaits.so` and every parameter's position are unchanged, so projects saved with poloq's
1.0.x open with this build and the other way round. The MODEL < and > buttons (the last two parameters) are gone:
pick the model from its list or turn its Q-Link.

## Highlights

- **All 24 Plaits models** (firmware 1.2, in the module's order), from virtual analog and FM to chords, speech,
  strings and drums.
- **Polyphonic:** mono, poly or legato, up to 8 voices, with unison, detune and stereo spread.
- **Four ways to play the low-pass gate:** GATE, PING (struck), ENV (driven by an ADSR) and DRONE.
- **Modulation:** two LFOs, two ADSRs, a cycling envelope and a random source, routed through a ready-made 4 x 4 matrix
  plus an assignable one (velocity, aftertouch, mod wheel into FM, LPG, filter, volume, pan and more).
- **Tempo sync:** LFOs, random and retriggers follow the tempo and restart when the sequencer starts.

## Requirements

- **MPC OS:** a first-generation standalone device (32-bit ARM: MPC One, Live, Live II, X, Key 61, Force) or a
  second-generation one (aarch64), with root SSH access. Stock MPC OS doesn't offer this, so you need a modded unit.
  poloq tested 1.0.x on an MPC One running MPC OS 3.9.1 (`tested.json`).
- **Melodee:** an MPC Sample running Melodee.

Installing plugins this way is unofficial: back up first, and use it at your own risk.

## Install

### Melodee (MPC Sample)

1. Download `MPC-Plaits-<version>-mpc-sample.zip` from [Releases](../../releases).
2. Unzip it and copy the folder inside (`poloq - VST - MPC Plaits`) into `Plugins/` at the top of the SD card.
3. Pick **MPC Plaits** on a PLUGIN track.

### MPC OS

1. Download `MPC-Plaits-<version>-mpc-armv7.zip` (Gen1, Force) or `-mpc-aarch64.zip` (Gen2) from Releases.
2. Unzip it and copy the folder to the device:
   ```
   scp -r MPC-Plaits-1.1.0 root@<device-ip>:/tmp/
   ```
3. **Save your project**, then run the installer. It stops MPC, backs up `MPC.settings`, registers the plugin and
   starts MPC again:
   ```
   ssh root@<device-ip> sh /tmp/MPC-Plaits-1.1.0/install.sh
   ```
4. Add **MPC Plaits** to a track from the plugin browser (Instrument plugins).

> **MPC One and Live:** the SD card is mounted `noexec`, so a plugin can't load from it. Install into a folder on the
> internal storage instead, and list that folder under `SynthContentLocations` in `MPC.settings`:
> `sh install.sh -t /media/az01-internal/Synths`

`INSTALL.md` inside the zip has the full steps, including installing by hand.

## The pages

Eight tabs, each two rows. Q-Links follow the controls left to right, row 1 then row 2. In Melodee every three
Q-Links are one row on K1-K3, so the groups below are Melodee's rows.

| Tab | Rows of three |
|---|---|
| **PLAITS** | MODEL, FREQ, HARMONICS · TIMBRE, MORPH, OUT/AUX · the TIMBRE, FM and MORPH attenuverters · AMP, LPG COLOR, LPG DECAY |
| **VOICE** | MODE, NOTES, UNISON · DETUNE, SPREAD, PAN · GLIDE, BEND, VEL CURVE · filter TYPE, CUTOFF, RESO |
| **ENV** | ENV 1 ATTACK, DECAY, SUSTAIN · RELEASE, RETRIG, VOLUME · ENV 2 ATTACK, DECAY, SUSTAIN · RELEASE, RETRIG, TRIG RATE |
| **LFO** | per LFO: SHAPE, RATE, PHASE · RETRIG, SYNC, SYNC DIV |
| **CYCLE** | cycling envelope RISE, FALL, SHAPE · RANDOM MODE, RATE, SLEW · RETRIG, SYNC, SYNC DIV |
| **ROUTES** | the assignable matrix's four sources and four destinations |
| **ASSIGN** | its 16 amounts, a row per source, each with an ON switch |
| **MOD** | the fixed matrix: LFO 1, ENV 2, CYCLE and RANDOM into PITCH, HARM, TIMBRE and MORPH, each with an ON switch |

Switches that are set once (AT CURVE, LFO PER VOICE, CYCLE BIPOLAR and RETRIG, the matrix ON switches) are on the
screen but not on Q-Links; in Melodee they come after the Q-Link pages.

- **AMP:** GATE (the gate follows the key), PING (struck, rings out with DECAY), ENV (ENV 1 drives the gate), DRONE
  (free-running).
- **TRIG RATE:** synced retriggers while a key is held, so Chiptune arpeggiates and drums ratchet.
- **The attenuverters** set how far the per-note decay envelope moves TIMBRE, FREQUENCY and MORPH, as on the module.
- **The matrices:** every amount is bipolar and uses Plaits' own attenuverter curve, fine-grained around the centre.
  ASSIGN starts routed as LFO 2, velocity, aftertouch and mod wheel into FM, LPG decay, cutoff and volume.

## Factory sounds

Init, Filter Bass, Saw Lead, Square Bass, PD Keys, FM Piano, FM Bells, Terrain Lead, String Ensemble, Chip Arp,
Fold Bass, FM Pluck, Formant Voice, Drawbar Organ, Wavetable Pad, Chord Stab, Speech, Swarm Pad, Noise Sweep,
Particle Drops, Plucked String, Modal Bell, Kick, Snare, Hi-Hat. A sound sets every parameter except VOLUME.
`tools/make_presets.py` writes them to `vst/presets.json`.

## MIDI

| Message | Does |
|---|---|
| Note on / off | plays (velocity 0 is a release) |
| Pitch bend | by BEND semitones |
| CC 1 | the mod wheel |
| Poly pressure, channel pressure | aftertouch |
| CC 64 | sustain pedal |
| CC 84, then a note | **slide**: the held voice of the key CC 84 named goes on as the new note, no new strike, gliding there at GLIDE's rate (60 ms with GLIDE at 0) |
| CC 68 down, CC 84, then a note | **tie**: the same, without the glide |
| CC 120 / 123 / 121 | all sound off / all notes off / reset controllers |

## CPU

poloq's measurement on an MPC One (`tools/bench.sh` in mpc-vst-plugins), as a share of one 128-sample audio block:

| Load | p99 |
|---|---|
| 1 voice | ~3% |
| 4 to 16 voices | ~7% |
| Release tail | ~10% |
| Fast Q-Link sweep | ~24% |

The Q-Link sweep peak comes from Plaits recomputing the model's parameters on every step. The aarch64 build has no
bench yet.

## Building from source

<details>
<summary>Build, release, install from source and tests</summary>

### Build

Needs Docker and a sibling checkout of [mpc-vst-plugins](https://github.com/open-mpc/mpc-vst-plugins) (`main`; poloq's
`poloq-dev` branch has no aarch64 target or presets). Set `MPC_VST` if it isn't at `../mpc-vst-plugins`.

```
./build.sh
```

Outputs `vst/build/plaits.so` (armv7), `vst/build/aarch64/plaits.so`, `vst/build/skin/poloq - VST - MPC Plaits/` and
`vst/build/pluginlist-entry.xml`.

The page and the sounds are generated: edit `tools/make_layout.py` or `tools/make_presets.py` and run it, then build.

### Release

```
tools/release.sh
```

Builds both targets and writes `dist/`: the `-mpc-armv7.zip` and `-mpc-aarch64.zip` release zips (mpc-vst-plugins'
`tools/release.py`), the `-mpc-sample.zip` (the aarch64 plug-in folder alone) and `SHA256SUMS.txt`.

### Install from source (MPC One)

```
./install_mpc_one.sh [--bench bench.json]
```

Packages the build as a release zip and installs it on the MPC reachable as `ssh mpc`, into
`/media/az01-internal/Synths`. That folder must be listed in `MPC.settings`' `SynthContentLocations`.

### Tests

- `TEST=tests/<name>.c tests/run_c.sh` builds one host test (`controls`, `notes`, `sustain`, `voices`, `voicing`,
  `modulation`, `deadvoice`, `slide`, `presets`, `dump_defaults`) with ASan/UBSan in Docker and runs it. After editing
  a header, `rm -rf tests/build` first. `notes` takes a mode argument (`-1` = all): `TEST=tests/notes.c tests/run_c.sh -1`.
- `tests/run_fuzz.sh [blocks] [seed]` runs the random-input fuzzer (`tests/fuzz.c`).

### Versioning

The uid (`MiPl`), `plaits.so` and the catalog id `mpc-plaits` never change. The major version goes up only when
parameter positions change, because MPC stores a project's plugin values by position.

</details>

## Credits

Port and MPC integration by **poloq** ([poloq-instruments](https://github.com/poloq-instruments)). Aarch64 build,
Slide and Tie, Melodee page and factory sounds by Kerem Kilic (Ellic Studio).

Built on:

- **Emilie Gillet / Mutable Instruments**: [Plaits](https://github.com/pichenettes/eurorack/tree/master/plaits), the
  original module and its DSP (MIT).
- **[handcraftedcc](https://github.com/handcraftedcc)**: [schwung-mrhyde](https://github.com/handcraftedcc/schwung-mrhyde),
  the Plaits build for Ableton Move whose bridge is vendored here (see `src/VENDORED.md` for what was reused, dropped
  and changed).
- **[charlesvestal](https://github.com/charlesvestal)**: [Schwung](https://github.com/charlesvestal/schwung) (formerly
  Move Anything), the plugin API that bridge targets.
- **[sd88me](https://github.com/sd88me)** and the Open MPC contributors: [mpc-vst-plugins](https://github.com/open-mpc/mpc-vst-plugins), the MPC OS
  VST2 wrapper, Schwung adapter and build and skin tooling this port is built with.
- **Rubik** (SIL Open Font License, `vst/fonts/OFL.txt`), the typeface of the page.

## License

MIT, see [`LICENSE`](LICENSE), which also lists the third-party components.

*Not affiliated with or endorsed by Akai Professional or Mutable Instruments.*
