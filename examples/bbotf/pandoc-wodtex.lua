-- Demonstration Pandoc filter for mechanical reference tables and statblocks.
-- WodTeX is native LaTeX; without this filter, Pandoc would emit longtable,
-- which is not the native wide-table interface of the corrected M20 renderer.
-- This filter intentionally handles only simple Markdown pipe tables.

local table_index = 0
local input = (PANDOC_STATE.input_files and PANDOC_STATE.input_files[1]) or 'reference.md'
local basename = input:gsub('\\', '/'):match('([^/]+)$') or 'reference.md'
local prefix = (basename:gsub('%.md$', ''):gsub('[^%w_-]', '-'))
local header_index = 0

function Header(h)
  -- Pandoc otherwise emits duplicate labels such as \label{validation}
  -- when several independent Markdown documents are combined into one book.
  header_index = header_index + 1
  local original = h.identifier ~= '' and h.identifier or ('heading-' .. header_index)
  h.identifier = prefix .. '-' .. original
  return h
end

local function latex(blocks)
  return (pandoc.write(pandoc.Pandoc(blocks), 'latex', {wrap_text = 'none'})
    :gsub('^%s+', ''):gsub('%s+$', ''):gsub('\n+', ' '))
end

local function table_row(row, n)
  if #row.cells ~= n then
    error('BBotF table has ' .. #row.cells .. ' cells; expected ' .. n)
  end
  local cells = {}
  for _, cell in ipairs(row.cells) do
    if cell.row_span > 1 or cell.col_span > 1 then
      error('Merged table cells are not supported in the BBotF example')
    end
    cells[#cells + 1] = latex(cell.contents)
  end
  return table.concat(cells, ' & ') .. ' \\\\'
end

function Table(tbl)
  table_index = table_index + 1
  local n = #tbl.colspecs
  local id = 'bbotf-' .. prefix .. '-table-' .. table_index
  local lines = {
    '\\begin{booktable}[id=' .. id .. ',head-rows=' .. #tbl.head.rows .. ',width=container]{' .. string.rep('l', n) .. '}'
  }
  for _, row in ipairs(tbl.head.rows) do lines[#lines + 1] = table_row(row, n) end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.head) do lines[#lines + 1] = table_row(row, n) end
    for _, row in ipairs(body.body) do lines[#lines + 1] = table_row(row, n) end
  end
  for _, row in ipairs(tbl.foot.rows) do lines[#lines + 1] = table_row(row, n) end
  lines[#lines + 1] = '\\end{booktable}'
  return pandoc.RawBlock('latex', table.concat(lines, '\n'))
end

local function has_class(classes, searched)
  for _, name in ipairs(classes) do if name == searched then return true end end
  return false
end

-- Optional Markdown syntax:
-- ::: statblock
-- **Rank:** 3
-- **Spheres:** Spirit 3
-- :::
function Div(div)
  if not has_class(div.classes, 'statblock') then return nil end
  local parts = {'\\begin{statblock}'}
  for _, block in ipairs(div.content) do
    if block.t ~= 'Para' and block.t ~= 'Plain' then
      error('BBotF statblock example only accepts paragraph entries')
    end
    parts[#parts + 1] = '\\statentry{' .. latex({block}) .. '}'
  end
  parts[#parts + 1] = '\\end{statblock}'
  return pandoc.RawBlock('latex', table.concat(parts, '\n'))
end