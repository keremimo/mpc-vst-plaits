/* Every factory sound (vst/presets.json) plays: one note per sound, a peak that is heard and does not clip, and no
 * NaN. Prints each sound's peak and RMS. Exits 1 on any failure. */
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

int main(void) {
    AEffect *a = VSTPluginMain(host);
    int programs = a->np;
    check("there are factory sounds", programs > 1, programs, 1);
    for (int p = 0; p < programs; p++) {
        char name[64] = {0};
        a->d(a, 2, 0, p, 0, 0);            /* effSetProgram */
        a->d(a, 5, 0, 0, name, 0);         /* effGetProgramName */
        run(a, 50);
        on(a, 60); int n = run(a, 1200); off(a, 60);
        double peak = 0; int bad = 0;
        for (int i = 0; i < n; i++) { if (!isfinite(buf[i])) bad = 1; if (fabs(buf[i]) > peak) peak = fabs(buf[i]); }
        char what[96]; snprintf(what, sizeof what, "%-16s peak %.3f rms %.4f", name, peak, rms(n));
        check(what, !bad && peak > 0.02 && peak < 1.0, peak, rms(n));
        silence(a);
    }
    printf(fails ? "%d FAILED\n" : "all passed\n", fails);
    return fails ? 1 : 0;
}
