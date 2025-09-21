# WhyML Refaktoryzacja - Plan Architektury Modularnej

## 🎯 Cel Refaktoryzacji
Podzielenie monolitycznego pakietu WhyML na mniejsze, reużywalne komponenty i stworzenie ekosystemu komplementarnych pakietów.

## 📦 Nowa Architektura Pakietów

### 1. **whyml-core** (Podstawowy pakiet)
```
whyml_core/
├── __init__.py
├── exceptions/
│   ├── __init__.py
│   ├── base_exceptions.py
│   ├── validation_exceptions.py
│   └── processing_exceptions.py
├── validation/
│   ├── __init__.py
│   ├── manifest_validator.py
│   ├── schema_loader.py
│   └── field_validators.py
├── loading/
│   ├── __init__.py
│   ├── manifest_loader.py
│   ├── cache_manager.py
│   └── dependency_resolver.py
├── processing/
│   ├── __init__.py
│   ├── template_processor.py
│   ├── inheritance_resolver.py
│   └── variable_substitution.py
└── utils/
    ├── __init__.py
    ├── yaml_utils.py
    └── async_utils.py
```

### 2. **whyml-scrapers** (Web scraping funkcjonalność)
```
whyml_scrapers/
├── __init__.py
├── analysis/
│   ├── __init__.py
│   ├── page_analyzer.py
│   ├── content_analyzer.py
│   └── seo_analyzer.py
├── extraction/
│   ├── __init__.py
│   ├── html_extractor.py
│   ├── css_extractor.py
│   └── metadata_extractor.py
├── parsing/
│   ├── __init__.py
│   ├── dom_parser.py
│   ├── structure_parser.py
│   └── content_parser.py
└── scrapers/
    ├── __init__.py
    ├── url_scraper.py
    └── webpage_scraper.py
```

### 3. **whyml-converters** (Format conversion)
```
whyml_converters/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── base_converter.py
│   ├── conversion_result.py
│   └── template_engine.py
├── html/
│   ├── __init__.py
│   ├── html_converter.py
│   └── html_templates.py
├── react/
│   ├── __init__.py
│   ├── react_converter.py
│   └── jsx_generator.py
├── vue/
│   ├── __init__.py
│   ├── vue_converter.py
│   └── sfc_generator.py
├── php/
│   ├── __init__.py
│   ├── php_converter.py
│   └── php_templates.py
└── shared/
    ├── __init__.py
    ├── component_builder.py
    ├── style_processor.py
    └── asset_manager.py
```

### 4. **whyml-cli** (Command Line Interface)
```
whyml_cli/
├── __init__.py
├── commands/
│   ├── __init__.py
│   ├── scrape_command.py
│   ├── convert_command.py
│   ├── serve_command.py
│   └── validate_command.py
├── ui/
│   ├── __init__.py
│   ├── progress_bars.py
│   ├── output_formatters.py
│   └── error_handlers.py
└── config/
    ├── __init__.py
    ├── cli_config.py
    └── argument_parser.py
```

### 5. **whyml-generators** (Dodatkowe generatory)
```
whyml_generators/
├── __init__.py
├── pwa/
│   ├── __init__.py
│   ├── pwa_generator.py
│   ├── manifest_generator.py
│   └── service_worker_generator.py
├── spa/
│   ├── __init__.py
│   ├── spa_generator.py
│   └── router_generator.py
├── mobile/
│   ├── __init__.py
│   ├── cordova_generator.py
│   └── capacitor_generator.py
└── docker/
    ├── __init__.py
    ├── dockerfile_generator.py
    └── compose_generator.py
```

## 🔄 Proces Refaktoryzacji

### Faza 1: Analiza i Podział Core
1. **manifest_processor.py** → `whyml_core/validation/`, `whyml_core/processing/`
2. **manifest_loader.py** → `whyml_core/loading/`
3. **exceptions.py** → `whyml_core/exceptions/`

### Faza 2: Refaktoryzacja Scrapers
1. **url_scraper.py** → `whyml_scrapers/scrapers/`, `whyml_scrapers/extraction/`
2. **webpage_analyzer.py** → `whyml_scrapers/analysis/`

### Faza 3: Modularyzacja Converters
1. **base_converter.py** → `whyml_converters/base/`
2. **html_converter.py** → `whyml_converters/html/`
3. **react_converter.py** → `whyml_converters/react/`
4. **vue_converter.py** → `whyml_converters/vue/`
5. **php_converter.py** → `whyml_converters/php/`

### Faza 4: CLI i Generator Separation
1. **cli.py** → `whyml_cli/`
2. **generators.py** → `whyml_generators/`

## 🎯 Korzyści Refaktoryzacji

1. **Modularność** - Każdy pakiet ma jasno określoną odpowiedzialność
2. **Reużywalność** - Komponenty można używać niezależnie
3. **Testowalność** - Łatwiejsze testowanie izolowanych komponentów
4. **Rozszerzalność** - Prosta możliwość dodawania nowych funkcji
5. **Utrzymywalność** - Mniejsze pliki, lepsze oddzielenie obowiązków
6. **Dystrybucja** - Użytkownicy mogą instalować tylko potrzebne komponenty

## 📚 Zależności Między Pakietami

```
whyml-cli
    ├── whyml-core
    ├── whyml-scrapers
    ├── whyml-converters
    └── whyml-generators

whyml-scrapers
    └── whyml-core

whyml-converters
    └── whyml-core

whyml-generators
    ├── whyml-core
    └── whyml-converters
```

## ✅ Kryteria Sukcesu

1. Wszystkie testy przechodzą po refaktoryzacji
2. Publiczne API pozostaje kompatybilne
3. Każdy pakiet ma jasno określoną odpowiedzialność
4. Brak duplikacji kodu między pakietami
5. Dokumentacja jest aktualna i kompletna
