#!/usr/bin/env python3
"""MPC Plaits' factory sounds: writes vst/presets.json (the wrapper's presets, listed in MPC's PRESET menu and in
Melodee's PRESETS) from the list below.

    python3 tools/make_presets.py

Each sound starts from every parameter's default in src/module.json and changes what it lists, so picking one
sets the whole sound (models, voices, envelopes, modulation) the same way every time. VOLUME is left out: it
stays where it is set.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

SKIP = {"volume"}

ENV_AMP = {"amp_mode": "Env"}


def adsr(n, a, d, s, r):
    return {"env%d_attack" % n: a, "env%d_decay" % n: d, "env%d_sustain" % n: s, "env%d_release" % n: r}


SOUNDS = [
    ("Init", {}),
    ("Filter Bass", {"model": "VA VCF", "pitch": -12, "harmonics": 0.35, "timbre": 0.35, "morph": 0.2,
                     "voice_mode": "Legato", "glide_ms": 40, **ENV_AMP, **adsr(1, 2, 280, 0.55, 90),
                     "timbre_att": 0.35, "lpg_decay": 0.3}),
    ("Saw Lead", {"model": "Virtual Analog", "harmonics": 0.55, "timbre": 0.5, "morph": 0.85,
                  "voice_mode": "Legato", "glide_ms": 70, "unison": 2, "detune": 0.12, "spread": 0.6,
                  **ENV_AMP, **adsr(1, 4, 400, 0.8, 200), "mod_lfo1_pitch": 0.08, "lfo1_rate": 5.5}),
    ("Square Bass", {"model": "Virtual Analog", "pitch": -12, "harmonics": 0.0, "timbre": 0.25, "morph": 0.0,
                     "voice_mode": "Mono", **ENV_AMP, **adsr(1, 1, 220, 0.4, 60)}),
    ("PD Keys", {"model": "Phase Distortion", "harmonics": 0.3, "timbre": 0.45, "morph": 0.3,
                 "timbre_att": 0.5, "lpg_decay": 0.5, "lpg_color": 0.7}),
    ("FM Piano", {"model": "6-Op FM I", "harmonics": 0.0, "timbre": 0.5, "morph": 0.4, "lpg_decay": 0.75}),
    ("FM Bells", {"model": "6-Op FM II", "harmonics": 0.2, "timbre": 0.5, "morph": 0.35, "lpg_decay": 0.85}),
    ("Terrain Lead", {"model": "Wave Terrain", "harmonics": 0.4, "timbre": 0.6, "morph": 0.5,
                      "voice_mode": "Legato", "glide_ms": 50, **ENV_AMP, **adsr(1, 10, 300, 0.75, 250),
                      "mod_lfo1_timbre": 0.25, "lfo1_rate": 0.6}),
    ("String Ensemble", {"model": "String Machine", "harmonics": 0.5, "timbre": 0.55, "morph": 0.6,
                         **ENV_AMP, **adsr(1, 450, 600, 0.85, 1400), "polyphony": 6}),
    ("Chip Arp", {"model": "Chiptune", "harmonics": 0.5, "timbre": 0.4, "morph": 0.3, "trig_rate": "1/16",
                  "amp_mode": "Gate"}),
    ("Fold Bass", {"model": "Waveshaping", "pitch": -12, "harmonics": 0.3, "timbre": 0.25, "morph": 0.35,
                   "timbre_att": 0.6, "voice_mode": "Mono", "lpg_decay": 0.4}),
    ("FM Pluck", {"model": "FM 2-Op", "harmonics": 0.45, "timbre": 0.55, "morph": 0.3, "amp_mode": "Ping",
                  "lpg_decay": 0.45, "timbre_att": 0.5}),
    ("Formant Voice", {"model": "Grain Formant", "harmonics": 0.4, "timbre": 0.5, "morph": 0.4,
                       **ENV_AMP, **adsr(1, 60, 400, 0.8, 400), "mod_lfo1_timbre": 0.2, "lfo1_rate": 0.4}),
    ("Drawbar Organ", {"model": "Harmonic", "harmonics": 0.3, "timbre": 0.4, "morph": 0.3,
                       **ENV_AMP, **adsr(1, 3, 100, 1.0, 60)}),
    ("Wavetable Pad", {"model": "Wavetable", "harmonics": 0.25, "timbre": 0.4, "morph": 0.5,
                       **ENV_AMP, **adsr(1, 700, 800, 0.8, 1800), "polyphony": 6, "unison": 1,
                       "mod_lfo1_morph": 0.3, "lfo1_rate": 0.2, "lfo1_shape": "Triangle"}),
    ("Chord Stab", {"model": "Chords", "harmonics": 0.35, "timbre": 0.5, "morph": 0.4, "amp_mode": "Ping",
                    "lpg_decay": 0.4, "voice_mode": "Mono"}),
    ("Speech", {"model": "Speech", "harmonics": 0.6, "timbre": 0.5, "morph": 0.5,
                **ENV_AMP, **adsr(1, 5, 600, 0.9, 200)}),
    ("Swarm Pad", {"model": "Swarm", "harmonics": 0.4, "timbre": 0.4, "morph": 0.5,
                   **ENV_AMP, **adsr(1, 900, 800, 0.85, 2000), "polyphony": 4}),
    ("Noise Sweep", {"model": "Noise", "harmonics": 0.6, "timbre": 0.5, "morph": 0.6,
                     **ENV_AMP, **adsr(1, 300, 600, 0.7, 900), "mod_lfo1_timbre": 0.4, "lfo1_rate": 0.25}),
    ("Particle Drops", {"model": "Particle", "harmonics": 0.4, "timbre": 0.4, "morph": 0.7, "amp_mode": "Ping",
                        "lpg_decay": 0.7}),
    ("Plucked String", {"model": "Inharm. String", "harmonics": 0.2, "timbre": 0.5, "morph": 0.45}),
    ("Modal Bell", {"model": "Modal Resonator", "harmonics": 0.55, "timbre": 0.6, "morph": 0.65}),
    ("Kick", {"model": "Bass Drum", "harmonics": 0.45, "timbre": 0.45, "morph": 0.55}),
    ("Snare", {"model": "Snare Drum", "harmonics": 0.5, "timbre": 0.5, "morph": 0.45}),
    ("Hi-Hat", {"model": "Hi-Hat", "harmonics": 0.5, "timbre": 0.6, "morph": 0.3}),
]


def main():
    module = json.load(open(os.path.join(ROOT, "src", "module.json")))
    params = [p for p in module["capabilities"]["chain_params"] if p["key"] not in SKIP]
    by_key = {p["key"]: p for p in params}
    out = []
    for name, changes in SOUNDS:
        for k in changes:
            if k not in by_key:
                raise SystemExit("make_presets: %s: no parameter %r" % (name, k))
        values = {}
        for p in params:
            v = changes.get(p["key"], p["default"])
            if p.get("options") and isinstance(v, int):
                v = p["options"][v]
            values[p["key"]] = v
        out.append({"name": name, "values": values})
    path = os.path.join(ROOT, "vst", "presets.json")
    open(path, "w").write(json.dumps({"presets": out}, indent=1) + "\n")
    print("vst/presets.json: %d sounds" % len(out))


if __name__ == "__main__":
    main()
