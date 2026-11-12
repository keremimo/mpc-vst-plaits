/* Slide and tie from a sequencer (CC 84 names the key the next note goes on from, CC 68 down for a tie), as Melodee
 * sends them for Slide and Tie steps. Exits 1 on any failure. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "params.h"
typedef struct AEffect AEffect;
typedef intptr_t (*cb)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
struct AEffect { int32_t magic; intptr_t (*d)(AEffect*,int32_t,int32_t,intptr_t,void*,float);
 void*p; void (*setP)(AEffect*,int32_t,float); float (*getP)(AEffect*,int32_t);
 int32_t np,npar,ni,no,flags; intptr_t r1,r2; int32_t a,b,c; float io; void*obj,*user; int32_t uid,ver;
 void (*pr)(AEffect*,float**,float**,int32_t); void*pdr; char f[56]; };
typedef struct { int32_t type,byteSize,deltaFrames,flags,noteLength,noteOffset; unsigned char m[4]; char x[4]; } ME;
typedef struct { int32_t n; intptr_t r; void* ev[2]; } EV;
extern AEffect* VSTPluginMain(cb);
static intptr_t host(AEffect*e,int32_t op,int32_t i,intptr_t v,void*p,float o){
    static double ti[16];
    if (op == 7) { ti[4] = 120.0; ((int32_t*)&ti[8])[5] = 1 << 10; return (intptr_t)ti; }
    return 0;
}
#define SR 44100
#define BLK 128
static float buf[SR * 4];
static int fails;
static void midi(AEffect *a, int s, int d1, int d2) {
    ME m = {1, sizeof(ME), 0, 0, 0, 0, {(unsigned char)s, (unsigned char)d1, (unsigned char)d2, 0}, {0}};
    EV ev = {1, 0, {&m, 0}};
    a->d(a, 25, 0, 0, &ev, 0);
}
static void on(AEffect *a, int n) { midi(a, 0x90, n, 100); }
static void off(AEffect *a, int n) { midi(a, 0x80, n, 0); }
/* Renders ms of audio; returns how many samples went into buf. */
static int run(AEffect *a, int ms) {
    float L[BLK], R[BLK], *o[2] = {L, R};
    int n = (int)((long)ms * SR / 1000 / BLK), w = 0;
    for (int k = 0; k < n; k++) {
        a->pr(a, 0, o, BLK);
        if (w + BLK <= (int)(sizeof buf / sizeof buf[0])) { memcpy(buf + w, L, sizeof L); w += BLK; }
    }
    return w;
}
static double rms(int n) { double s = 0; for (int i = 0; i < n; i++) s += buf[i] * buf[i]; return sqrt(s / (n ? n : 1)); }
static double tone(int n, int note) {   /* Goertzel magnitude at a MIDI note's fundamental */
    double w = 2 * M_PI * 440.0 * pow(2.0, (note - 69) / 12.0) / SR, c = 2 * cos(w), s1 = 0, s2 = 0;
    for (int i = 0; i < n; i++) { double s = buf[i] + c * s1 - s2; s2 = s1; s1 = s; }
    return sqrt(s1 * s1 + s2 * s2 - c * s1 * s2) / n;
}
static void check(const char *what, int ok, double x, double y) {
    printf("%s  %-58s (%.5f vs %.5f)\n", ok ? "PASS" : "FAIL", what, x, y);
    if (!ok) fails++;
}
static int idx(const char *k) { for (int i = 0; i < NPARAMS; i++) if (!strcmp(PARAMS[i].key, k)) return i; return -1; }
static void set_opt(AEffect *a, const char *key, const char *name) {
    int i = idx(key);
    for (int o = 0; o < PARAMS[i].nopts; o++)
        if (!strcmp(PARAMS[i].opts[o], name)) { a->setP(a, i, (float)o / (PARAMS[i].nopts - 1)); return; }
    printf("no option %s for %s\n", name, key); fails++;
}
static void set(AEffect *a, const char *key, float norm) { a->setP(a, idx(key), norm); }
static void silence(AEffect *a) { midi(a, 0xB0, 123, 0); run(a, 3000); }

static void slide_to(AEffect *a, int from, int to, int tie) {   /* in Melodee's order (PluginEngine::slide) */
    if (tie) midi(a, 0xB0, 68, 127);
    midi(a, 0xB0, 84, from);
    on(a, to);
    off(a, from);
    if (tie) midi(a, 0xB0, 68, 0);
}

int main(void) {
    AEffect *a = VSTPluginMain(host);
    int n;

    /* A slide moves the held voice to the new key: the old pitch is gone, no second voice. */
    set_opt(a, "model", "Virtual Analog"); set_opt(a, "voice_mode", "Poly"); set(a, "lpg_decay", 0.1f);
    on(a, 57); run(a, 300);
    slide_to(a, 57, 64, 0); run(a, 300);
    n = run(a, 300);
    check("slide: the voice now sounds E", tone(n, 64) > 4 * tone(n, 57), tone(n, 64), tone(n, 57));
    off(a, 64); run(a, 50);
    n = run(a, 300);
    double after = rms(n);
    on(a, 60); run(a, 300); n = run(a, 300); double played = rms(n);
    check("slide: releasing the new key releases the voice", after < 0.2 * played, after, played);
    off(a, 60); silence(a);

    /* A slide glides (60 ms with GLIDE at 0); a tie jumps. Compare E in the first 15 ms after each. */
    double early[2];
    for (int tie = 0; tie < 2; tie++) {
        on(a, 57); run(a, 300);
        slide_to(a, 57, 64, tie);
        n = run(a, 15); early[tie] = tone(n, 64);
        off(a, 64); silence(a);
    }
    check("slide glides, tie jumps (E in the first 15 ms)", early[1] > 1.5 * early[0], early[1], early[0]);

    /* Neither restrikes: Modal only sounds when struck, so a slid voice stays quiet; a played note rings. */
    set_opt(a, "model", "Modal Resonator"); set(a, "morph", 0.4f);
    double r[2];
    for (int slid = 0; slid < 2; slid++) {
        on(a, 57); run(a, 1500);
        if (slid) slide_to(a, 57, 61, 1); else { on(a, 61); off(a, 57); }
        n = run(a, 200); r[slid] = rms(n);
        off(a, 61); silence(a);
    }
    check("tie doesn't restrike, a played note does", r[0] > 3 * r[1], r[0], r[1]);

    /* With nothing held on the named key, the note plays as ever. */
    set_opt(a, "model", "Virtual Analog");
    slide_to(a, 50, 64, 0); run(a, 200);
    n = run(a, 300);
    check("slide from an unheld key plays the note", rms(n) > 1e-3 && tone(n, 64) > 4 * tone(n, 50), tone(n, 64), tone(n, 50));
    off(a, 64); silence(a);

    /* Mono: the slid-to key is the held one; releasing it ends the note. */
    set_opt(a, "voice_mode", "Mono");
    on(a, 57); run(a, 200);
    slide_to(a, 57, 64, 0); run(a, 300);
    n = run(a, 300);
    check("mono slide: sounds E", tone(n, 64) > 4 * tone(n, 57), tone(n, 64), tone(n, 57));
    off(a, 64); run(a, 50);
    n = run(a, 300);
    check("mono slide: releasing E releases the note", rms(n) < 0.2 * played, rms(n), played);
    silence(a);

    printf(fails ? "%d FAILED\n" : "all passed\n", fails);
    return fails ? 1 : 0;
}
