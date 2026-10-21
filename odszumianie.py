"""
Projekt 1 – wersja 5: konserwatywne usuwanie trzasków impulsowych.

Ta wersja NIE używa błędu AR jako samodzielnego kryterium usuwania próbki.
AR(4) jest nadal śledzony metodą RLS i parametry są zapisywane na wykresie,
ale detektor opiera się na nagłym, lokalnym odchyleniu próbki. Ogranicza to
ryzyko uznania całej muzyki za zakłócenie.

Instalacja:
    python -m pip install numpy soundfile matplotlib scipy

Uruchomienie:
    python odszumianie.py --input ./nagrania --output ./wyniki_v5
"""
import argparse
import glob
import os
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter

ORDER = 4
RLS_LAMBDA = 0.995
MAX_RUN = 4
MEDIAN_WINDOW = 7
ABS_THRESHOLD = 0.16       # próg bezwzględny dla WAV znormalizowanego do [-1, 1]
LOCAL_DIFF_MULTIPLIER = 8.0
PLOT_MAX_POINTS = 100_000


def robust_sigma(x):
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return 1e-6
    med = np.median(x)
    return max(1.4826 * np.median(np.abs(x - med)), 1e-6)


def get_runs(mask):
    ids = np.flatnonzero(mask)
    if not len(ids):
        return []
    chunks = np.split(ids, np.flatnonzero(np.diff(ids) > 1) + 1)
    return [(int(c[0]), int(c[-1])) for c in chunks]


def detect_impulses(x):
    """Detekcja lokalnych skoków, nie zaś dużej amplitudy samej w sobie."""
    n = len(x)
    if n < 5:
        return np.zeros(n, dtype=bool)

    # Różnica względem interpolacji sąsiadów dobrze reaguje na pojedynczy trzask.
    left = np.r_[x[0], x[:-1]]
    right = np.r_[x[1:], x[-1]]
    linear = 0.5 * (left + right)
    innovation = np.abs(x - linear)

    # Lokalna skala zmian liczona z pierwszych różnic.
    dx = np.diff(x, prepend=x[0])
    local_mad = median_filter(np.abs(dx), size=31, mode="reflect")
    threshold = np.maximum(ABS_THRESHOLD, LOCAL_DIFF_MULTIPLIER * local_mad)

    # Dodatkowy warunek: próbka musi wyraźnie odstawać od lokalnej mediany.
    med = median_filter(x, size=MEDIAN_WINDOW, mode="reflect")
    dev = np.abs(x - med)
    mask = (innovation > threshold) & (dev > threshold)

    # Przypadki na granicy pliku nie są rekonstruowane.
    mask[0] = False
    mask[-1] = False

    # W zadaniu założono serie maksymalnie 4-próbkowe. Dłuższych obszarów
    # nie usuwamy automatycznie, bo najpewniej są to fragmenty muzyki/transjenty.
    keep = np.zeros(n, dtype=bool)
    for a, b in get_runs(mask):
        if b - a + 1 <= MAX_RUN:
            keep[a:b+1] = True
    return keep


def repair_linear(x, mask):
    """Rekonstrukcja liniowa; dla serii do 4 próbek łączy poprawne końce."""
    y = x.copy()
    repaired = np.zeros(len(x), dtype=bool)
    n = len(x)
    for a, b in get_runs(mask):
        if b-a+1 > MAX_RUN or a == 0 or b == n-1:
            continue
        # Wymagane w poleceniu uzupełnianie interpolacją liniową.
        y[a:b+1] = np.linspace(x[a-1], x[b+1], b-a+3)[1:-1]
        repaired[a:b+1] = True
    return y, repaired


