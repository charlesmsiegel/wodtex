\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{v20clanbook}[2026/10/02 v20-clanbook native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{v20clanbook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{v20-clanbook}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-v20-clanbook}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
