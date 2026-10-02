\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{kote20dharmabook}[2026/10/02 kote20-dharmabook native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{kote20dharmabook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{kote20-dharmabook}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-kote20-dharmabook}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
