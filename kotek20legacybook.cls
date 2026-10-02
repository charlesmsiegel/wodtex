\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{kotek20legacybook}[2026/10/02 kotek20-legacybook native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{kotek20legacybook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{kotek20-legacybook}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-kotek20-legacybook}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
