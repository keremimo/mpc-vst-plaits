#!/usr/bin/env bash
# Build both targets and package dist/:
#   MPC-Plaits-<version>-mpc-armv7.zip    Gen1 MPC OS devices and Force (mpc-vst-plugins tools/release.py: install.sh, INSTALL.md)
#   MPC-Plaits-<version>-mpc-aarch64.zip  Gen2 MPC OS devices
#   MPC-Plaits-<version>-mpc-sample.zip   the aarch64 plug-in folder alone, for Melodee: unzip into Plugins/ on the card
# Needs Docker and an mpc-vst-plugins checkout (MPC_VST, default ../mpc-vst-plugins).
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
MPC_VST="${MPC_VST:-$here/../mpc-vst-plugins}"
MPC_VST="$(cd "$MPC_VST" && pwd)"
version="$(python3 -c 'import json,sys; v=json.load(open(sys.argv[1]))["version"]; print("%d.%d.%d" % (v // 1000, v // 100 % 10, v % 100))' "$here/vst/vst.json")"

[ "${SKIP_BUILD:-0}" = 1 ] || MPC_VST="$MPC_VST" "$here/build.sh"
skin="$(cd "$here/vst/build/skin" && ls -d */ | head -1)"; skin="${skin%/}"
rm -rf "$here/dist"; mkdir -p "$here/dist"
about="All 24 Plaits models with voices, envelopes, LFOs and two modulation matrices; Melodee's look and Slide/Tie."
for arch in armv7 aarch64; do
  so="$here/vst/build/plaits.so"; [ "$arch" = aarch64 ] && so="$here/vst/build/aarch64/plaits.so"
  python3 "$MPC_VST/tools/release.py" --so "$so" --skin "$here/vst/build/skin/$skin" \
    --entry "$here/vst/build/pluginlist-entry.xml" --version "$version" --about "$about" -o "$here/dist"
done

# The MPC Sample zip: the aarch64 release's portable plug-in folder and its manifest, nothing else.
python3 - "$here/dist" "$version" "$skin" <<'EOF'
import sys, zipfile, glob, os
out, version, skin = sys.argv[1:]
src = glob.glob(os.path.join(out, "*-%s-mpc-aarch64.zip" % version))[0]
dst = src.replace("-mpc-aarch64.zip", "-mpc-sample.zip")
with zipfile.ZipFile(src) as z, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as w:
    names = z.namelist()
    top = names[0].split("/")[0]
    prefix = "%s/portable/%s/" % (top, skin)
    for n in sorted(names):
        if n.startswith(prefix) and not n.endswith("/"):
            info = zipfile.ZipInfo(skin + "/" + n[len(prefix):], (2026, 1, 1, 0, 0, 0))
            info.external_attr = z.getinfo(n).external_attr
            w.writestr(info, z.read(n), zipfile.ZIP_DEFLATED)
    manifest = "%s/mpc-plugin.json" % top
    if manifest in names:
        info = zipfile.ZipInfo(skin + "/mpc-plugin.json", (2026, 1, 1, 0, 0, 0))
        w.writestr(info, z.read(manifest), zipfile.ZIP_DEFLATED)
print(dst)
EOF
(cd "$here/dist" && shasum -a 256 *.zip > SHA256SUMS.txt && cat SHA256SUMS.txt)
