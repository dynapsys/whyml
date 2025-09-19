
Oto zestaw kolejnych promptów, które mogą poprowadzić rozwój WhyML w kierunku pełnej konkurencyjności względem rozwiązań enterprise, OCI i manifestów w ekosystemie Kubernetes:

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



