## Project Artifact SVG - PASVG

Wykorzystaj dane z turorialu i stworz do każdego pliku markdown odpowiednik w formacie SVG, wszystkie
pliki źródłowe (YAML, Dockerfile, docker-compose, manifesty, kod, zasoby) powinny być osadzone w SVG
 np. przez <foreignObject>, CDATA albo data URI.
Czyli jeden plik .svg staje się artefaktem źródłowym projektu, z którego generator potrafi wyciągnąć:
Dockerfile
docker-compose.yml
manifest.json


Na koniec wygeneruj z każdego projektu SVG, wedle tutoriala docelowy format:
apk (Android)
pwa.html
deb (Tauri, Linux)





## Dlaczego SVG się nadaje

✅ To XML, więc:

można w nim osadzać dowolne dane tekstowe (np. kod w <![CDATA[]]>),

można osadzać pliki binarne (base64 w xlink:href="data:..."),

każdy element może mieć id i data-* → semantyczne oznaczenie plików.
✅ W odróżnieniu od ZIP/TAR, SVG jest czytelne dla człowieka (edytowalne w Inkscape/Figma).
✅ To też wizualny manifest – możesz narysować architekturę, a jednocześnie embedować w niej realne pliki.


Pipeline (build z takiego SVG)

Parser (np. w Node.js, Pythonie):

otwiera .svg,

wyszukuje <pre data-filename="...">...</pre>,

zapisuje zawartość do odpowiednich plików.

Build system (npm, Docker, gradle, tauri, cargo itp.) działa na wygenerowanych plikach.

SVG pozostaje jedynym źródłem prawdy (artefakt projektu).

Zalety

Single source of truth: jeden .svg zamiast dziesiątek plików.

Human + machine readable: człowiek widzi architekturę, maszyna widzi pliki.

Przenośność: możesz wysłać komuś jeden plik SVG, a on może z niego wyciągnąć cały projekt.

Rozszerzalność: w tym samym pliku możesz embedować np. ikony, obrazy, schematy bazy danych.

