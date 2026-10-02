\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{wodbook}[2026/10/02 wod native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{wodbook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{wod}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-wod}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
