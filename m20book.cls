\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesClass{m20book}[2026/09/30 M20 semantic book and output adapters]
\RequirePackage{expl3,xparse}
\newif\ifmTwentyEpub
\DeclareOption{output=pdf}{\mTwentyEpubfalse}
\DeclareOption{output=epub}{\mTwentyEpubtrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions\relax
% tex4ebook 0.4d's generic class/after hook runs for both book and this class,
% wrapping its own title wrapper recursively. Capture metadata once here.
\ifmTwentyEpub
  \RemoveFromHook{class/after}[tex4ebook]
\fi
\LoadClass[10pt,letterpaper,twoside,openright]{book}
\ifmTwentyEpub
  \let\mTwentyOriginalTitle\title
  \let\mTwentyOriginalAuthor\author
  \renewcommand\title[1]{\mTwentyOriginalTitle{#1}\gdef\Title{#1}}
  \renewcommand\author[1]{\mTwentyOriginalAuthor{#1}\gdef\Author{#1}}
\fi
\RequirePackage{tex/m20-core}
\RequirePackage{tex/m20-fonts}
\RequirePackage{tex/m20-art}
\ifmTwentyEpub
  \RequirePackage{fontspec}
  \AtBeginDocument{\mTwentyLoadFonts}
\else
  \RequirePackage{tex/m20-pdf-layout}
  \RequirePackage{tex/m20-pdf-sidebars}
  \RequirePackage{tex/m20-pdf-tables}
\fi
\RequirePackage{tex/m20-references}
\endinput
