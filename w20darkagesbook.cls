\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{w20darkagesbook}[2026/10/02 w20-dark-ages native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{w20darkagesbook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{w20-dark-ages}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-w20-dark-ages}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
