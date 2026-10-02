\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{vva20book}[2026/10/02 vva20 native PDF book]
\DeclareOption{output=pdf}{}
\DeclareOption{output=epub}{\ClassError{vva20book}{WODTEX_E_OUTPUT_UNSUPPORTED: EPUB}{This profile supports native PDF only.}}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
\LoadClass[10pt,twoside,openright]{book}
\def\wodtexProfileId{vva20}
\RequirePackage{tex/wodtex-profile-core}
\RequirePackage{tex/wodtex-vva20}
\expandafter\wodtexSetClassStyle\expandafter{\wodtexProfileId}
\RequirePackage{tex/wodtex-api}
\endinput
