#!/usr/bin/env python3
"""MPC Plaits' MPC page: writes vst/layout.conf (mpc-vst-plugins' Force Shadow widget syntax) from the tabs below.

    python3 tools/make_layout.py

Every tab is two rows of slots. A row holds frames (a titled group of slots, left to right). A control's kind follows
its parameter in src/module.json: a number is a knob, Off/On a toggle, up to nine options a column of segments
(every option on screen), more a pop-up list. The look is Melodee's NIGHT palette with Rubik (vst/skin.css).

Q-Links follow the controls left to right, row 1 then row 2, in threes: Melodee shows a plug-in's parameters three
at a time on K1-K3, in the order of its Q-Link pages, so each three below is one Melodee row. A control written
("key", "LABEL", False) is drawn but left off the Q-Links (switches that are set once). A knob may carry its own
on/off switch under it: ("key", "LABEL", "switch_key").
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")

W, Y_OFF = 1280, 86            # MPC's plugin area (1280x628), from y=86 in the layout's coordinates
X0, Y0, ROW = 20, Y_OFF + 14, 304
WIDTH = W - 2 * X0
FIRST = 100                    # a segment column's first option (its centre) under the row's top

ACCENT, ACCENT_HI = "4FC3D9", "8FDCEB"
THEME = {
    "bg": "17141F", "panel": "1D1926", "line": "2E2939", "ink": "F3EEF8", "ink_dim": "9A93A8", "ink_faint": "5A5468",
    "accent": ACCENT, "accent_hi": ACCENT_HI, "knob_face": "262033", "knob_ring": "3A3448", "knob_dot": "F3EEF8",
    "bar": "1A1722", "lcd": "221E2C", "box": "1D1926", "btn_bg": "262033", "btn_text": "F3EEF8",
    "seg_active": ACCENT, "seg_inactive": "221E2C", "seg_active_tx": "17141F", "tab_on": ACCENT, "tab_on_tx": "17141F",
}

ATT = ("ATTENUVERTERS", [("timbre_att", "TIMBRE"), ("fm_att", "FM"), ("morph_att", "MORPH")])


def env(n):
    return [("ENV %d" % n, [("env%d_attack" % n, "ATTACK"), ("env%d_decay" % n, "DECAY"),
                            ("env%d_sustain" % n, "SUSTAIN"), ("env%d_release" % n, "RELEASE"),
                            ("env%d_retrig" % n, "RETRIG")])]


def lfo(n):
    # SYNC DIV last: its list opens over the slots to its right
    return [("LFO %d" % n, [("lfo%d_shape" % n, "SHAPE"), ("lfo%d_rate" % n, "RATE"), ("lfo%d_phase" % n, "PHASE"),
                            ("lfo%d_per_voice" % n, "PER VOICE", False), ("lfo%d_retrig" % n, "RETRIG"),
                            ("lfo%d_sync" % n, "SYNC"), ("lfo%d_div" % n, "SYNC DIV")])]


DESTS = [("pitch", "> PITCH"), ("harm", "> HARM"), ("timbre", "> TIMBRE"), ("morph", "> MORPH")]


def mod_row(sources):
    return [(title, [("mod_%s_%s" % (src, d), label, "mod_%s_%s_on" % (src, d)) for d, label in DESTS])
            for src, title in sources]


def amounts_row(first):
    return [("SOURCE %d" % s, [("asg_%d_%d" % (s, d), "> DEST %d" % d, "asg_%d_%d_on" % (s, d)) for d in range(1, 5)])
            for s in (first, first + 1)]


TABS = [
    ("PLAITS", [
        [("MODEL", [("model", "MODEL"), ("pitch", "FREQ"), ("harmonics", "HARMONICS"),
                    ("timbre", "TIMBRE"), ("morph", "MORPH"), ("aux_mix", "OUT / AUX")])],
        [ATT, ("LPG", [("amp_mode", "AMP"), ("lpg_color", "COLOR"), ("lpg_decay", "DECAY")])],
    ]),
    ("VOICE", [
        [("VOICES", [("voice_mode", "MODE"), ("polyphony", "NOTES"), ("unison", "UNISON"),
                     ("detune", "DETUNE"), ("spread", "SPREAD"), ("pan", "PAN")])],
        [("PLAY", [("glide_ms", "GLIDE"), ("bend_range", "BEND"), ("velocity_curve", "VEL CURVE"),
                   ("poly_aftertouch_curve", "AT CURVE", False)]),
         ("FILTER", [("filter_mode", "TYPE"), ("filter_cutoff", "CUTOFF"), ("filter_resonance", "RESO")])],
    ]),
    # ENV 1 shapes the level in the AMP modes ENV and DRONE: VOLUME sits with it. TRIG RATE retriggers the
    # envelopes (and Plaits) while a key is held.
    ("ENV", [
        env(1) + [("OUT", [("volume", "VOLUME")])],
        env(2) + [("RETRIG", [("trig_rate", "TRIG RATE")])],
    ]),
    ("LFO", [lfo(1), lfo(2)]),
    ("CYCLE", [
        [("CYCLE", [("cycle_attack_ms", "RISE"), ("cycle_decay_ms", "FALL"), ("cycle_shape", "SHAPE"),
                    ("cycle_bipolar", "BIPOLAR", False), ("cycle_retrig", "RETRIG", False)])],
        [("RANDOM", [("random_mode", "MODE"), ("random_rate", "RATE"), ("random_slew", "SLEW"),
                     ("random_retrig", "RETRIG"), ("random_sync", "SYNC"), ("random_div", "SYNC DIV")])],
    ]),
    ("ROUTES", [
        [("SOURCES", [("asg_src%d" % n, "SOURCE %d" % n) for n in range(1, 5)]),
         ("DESTINATIONS", [("asg_dst%d" % n, "DEST %d" % n) for n in range(1, 5)])],
        [],
    ]),
    ("ASSIGN", [amounts_row(1), amounts_row(3)]),
    ("MOD", [mod_row([("lfo1", "LFO 1"), ("env2", "ENV 2")]), mod_row([("cyc", "CYCLE"), ("rnd", "RANDOM")])]),
]


def control(p, label, cx, cy, slot, row_top):
    opts = p.get("options")
    key = p["key"]
    if not opts:
        return ['knob cx=%d cy=%d r=40 label="%s" key=%s' % (cx, cy, label, key)]
    if [o.lower() for o in opts] == ["off", "on"]:
        return ['toggle cx=%d cy=%d label="%s" key=%s' % (cx, cy, label, key)]
    names = ",".join(o.upper() for o in opts)
    if len(opts) <= 9:
        # Every option on screen, a row 2 px apart, as tall as fits above the frame's foot. enum_h with a row per
        # option (not enum_v): its label sits a fixed 38 px over the first option, clear of the frame's title.
        n = len(opts)
        sh = min(34, 2 * (ROW - 14 - FIRST - 2 * n) // (2 * n - 1))
        return ['enum_h cx=%d cy=%d label="%s" key=%s options="%s" sw=%d sh=%d rows=%d'
                % (cx, row_top + FIRST, label, key, names, slot - 24, sh, n)]
    return ['popup cx=%d cy=%d w=%d h=40 label="%s" key=%s options="%s" wheel=1' % (cx, cy, slot - 18, label, key, names)]


def tab_lines(name, rows, params):
    out = ["", "[tab %s]" % name]
    slots = max([6] + [sum(len(cs) for _, cs in frames) for frames in rows])
    slot = WIDTH // slots
    order = []
    for r, frames in enumerate(rows):
        col = 0
        y = Y0 + r * ROW
        for title, controls in frames:
            n = len(controls)
            out.append('frame x=%d y=%d w=%d h=%d title="%s"' % (X0 + col * slot + 4, y + 4, n * slot - 8, ROW - 12, title))
            for c in controls:
                key, label = c[0], c[1]
                extra = c[2] if len(c) > 2 else None
                if key not in params:
                    raise SystemExit("layout: no parameter %r" % key)
                cx = X0 + col * slot + slot // 2
                cy = y + ROW // 2 + (-24 if extra else 14)   # a knob with a switch sits higher, clear of it
                out += control(params[key], label, cx, cy, slot, y)
                if extra:   # the knob's own on/off switch, under it
                    if extra not in params:
                        raise SystemExit("layout: no parameter %r" % extra)
                    out.append('toggle cx=%d cy=%d label="ON" key=%s' % (cx, y + ROW - 50, extra))
                if extra is not False:
                    order.append(key)
                col += 1
    if len(order) > 16:
        raise SystemExit("layout: tab %s has %d Q-Links (16 at most)" % (name, len(order)))
    out.append('qlinks "%s" = %s' % (name, ",".join(order)))
    return out, order


def main():
    module = json.load(open(os.path.join(ROOT, "src", "module.json")))
    params = {p["key"]: p for p in module["capabilities"]["chain_params"]}
    lines = ["# generated by tools/make_layout.py: MPC Plaits on MPC's 1280x628 plugin area, Melodee's NIGHT palette"]
    lines += ["theme_%s=%s" % kv for kv in THEME.items()]
    lines.append("art_css=skin.css")
    body, total = [], 0
    for name, rows in TABS:
        tab, order = tab_lines(name, rows, params)
        body += tab
        if name == TABS[0][0]:
            lines.append("qlinks_track = %s" % ",".join(order))
        total += len(order)
    lines += body
    open(os.path.join(ROOT, "vst", "layout.conf"), "w").write("\n".join(lines) + "\n")
    print("vst/layout.conf: %d tabs, %d Q-Link parameters" % (len(TABS), total))


if __name__ == "__main__":
    main()
