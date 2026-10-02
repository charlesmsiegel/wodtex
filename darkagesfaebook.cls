\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{darkagesfaebook}[2026/10/02 dark-ages-fae native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{darkagesfaebook}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{dark-ages-fae}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-dark-ages-fae}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
