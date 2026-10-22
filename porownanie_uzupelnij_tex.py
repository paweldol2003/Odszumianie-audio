import json
from pathlib import Path
p=Path('sprawozdanie/main.tex')
s=p.read_text(encoding='utf-8-sig')
rows=json.loads(Path('sprawozdanie/wyniki_AB.json').read_text())
assert len(rows)==10
s=s.replace('Wektor regresorów zawiera cztery poprzednie próbki:', 'Wektor regresorów zawiera cztery poprzednie wartości pomocniczej historii $z$. W wariancie A historia jest równa sygnałowi wejściowemu:')
s=s.replace(r'\varphi(k)=[x(k-1),x(k-2),x(k-3),x(k-4)]^T.', r'\varphi(k)=[z(k-1),z(k-2),z(k-3),z(k-4)]^T.')
s=s.replace('Wektor regresorów nadal pochodzi z sygnału wejściowego, więc zakłócenie może wpływać na kolejne prognozy.', 'Sposób tworzenia historii regresorów zależy od wariantu. W obu przypadkach bieżący błąd jest liczony względem oryginalnej próbki $x(k)$.')
section=r'''\subsection{Dwa warianty historii predykcji}
\textbf{Wariant A -- historia oryginalna.} Przyjęto $z_A(k)=x(k)$. Zakwestionowana próbka nie aktualizuje współczynników modelu, ale pozostaje w historii kolejnych predykcji.

\textbf{Wariant B -- ostatnia zaakceptowana wartość.} Po detekcji zakłócenia wartość w pomocniczej historii jest zastępowana przez poprzednią wartość tej historii:
\begin{equation}
z_B(k)=\begin{cases}
x(k), & \text{gdy próbka jest zaakceptowana},\\
z_B(k-1), & \text{gdy próbka jest zakwestionowana}.
\end{cases}
\end{equation}
Przy kilku detekcjach z rzędu powtarzana jest ostatnia zaakceptowana wartość. Zachowano cztery pozycje historii, więc model nadal ma rząd 4. Przed uruchomieniem detekcji historia jest równa sygnałowi wejściowemu.

Powtarzanie wartości służy do obliczania regresorów w wariancie B. Końcowy sygnał $y$ w obu wariantach powstaje przez interpolację liniową oryginalnego sygnału według maski danego wariantu. Błędy wszystkich próbek, również zakwestionowanych, nadal wchodzą do lokalnego oszacowania progu. Modele są inicjalizowane oddzielnie; porównanie zmienia wyłącznie sposób tworzenia historii.

'''
s=s.replace(r'\section{Detekcja zakłóceń}',section+r'\section{Detekcja zakłóceń}')
start=s.index(r'\section{Wyniki dla pięciu losowych nagrań}')
end=s.index(r'\section{Wnioski}',start)
part=r'''\section{Porównanie wariantów A i B}
Oba warianty przeliczono dla tych samych pięciu nagrań: \texttt{03.wav}, \texttt{04.wav}, \texttt{17.wav}, \texttt{22.wav} i \texttt{23.wav}, z nastawami podanymi wcześniej. Tabela obejmuje całe nagrania.

Detekcje oznaczają zakwestionowane próbki, a rekonstrukcja -- próbki objęte interpolacją. Pominięte serie nie spełniają limitu długości lub warunku dostępności obu sąsiadów. RMSE zmiany obliczono jako
\begin{equation}
D=\sqrt{\frac{1}{N}\sum_{k=0}^{N-1}[y(k)-x(k)]^2}.
\end{equation}
Wielkość $D$ opisuje ingerencję w wejście, a nie błąd względem czystej muzyki. Nie jest miarą skuteczności odszumiania.

\begin{center}
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{llrrrrr}
\toprule
Plik & Wariant & Detekcje & Rekonstr. & Udział [\%] & Pom. serie & $D$\\
\midrule
'''
for item in rows:
 part+=f"{item['file']} & {item['variant']} & {item['detected']} & {item['repaired']} & "+f"{item['percent']:.3f}".replace('.',',')+f" & {item['omitted_runs']} & "+f"{item['change_rmse']:.5f}".replace('.',',')+r'\\'+'\n'
part+=r'''\bottomrule
\end{tabular}
\end{center}

We wszystkich pięciu przykładach wariant B dał więcej detekcji i pominiętych serii. W czterech nagraniach objął interpolacją mniej próbek niż A; wyjątkiem jest plik \texttt{23.wav}, dla którego liczba ta wzrosła z 2093 do 3170. Powtarzanie jednej wartości może pogorszyć dopasowanie predykcji do zmieniającej się muzyki i podtrzymywać kolejne detekcje. Wyniki nie potwierdzają więc przewagi B dla całej procedury. Brak czystych nagrań odniesienia uniemożliwia wyznaczenie liczby prawdziwych i fałszywych detekcji.

Na wykresach lewa kolumna odpowiada A, a prawa B. Kolejne wiersze przedstawiają wynik na tle wejścia, różnicę wejście--wynik, współczynniki AR(4) i błąd z progiem. Odpowiadające sobie wykresy mają wspólne skale. Sygnały i błędy rysowane są ze wszystkich próbek; współczynniki pokazano co dziesiątą próbkę.
'''
for name in ['03','04','17','22','23']:
 part+='\n'+r'\clearpage'+'\n'+f'\\subsection{{Nagranie {name}.wav}}\n'
 part+=r'\begin{figure}[htbp]'+'\n'+r'\centering'+'\n'
 part+=f'\\includegraphics[width=\\linewidth]{{images/{name}_AB.png}}\n'
 part+=f'\\caption{{Porównanie nagrania \\texttt{{{name}.wav}}: A -- historia oryginalna; B -- ostatnia zaakceptowana wartość.}}\n'
 part+=r'\end{figure}'+'\n'
part+='\n'+r'\clearpage'+'\n'
s=s[:start]+part+s[end:]
start=s.index(r'\section{Wnioski}')
s=s[:start]+r'''\section{Wnioski}
W obu wariantach zastosowano AR(4), EW-LS z pomijaniem aktualizacji dla zakwestionowanych próbek, próg $3\sigma$ i interpolację liniową serii do czterech próbek. Zmiana historii nie zmienia rzędu modelu ani metody końcowej rekonstrukcji.

Wariant A dopuszcza wpływ wykrytego zakłócenia na kolejne regresory. Wariant B usuwa tę wartość z historii przez powtórzenie ostatniej zaakceptowanej próbki, lecz w badanych nagraniach tworzy więcej detekcji i pominiętych serii. Większa liczba detekcji nie oznacza lepszego usuwania trzasków. Ograniczenie naprawy do czterech kolejnych detekcji pozostaje istotne dla obu wariantów, ponieważ długość serii błędów predykcji może przekraczać długość rzeczywistego zakłócenia.

Do porównania odsłuchowego zapisano osobne pliki \texttt{NN\_A\_odszumiony.wav} i \texttt{NN\_B\_odszumiony.wav}. Ostateczna ocena wymaga porównania słyszalności trzasków i zachowania brzmienia przy tej samej głośności. Przedstawione statystyki nie zastępują tej oceny.

\end{document}
'''
p.write_text(s,encoding='utf-8')
