
udokumentuj zmiany i stworz dokumentacje z linkowaniami  z README.md i docs/*.md, plan był jak poniżej, co zostało już zaimplementowane?
w examples rozbuduj o kolejen przykłady z ostatnimi zmianami

uzywaj komendy whyml run, ktora domyslnie uruchomi manifest.yaml ze strona
lub 
whyml run -f manifest.yaml -p 8080 -h localhost
lub
whyml run -f manifest.yaml --port 80 --host web.local --tls-provider letsencrypt
komdnea powinna korzystac z caddy i generowac pliki caddy aby mozna bylo potem uzyc tego do produkcji

dodatkowo do konwersji używaj takiej bliskiej naturalnego języka nomenklatury
whyml --from manifest.yaml --to index.html -as spa

pozwalaj w manifescie zalaczac po prostu pliki html, vue, react, rozne theme, templates, itd
- stworz generator aplikacji artefaktów PWA SPA APK, SVG (as PWA app), docker service, tauri app
- pozwol na integracje roznych danych, typu globalne zmienne z .env ze wskazaniem pliku, np config.json, package.json, ...

CDN Integration: Automated asset deployment
Real-Time Collaboration: Multi-user manifest editing
Visual Editor: GUI for manifest creation


tutaj jest stara wersja: /home/tom/github/tom-sapletta-com/webpage.yaml
jesli to pomoże to sprawdz co może juz zostało poporawnie zaimplementowano albo zainsiipruj sie rozwizaniami
ktore tutaj trzeba bedzieie zaimplementować

potrzebne sa przyklady do testowania z roznymi jezykami, aby np łączyć różne frameworki w ramach jednej strony www
do tego potrzebne są predefiniowane środowiska docker, które powinny być uruchamiane do wygenerowania pełnego html
dozwol na inne metody, jeśli są prostsze, aby generować pliki wynikowe html z różnycmi opcjami, np kompresja, optymalizacja css, js, itd


daj drugi wariant [test-manifest.yaml](test-manifest.yaml) gdzie kod html z yaml 
znajduje sie w sosobnym pliku .html, ktyory jest ładowany i renderowany, 
zamiast byc dodawany sam kod, dodajemy plik jako moduł
taki moduł w osobnym pliku powinien być ładowany dynamicznie,
z możliwoscia zamiany etykiet jeśli są tam używane jakieś formy zmiennych 
np w podwójnych klamrach {{VAR}} lub w php <?=VAR ?>

w rozwiązniu serwera:
whyml run -f test-manifest.yaml --watch --api-debug
dodaj warstwe API, ktora w momencie startu http://localhost:8080/
czyli http://localhost:8080/api/health
http://localhost:8080/api/debug/logs
http://localhost:8080/api/debug/logs/error/
chodzi o to by możliwe było używanie usług w róznych ekosystemach i analiza zachowań usługi
wyczytywanie błędów

Jak ładować wiele manifestow z jednego folderu, ktore maja meidzy soba zaleznosci sa ladowane jako komponenty a główny je włącza do całej mapy strony
jak łączyć ze sobą różne formaty, jak wygenerować cłą sitemap.xml?

whyml run -f test-manifest.yaml --watch --rss
dodaj do server opcję RSS, ktora ma za zadanie informowanie o zmianach na stronie
wynikajace z --watch obejmujace nie tylko strukture ale i tresc

podaj przyklad uruchomienia na produkcji z domena i tls na porcie 80 


Install dependencies: pip install -r requirements.txt
Test examples: Run the example scripts in examples/
Create your first app: Use whyml run with your manifest
Explore generators: Try whyml generate pwa for complete apps
Deploy production: Use Caddy integration for HTTPS deployment



Fix PWA generators to only cache existing assets and provide default icons
Add RSS feed functionality for --watch changes
Implement template variable substitution ({{VAR}} and )
Update HTML converter to support external_content, variables, config, dependencies
Add support for loading multiple manifests with dependencies
Add sitemap.xml generation capability





dodaj testowanie pobranej strony
 whyml scrape https://example.com --output scraped-manifest.yaml
Successfully scraped https://example.com to scraped-manifest.yaml

pobierz strone html , przekonwertuj na yaml i z yaml do html i porownaj te dwie wersje 
czy oryginalna rozni sie od tej regenrowanej z manifestu yaml?
 
Dodaj więcej parametrow, ktore pozwolą na uproszczenie struktury yaml manifestu, 
np pomijając duże zagnieżdzenia, chodzi o to aby moc zrobic prostsza strone na bazie informacji, tekstu jaki zawiera strona zrodlowa, 
np przy refaktoringu starej wersji przydaje sie zrobienie protszej reprezentacji i mozna ominac zagniezdzenia
albo przy realizacji projektu na rozne platformy mozna uproscic, albo przy monitorowaniu stron mozna wygenerowac prostsza reprezentacje, ktora nie bedzie wrazaliwa na drobne zmiany zagniezdzen strukutry html, podczas gdy np etykiety, contnet text beda te same

upraszczajac strukture html poprzez mniejszenie zagneizdzen, np:


                - div:
                    class: entry-data-wrapper entry-data-wrapper-archive
                    children:
                    - div:
                        class: entry-header-wrapper entry-header-wrapper-archive
                        children:
                        - div:
                            class: entry-meta entry-meta-header-before
                            children:
                              ul:
                                children:
                                  li:
                                    children:
                                      span:
                                        class: post-first-category
                                        children:
                                          a:
                                            href: https://tom.sapletta.com/category/idea-en/
                                            title: Idea
                                            text: Idea
                        - header:
                            class: entry-header
                            children:
                              h1:
                                class: entry-title
                                children:
                                  a:
                                    href: https://tom.sapletta.com/tools-en/dev-environment-for-fast-development-with-cubieboard-mini-pc-and-switch-without-virtualization/
                                    text: dev environment for fast development with
                                      odroid xu4, mini PC and switch, without virtualization


Stworz tez opcje do generowanie z pliku zrodlowego, np. html tylko sekcji w yaml "analysis" lub tylko sekcji "imports" 



whyml scrape https://example.com --section metadata --section structure
ta komenda nie powinna generowac analysis

Oto zestaw kolejnych promptów, które mogą poprowadzić rozwój WhyML w kierunku pełnej konkurencyjności względem rozwiązań enterprise, OCI i manifestów w ekosystemie Kubernetes:
Production Deployment - All features examples, tested and documented
User Testing - Comprehensive examples and documentation available
Future Enhncements - Multi-manifest dependencies and sitemap generation remain as optional medium/low priority features




zrob w docs/tutorials/ kolejne przyklady jakie mozna zaimplementowac krok po kroku:
- stworzenie kilku stron html z menu poprzez polaczenie kilku plikow yaml z zaleznosciami z php i uruchomienie z docker
- stworzenie pliku SVG z menu, metadanymi, mediami jako datauri odtwrazanymi przyotwarciu w przegladarce poprzez polaczenie z php i uruchomienie z docker
- tworzenie aplikacji tauri z przykładowej strony skonwerrtowanej za pomoca whyml do tauri
- stworzenie react, vue, pwa, spa za pomoca przykladowej strony skonwerttowanej z http do yaml do finalnej wersji
- Stworzenie przykladowej aplikacji na android, windows, linux za pomoca manifestu apk.yaml z przykladami komend i uzycia



skrypt generowac zrzut ekranu strony zrodlowej i wygenerowanych i
stworzyc dokumentacje na koniec z porownaniem i podlinkowanymi plikami, rowniez manifestow
Continue with a smaller test run to verify specific areas (e.g., just converter tests)
Proceed with documenting the complete automation success since the core functionality is working


zrob skrypt, ktory bedzie pobieral z listy z pliku konkretne strony www
zapisywal kazda domene w osobnym folderze:
 project/url.list.txt
 project/[domain]/source/index.html
 project/[domain]/source/index.png
 project/[domain]/manifest.yaml
 project/[domain]/html/index.html
 project/[domain]/html/index.png
 project/[domain]/php/index.php
 project/[domain]/vue/index.vue
 project/[domain]/js/index.js
 project/[domain]/test/index.ts
 project/[domain]/react/index.tsx


zrob docker compose, ktory będzie uruchamiał pod kolejnym portem zaczynając 
od 8010 kolejne podfoldery wybranego projektu, każda strona ma inne srodowisko w natywnych technologiach dla podfodleruy:
np. html to zwykła statyczna strona, ale php to już php 8.2 itd  
czyli dla przykładowego projektu example_com
html = port 8011, itd...
[html](project/example_com/html) 8011
[js](project/example_com/js) 8012
[php](project/example_com/php) 8013
[react](project/example_com/react) 8014
[source](project/example_com/source) 8015
[ts](project/example_com/ts) 8016
[vue](project/example_com/vue) 8017
Dodatkowo pokaż w podsumowaniu na port 8010  ale do podgladu w iframe
Dodatkowo strona na poczatku powinna pokazywać skrypt generowac zrzut ekranu strony zrodlowej i rowneiz w oknie iframe to co zostalo pobrane do source
Celem tego rozwiaznaia jest podsumowanie działania rozwiazania do konkwersji strony html na inne formaty, aby wiuzalnie ocenić




zrob refaktoryzacje paczki w folderze whyml
podziel większe pliki na mniejsze, podziel jak reużywalne komponenty, aby bylo łatwiej rozwiazywac problemy i rozbudowwywać funkcjonalność whyml
stworz dodatkowe komponenty, wykorzystującye whyml, które będą osobną paczką python wykorzystującą whyml
stworz oddzielne paczki w taki sposob aby były ze sobą komplementarne, bez duplikacji funkcji, odpowiedzialności





***

### Prompt 1: Rozszerzenia interoperacyjności i standardów OCI  
**"Zaproponuj, jak można zintegrować w WhyML pełne wsparcie dla standardów OCI Artifact Spec i Image Spec, aby manifesty mogły być używane natywnie w rejestrach OCI i runtime kontenerowych"**

***

### Prompt 2: Wsparcie dla Kubernetes i Helm/Kustomize  
**"Jak dodać do WhyML generator manifestów Kubernetes kompatybilny z Helm Charts i Kustomize overlays, uwzględniając modularność i zarządzanie zależnościami"**

***

### Prompt 3: Polityki bezpieczeństwa i podpisy cyfrowe manifestów  
**"Zmodyfikuj WhyML tak, aby umożliwić podpisywanie generowanych manifestów zgodnie z Sigstore oraz integrację z politykami walidacji OPA Gatekeeper"**

***

### Prompt 4: Rozszerzenie systemu szablonów i dziedziczenia  
**"Jak wzbogacić system template inheritance w WhyML o dynamiczne generowanie warunkowe, parametryzację i możliwość wielowarstwowego łączenia manifestów"**

***

### Prompt 5: Rozszerzona integracja CI/CD i API  
**"Zaprojektuj rozszerzenia API i CLI WhyML do automatycznej integracji z pipeline'ami CI/CD (GitLab, Jenkins) oraz implementację webhooków do Live Reload i GitOps"**

***

### Prompt 6: Wsparcie dla manifestów multi-artefaktowych i metadanych  
**"Dodaj wsparcie wieloartefaktowych manifestów z metadanymi (wersja, zależności, schematy danych) i ich automatyczną walidacją na podstawie schematów JSON Schema lub OpenAPI"**

***

### Prompt 7: Integracja z narzędziami low-code/no-code i generowania UI  
**"Jak WhyML może stać się platformą backendową do generowania komponentów UX/Frontend z deklaratywnych manifestów, integrując się z narzędziami low-code/no-code"**

***

Każdy z tych promptów można użyć do kolejnych rozmów, by precyzyjnie zaplanować rozwój WhyML i uczynić go pełnoprawnym konkurentem na rynku narzędzi manifestów i zarządzania artefaktami w enterprise.

Przykłady praktycznej integracji manifest-driven + WhyML + OCI  
Każdy etap wykorzystuje **standardy OCI**, **declarative manifests**, **Helm/Kustomize** i tam, gdzie przyspiesza prace frontendowe, **WhyML**.

## 1. Przechowywanie artefaktów (obrazy+dokumentacja) w rejestrze OCI  

```shell
# Budowanie obrazu kontenera
docker build -t myapp:1.0.0 .

# Tagowanie i push do rejestru OCI
docker tag myapp:1.0.0 harbor.company.com/myproject/myapp:1.0.0
docker push harbor.company.com/myproject/myapp:1.0.0

# Pakowanie dokumentacji jako artefaktu OCI
oras push harbor.company.com/myproject/myapp-docs:1.0.0 \
  ./docs/user-guide.html:application/vnd.company.docs.html \
  ./docs/sbom.json:application/vnd.cyclonedx+json

# Weryfikacja listingu artefaktów
oras manifest get harbor.company.com/myproject/myapp-docs:1.0.0
```

## 2. Definicja Helm Chart z Kustomize Overlay  

```yaml
# charts/myapp/Chart.yaml
apiVersion: v2
name: myapp
version: 1.0.0
appVersion: "1.0.0"
```

```yaml
# charts/myapp/values.yaml
replicaCount: 2
image:
  repository: harbor.company.com/myproject/myapp
  tag: "1.0.0"
service:
  type: ClusterIP
  port: 80
```

```yaml
# overlays/prod/kustomization.yaml
resources:
  - ../../charts/myapp
patchesStrategicMerge:
  - deployment-replicas.yaml
images:
  - name: harbor.company.com/myproject/myapp
    newTag: "1.0.0"
```

```yaml
# overlays/prod/deployment-replicas.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 5
```

```shell
# Deploy via Kustomize+Helm in GitOps pipeline
kustomize build overlays/prod | helm upgrade --install myapp -f - charts/myapp
```

## 3. Generowanie komponentu frontendowego z WhyML  

```yaml
# manifests/ui/landing-page.yaml
metadata:
  title: "Landing Page"
  version: "1.0.0"
template_vars:
  primary_color: "#ff6600"
  hero_text: "Witamy w Aplikacji"
  cta_text: "Rozpocznij"
styles:
  hero:
    background: "linear-gradient(90deg, {{ primary_color }}, #cc5200)"
    text-align: "center"
structure:
  section:
    class: "hero"
    children:
      - h1:
          text: "{{ hero_text }}"
      - button:
          class: "btn-primary"
          text: "{{ cta_text }}"
          onClick: "handleCTA"
```

```bash
# Konwersja manifestu do komponentu React
whyml convert manifests/ui/landing-page.yaml --format react \
  --output ui/src/components/LandingPage.tsx
```

## 4. Podpis i weryfikacja manifestów OCI (Sigstore)  

```shell
# Instalacja narzędzi
brew install sigstore-cli

# Generowanie klucza tymczasowego
cosign generate-key-pair

# Podpis manifestu OCI
cosign sign --key cosign.key \
  harbor.company.com/myproject/myapp:1.0.0

# Weryfikacja podpisu
cosign verify --key cosign.pub \
  harbor.company.com/myproject/myapp:1.0.0
```

## 5. Przykładowy fragment GitLab CI/CD  

```yaml
stages:
  - build
  - publish
  - deploy

variables:
  IMAGE: harbor.company.com/myproject/myapp

build:
  stage: build
  script:
    - docker build -t $IMAGE:$CI_COMMIT_TAG .
    - docker push $IMAGE:$CI_COMMIT_TAG

publish-docs:
  stage: publish
  script:
    - oras push $IMAGE-docs:$CI_COMMIT_TAG ./docs/user-guide.html:application/vnd.company.docs.html

sign:
  stage: publish
  script:
    - cosign sign --key cosign.key $IMAGE:$CI_COMMIT_TAG

deploy:
  stage: deploy
  script:
    - kustomize build overlays/$CI_ENVIRONMENT_NAME | helm upgrade --install myapp -f - charts/myapp
  only:
    - tags
```



