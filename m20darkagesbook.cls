\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{m20darkagesbook}[2026/10/02 m20-dark-ages native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{m20darkagesbook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{m20-dark-ages}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-m20-dark-ages}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
