PROJEKT 1 – USUWANIE ZAKŁÓCEŃ IMPULSOWYCH

1. Wymagania
   Python 3.10+ (zalecany 3.11/3.12)
   Biblioteki: numpy, soundfile, matplotlib

2. Instalacja bibliotek
   python -m pip install numpy soundfile matplotlib

3. Przygotowanie danych
   Utwórz folder, np. nagrania, i skopiuj do niego pliki WAV.

4. Uruchomienie
   python odszumianie.py --input ./nagrania --output ./wyniki

5. Wyniki
   Dla każdego pliku powstaje:
   - *_odszumiony.wav
   - *_przebiegi.png
   - *_parametry_AR4.png

6. Najważniejsze nastawy
   R = 4
   LAMBDA = 0.995
   DETECTION_MULTIPLIER = 3.0
   WARMUP_SECONDS = 0.20
   RESIDUAL_WINDOW = 2205 próbek (0,1 s przy 22050 Hz)

7. Uwaga
   Wynik trzeba odsłuchać. Jeśli algorytm usuwa zbyt dużo poprawnych fragmentów,
   zwiększ DETECTION_MULTIPLIER np. do 3.5 lub 4.0. Jeśli trzaski pozostają,
   spróbuj 2.5, kontrolując, czy nie pogarsza się brzmienie muzyki.
