\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{w20book}[2026/10/02 w20 native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{w20book}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{w20}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-w20}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
