PROJEKT 1 – USUWANIE ZAKŁÓCEŃ IMPULSOWYCH

1. Wymagania
   Python 3.10+ (zalecany 3.11/3.12)
   Biblioteki: numpy, soundfile, matplotlib, scipy

2. Instalacja bibliotek
   python -m pip install numpy soundfile matplotlib scipy

3. Przygotowanie danych
   Utwórz folder, np. nagrania, i skopiuj do niego pliki WAV.

4. Uruchomienie
   python odszumianie.py --input ./nagrania --output ./wyniki_v5

5. Wyniki
   Dla każdego pliku powstaje:
   - *_odszumiony.wav
   - *_przebiegi.png
   - *_parametry_AR4.png
   WAV jest zapisywany w formacie PCM_16 z częstotliwością próbkowania wejścia.
   Każdy kanał jest przetwarzany osobno. Wykresy i liczba naprawionych próbek
   dotyczą tylko pierwszego kanału. Folder wynikowy jest tworzony automatycznie.
   Ponowne uruchomienie nadpisuje wyniki o tych samych nazwach.

6. Najważniejsze nastawy
   Stałe na początku odszumianie.py:
   ORDER = 4                      - rząd modelu AR
   RLS_LAMBDA = 0.995              - współczynnik zapominania RLS
   MAX_RUN = 4                    - limit długości zaznaczonej serii
   MEDIAN_WINDOW = 7              - okno mediany sygnału, w próbkach
   ABS_THRESHOLD = 0.16           - minimalny próg detekcji
   LOCAL_DIFF_MULTIPLIER = 8.0     - mnożnik lokalnej skali zmian
   PLOT_MAX_POINTS = 100_000       - parametr przerzedzania wykresów
   Lokalna skala zmian jest liczona filtrem medianowym w oknie 31 próbek.

7. Działanie obecnej wersji i strojenie
   Detektor porównuje próbkę z interpolacją jej sąsiadów i lokalną medianą.
   Oba odchylenia muszą przekroczyć próg będący maksimum ABS_THRESHOLD
   i LOCAL_DIFF_MULTIPLIER razy lokalna skala zmian. Zaznaczone serie do
   MAX_RUN próbek są zastępowane interpolacją liniową między ich sąsiadami.
   Pierwsza i ostatnia próbka nie są rekonstruowane.
   Model AR(4) jest śledzony przez RLS wyłącznie do wykresu parametrów;
   błąd predykcji AR nie jest używany przez obecny detektor.
   Wynik trzeba odsłuchać. Zwiększenie ABS_THRESHOLD lub
   LOCAL_DIFF_MULTIPLIER ogranicza liczbę detekcji; zmniejszenie zwiększa
   czułość i ryzyko zmiany poprawnych fragmentów muzyki.
   Znane ograniczenie: detektor może pominąć część lub całość trzasku
   wielopróbkowego. MAX_RUN = 4 nie gwarantuje wykrycia całej takiej serii.

8. Wymagania z Instrukcja.pdf
   Dane zadania: około 20 sekund nagrania, próbki 16-bitowe, 22050 Hz.
   Wymagany model: AR(4), parametry śledzone algorytmem EW-LS.
   Wymagany detektor: bezwzględny błąd predykcji przekraczający trzykrotnie
   lokalną wartość odchylenia standardowego błędu resztowego.
   Rekonstrukcja: interpolacja liniowa z obsługą serii do 4 próbek.
   Ocena jakości: odsłuchowa.
   Do zaliczenia: sprawozdanie z opisem procedur, uzasadnieniem nastaw
   i wykresami parametrów, kod źródłowy oraz wynikowy plik WAV.
   Obecna wersja nie realizuje wymaganego detektora opartego na błędzie AR.
   Przed oddaniem projektu należy go dostosować do polecenia i zweryfikować
   rekonstrukcję serii zakłóceń do 4 próbek.
