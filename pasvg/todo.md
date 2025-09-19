przenieś pliki:
scripts/pasvg_extractor.py
scripts/pasvg_generator.py
scripts/pasvg_build_system.py
do folderu ./pasvg i zrób z pasvg paczkę python z project.toml, makefile i opublikuj skrytpem, przetestuj z przykladowym plikiem projektu w svg
zrob refaktoryzacje aby pliki kodu nie miały wiekszej linii niż 500 linii, dodaj validator, extractor, importer, aby mozna bylo latwo rozbudowywac pliki projektow svg

dodaj opcję 
pasvg build - do zbudowania plikow
pasvg dev - do dynamicznego uruchomienia plikow z --watch w przegladarce 
pasvg edit - do edycji w przegladarce z parametrami opcjonalnymi odnosnie portu i hosta
pasvg edit -  powinien pozwalac na edycje z kolorwaniem składni elementow zawartych w projekcie svg 
i zawartosci z pomijaniem plikow data uri i rozpoznawaniem formatow typu html, xml, json, yaml, zapisywaniez przegaldarki bezposrednio na pliku z zapisywaniem historii w  folderze .pasvg

projekty przechowywane w pliku svg powinny być możliwe do exportowania do folderu
i z niego powino być mozliwe np generowanie artefaktow potrzebnych w  trakcie budowania np apk, pwa, itd
zapropnuj Jak połaczyć możliwość generowania artefaktów z whyml z projektem pasvg?