def track_ar4_rls(x):
    """Śledzenie AR(4) przez RLS; nie wykorzystuje go jako jedynego detektora."""
    n = len(x)
    a_hist = np.zeros((n, ORDER))
    if n <= ORDER + 1:
        return a_hist
    # Inicjalizacja z pierwszego fragmentu, odporna na początkowe trzaski.
    warm = min(max(100, int(0.05 * 22050)), max(ORDER+1, n//5))
    X, target = [], []
    for k in range(ORDER, warm):
        X.append([x[k-j-1] for j in range(ORDER)])
        target.append(x[k])
    if len(target) >= ORDER:
        a = np.linalg.lstsq(np.asarray(X), np.asarray(target), rcond=None)[0]
    else:
        a = np.zeros(ORDER)
    a = np.clip(a, -2.0, 2.0)
    P = np.eye(ORDER) * 10.0
    for k in range(ORDER, n):
        phi = np.array([x[k-j-1] for j in range(ORDER)])
        den = RLS_LAMBDA + phi @ P @ phi
        gain = P @ phi / max(den, 1e-12)
        err = x[k] - a @ phi
        a_new = a + gain * err
        P_new = (P - np.outer(gain, phi) @ P) / RLS_LAMBDA
        if np.all(np.isfinite(a_new)) and np.max(np.abs(a_new)) < 10:
            a = a_new
            P = 0.5 * (P_new + P_new.T)
        else:
            P = np.eye(ORDER) * 10.0
        a_hist[k] = a
    # Wypełnienie początkowych wartości, aby wykres nie wyglądał na pusty.
    a_hist[:ORDER] = a_hist[ORDER]
    return a_hist


def save_plots(x, y, mask, coeffs, sr, stem, outdir):
    t = np.arange(len(x)) / sr
    stride = max(1, len(x)//PLOT_MAX_POINTS)
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    ax[0].plot(t[::stride], x[::stride], lw=0.5)
    ax[0].set_title("Sygnał wejściowy – kanał 1")
    ax[1].plot(t[::stride], y[::stride], lw=0.5)
    ax[1].set_title("Sygnał po odszumianiu – kanał 1")
    ax[2].plot(t[::stride], (x-y)[::stride], lw=0.5, label="Zmiana po rekonstrukcji")
    ids = np.flatnonzero(mask)
    if len(ids):
        ids = ids[::max(1, len(ids)//5000)]
        ax[2].scatter(t[ids], (x-y)[ids], s=7, label="Naprawione próbki")
    ax[2].set_title(f"Naprawiono {int(mask.sum())} próbek")
    ax[2].set_xlabel("Czas [s]")
    for a in ax:
        a.set_ylabel("Amplituda")
        a.grid(True, alpha=0.25)
    ax[2].legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, stem + "_przebiegi.png"), dpi=130)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(12, 5))
    for j in range(ORDER):
        ax.plot(t[::stride], coeffs[::stride, j], lw=0.7, label=f"a{j+1}")
    ax.set_title("Zmiany parametrów modelu AR(4)")
    ax.set_xlabel("Czas [s]")
    ax.set_ylabel("Wartość parametru")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, stem + "_parametry_AR4.png"), dpi=130)
    plt.close(fig)


def process(path, outdir):
    data, sr = sf.read(path, always_2d=True, dtype="float64")
    out = np.empty_like(data)
    first = None
    for ch in range(data.shape[1]):
        x = data[:, ch]
        mask = detect_impulses(x)
        y, repaired = repair_linear(x, mask)
        out[:, ch] = y
        if ch == 0:
            first = (mask, track_ar4_rls(x))
    stem = os.path.splitext(os.path.basename(path))[0]
    sf.write(os.path.join(outdir, stem + "_odszumiony.wav"), out, sr, subtype="PCM_16")
    mask, coeffs = first
    save_plots(data[:, 0], out[:, 0], mask, coeffs, sr, stem, outdir)
    print(f"{os.path.basename(path)} -> {stem}_odszumiony.wav | "
          f"naprawiono {int(mask.sum())} próbek ({100*mask.mean():.3f}%) "
          f"w kanale 1")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Folder z oryginalnymi plikami WAV")
    parser.add_argument("--output", required=True, help="Folder na wynikowe WAV i wykresy")
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    files = sorted(glob.glob(os.path.join(args.input, "*.wav")))
    if not files:
        raise SystemExit("Nie znaleziono plików WAV w folderze wejściowym.")
    for path in files:
        process(path, args.output)


if __name__ == "__main__":
    main()
