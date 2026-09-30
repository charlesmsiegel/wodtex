-- Native TeX alignment rows are boxed once, then handed to the owner paginator.
-- Copying the unshipped alignment preserves each semantic write exactly once.
local M = {}
local hid, vid, wid = node.id('hlist'), node.id('vlist'), node.id('whatsit')
local write_subtype, dest_subtype = node.subtype('write'), node.subtype('pdf_dest')
local manual_subtype = node.subtype('user_defined')
local function visible(head)
  for n in node.traverse(head) do
    if n.id==node.id('glyph') or (n.id==node.id('rule') and n.width>0 and n.height+n.depth>0) then return true end
    if n.head and visible(n.head) then return true end
  end
  return false
end

local function alignment(head)
  for n in node.traverse(head) do
    if n.id == vid then return n end
    if n.head then
      local found = alignment(n.head)
      if found then return found end
    end
  end
end

local function strip_repeated_writes(head)
  local n=head
  while n do
    local following=n.next
    if n.head then n.head = strip_repeated_writes(n.head) end
    if n.id == wid and (n.subtype == write_subtype or n.subtype == dest_subtype) then
      head = node.remove(head,n,true)
    end
    n=following
  end
  return head
end

function M.extract(source, destination, header, count, maximum, offset)
  local box = tex.box[source]
  local rows = box and alignment(box.head)
  if not rows then tex.error('M20_E_TABLE_STRUCTURE',{'Native table alignment could not be found.'}); return end
  local output, tail, headings, htail
  local rownumber = 0
  for n in node.traverse(rows.head) do
    if n.id == hid then
      rownumber = rownumber + 1
      if n.height + n.depth > maximum then
        tex.error('M20_E_ROW_TOO_TALL',{'An atomic row, including nested cells, exceeds the usable page height. Split it or change its width.'})
        return
      end
    end
    local copy = node.copy(n)
    if n.head then copy.head = node.copy_list(n.head) end
    if copy.id == hid then copy.shift=offset end
    output,tail = node.insert_after(output,tail,copy)
    if count>0 and rownumber <= count then
      local h = node.copy(n)
      if n.head then h.head = strip_repeated_writes(node.copy_list(n.head)) end
      if h.id == hid then h.shift=offset end
      headings,htail = node.insert_after(headings,htail,h)
    end
    if n.id == hid then
      local penalty = node.new('penalty'); penalty.penalty = rownumber<=count and 10000 or 0
      output,tail = node.insert_after(output,tail,penalty)
    end
  end
  tex.box[destination] = node.vpack(output)
  tex.box[header] = headings and node.vpack(headings) or nil
end

function M.check_first(galley,available,placement,segment,maximum)
  local box=tex.box[galley]
  if not box then return end
  local height=0
  local ink=false
  local function check()
    if height>available then
      if placement=='here' and segment==0 then
        tex.error('M20_E_PLACEMENT_UNAVAILABLE',{'The first required atomic block does not fit at this anchor.'})
      elseif height>maximum then
        tex.error('M20_E_CONTENT_TOO_TALL',{'The atomic block exceeds a full usable region. Split it or change its width.'})
      else tex.sprint('\\mTwentyAdvance\\mTwentySetSplitHeight') end
    end
  end
  for n in node.traverse(box.head) do
    if ink and ((n.id==node.id('penalty') and n.penalty<10000) or
       (n.id==node.id('glue') and n.prev and (n.prev.id==hid or n.prev.id==vid))) then check();return end
    if n.id==node.id('glue') then height=height+n.width end
    if n.id==hid or n.id==vid or n.id==node.id('rule') then
      height=height+n.height+n.depth
      ink=ink or (n.id==node.id('rule') and n.width>0 and n.height+n.depth>0) or (n.head and visible(n.head))
    end
  end
  if ink then check() end
end

-- A native node marker keeps explicit breaks effective even in a short galley.
-- Cutting before pagination does not expand or typeset manuscript content again.
function M.manual_break(mode)
  local n=node.new('whatsit','user_defined')
  n.user_id=20260930; n.type=100; n.value=mode=='page' and 1 or 2
  node.write(n)
end

function M.cut_manual(source,pending)
  local box=tex.box[source]
  tex.box[pending]=nil
  if box then
    for n in node.traverse(box.head) do
      if n.id==wid and n.subtype==manual_subtype and n.user_id==20260930 then
        local before,after=box.head,n.next
        if n.prev then n.prev.next=nil else before=nil end
        if after then after.prev=nil end
        local mode=n.value==1 and 'page' or 'column'
        n.prev=nil; n.next=nil; node.flush_node(n)
        box.head=nil
        tex.box[source]=node.vpack(before)
        tex.box[pending]=after and node.vpack(after) or nil
        tex.sprint('\\def\\mTwentyManualMode{'..mode..'}')
        return
      end
    end
  end
  tex.sprint('\\def\\mTwentyManualMode{}')
end

return M
