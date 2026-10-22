# Porównanie historii do predykcji AR(4)

Wspólne nastawy: lambda=0.999, okno=221, próg 3 sigma, interpolacja serii 1–4. Zmieniono tylko wartość wpisywaną do historii po detekcji. Błędy wszystkich próbek nadal uczestniczą w estymacji progu. Zakwestionowane próbki nie aktualizują współczynników.

Test kontrolowany: dwa sygnały po 3 s, łącznie 62 uszkodzone próbki w impulsach długości 1–4, amplitudy dodanych zakłóceń 0.4–0.7; generator 193582. Przetestowano też te same sygnały bez zakłóceń. To proste sygnały syntetyczne, nie pełny model muzyki.

| Historia | Wykryte uszkodzone / 62 | Fałszywe detekcje | Uszkodzone objęte naprawą / 62 | Poprawne objęte naprawą |
|---|---:|---:|---:|---:|
| Historia oryginalna | 59 | 44 | 35 | 31 |
| Prognoza AR | 62 | 0 | 62 | 0 |
| Poprzednia zaakceptowana wartość | 62 | 13 | 62 | 13 |

W kontroli bez impulsów wszystkie warianty miały zero detekcji.

Test nagrań: całe 02.wav oraz pierwsze 3 s plików 01, 03, 04, 17, 22, 23. Brak czystych sygnałów odniesienia, więc liczby detekcji nie są miarą jakości. Próba zostaje przerwana, jeśli prognoza przekroczy 1e6 albo pojawią się wartości nieskończone — zabezpieczenie dotyczy wyłącznie testu, nie naprawia ani nie ogranicza modelu.

| Plik | Historia | Stabilny | Detekcje | Próbki objęte naprawą |
|---|---|---|---:|---:|
| 01.wav | Historia oryginalna | tak | 714 | 709 |
| 01.wav | Prognoza AR | tak | 2165 | 307 |
| 01.wav | Poprzednia zaakceptowana wartość | tak | 2055 | 307 |
| 02.wav | Historia oryginalna | tak | 2117 | 2112 |
| 02.wav | Prognoza AR | nie — przerwano | 1624 | 76 |
| 02.wav | Poprzednia zaakceptowana wartość | tak | 9895 | 1523 |
| 03.wav | Historia oryginalna | tak | 220 | 220 |
| 03.wav | Prognoza AR | nie — przerwano | 86 | 0 |
| 03.wav | Poprzednia zaakceptowana wartość | tak | 1589 | 112 |
| 04.wav | Historia oryginalna | tak | 259 | 259 |
| 04.wav | Prognoza AR | nie — przerwano | 142 | 0 |
| 04.wav | Poprzednia zaakceptowana wartość | tak | 1433 | 131 |
| 17.wav | Historia oryginalna | tak | 766 | 752 |
| 17.wav | Prognoza AR | nie — przerwano | 115 | 2 |
| 17.wav | Poprzednia zaakceptowana wartość | tak | 1291 | 722 |
| 22.wav | Historia oryginalna | tak | 325 | 325 |
| 22.wav | Prognoza AR | nie — przerwano | 750 | 286 |
| 22.wav | Poprzednia zaakceptowana wartość | tak | 1008 | 206 |
| 23.wav | Historia oryginalna | tak | 312 | 312 |
| 23.wav | Prognoza AR | tak | 635 | 581 |
| 23.wav | Poprzednia zaakceptowana wartość | tak | 570 | 486 |

Wniosek: prognoza AR była najlepsza na prostych sygnałach kontrolowanych, ale niestabilna w 5 z 7 prób nagrań. Powtarzanie poprzedniej zaakceptowanej wartości pozostało stabilne w 7 z 7 prób; jest bezpieczniejszym z dwóch zamienników. Nie wykazano jednak przewagi jakościowej nad historią oryginalną w rzeczywistej muzyce. Powtarzanie wartości także tworzy długie serie detekcji, które pomija obecna interpolacja. Wybór końcowy wymaga odsłuchu i poprawy obsługi takich serii.

Pliki 02_original.wav i 02_previous.wav umożliwiają odsłuch porównawczy. Wersji prediction nie zapisano dla 02.wav z powodu niestabilności. Notebook nie został zmieniony w ramach porównania.
