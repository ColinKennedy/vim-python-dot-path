" A module which traverses Python files and code to get a dot-separated path to the user's cursor.
"
" See Also:
"     :func:`GetCurrentDotPath`
"


" Get the Python module dot path to a given Python file.
"
" It's assumed that `reference` actually is within a Rez package.
"
" Args:
"     reference (str):
"         The absolute path to a file or folder on-disk. It must be
"         within a Rez package.
"
" Returns:
"     str:
"         The found module dot path, if any. e.g. "tests.test_foo".
"         This path does not contain Python class / function / method
"         information. Just the module names.
"
function! s:get_rez_dot_path(reference)
    let l:previous = ""
    let l:current = fnamemodify(a:reference, ":p:r")
    let l:names = []
    let l:package_path = ""

    while l:previous != l:current
        call add(l:names, fnamemodify(l:current, ":t"))

        let l:package_path = s:get_package_path(l:current)

        if filereadable(l:package_path)
            break
        endif

        let l:previous = l:current
        let l:current = fnamemodify(l:current, ":h")
    endwhile

    if l:package_path == ""
        echoerr "No package root could be found."

        return ""
    endif

    let l:names = reverse(l:names)
    let l:names = s:resolve_module_names(l:names, l:package_path)

    return join(l:names, ".")
endfunction


" Find the Rez package within `directory`, if it exists.
"
" Args:
"     directory (str): A folder, on-disk, where there may be a Rez package file.
"
" Returns:
"     str: The found package path, if any.
"
function! s:get_package_path(directory)
    for l:possibility in [
    \ a:directory . "/package.py",
    \ a:directory . "/package.yaml",
    \ a:directory . "/package.yml",
    \ ]
        if filereadable(l:possibility)
            return l:possibility
        endif
    endfor

    return ""
endfunction


" Get the Python module names which most closely resemble their import path.
"
" Args:
"     names (list[str]): Each found Python folder. They usually either assume
"     that the Python files are within a Rez package, within a folder called
"     "python" or assume that the Python files are defined, starting at the
"     root of the Python package. e.g. ["rez_utilities", "python", "rez_utilities", "blah.py"]
"     or ["rez_utilities", "rez_utilities", "blah.py"]
"
" Returns:
"     list[str]: The folders without the first 1 or 2 folder names.
"
function! s:resolve_module_names(names, package_path)
    if a:names[1] == "python"
        return a:names[2:]
    endif

    return a:names[1:]
endfunction


" Find the Python dot path to the user's current row / column position.
"
" Args:
"     buffer (container[str]):
"         Every Python source code line which will be parsed for a dot path.
"     row (int):
"         A 0-based index value for the user's cursor position.
"     column (int, optional):
"         A 0-based index value for the user's cursor offset.
"
" Returns:
"     str: The found dot path "Class.get_bar".
"
function! s:_get_inner_dot_path(buffer, row, column)
pythonx << EOF
import dot_finder
import vim

path = dot_finder.get_dot_path(
    int(vim.eval("a:row")),
    vim.eval("a:buffer"),
    int(vim.eval("a:column")),
)
vim.command('let l:result = "{path}"'.format(path=path))
EOF

return l:result
endfunction


" str: Get the user's current Python dot-import location. e.g. "tests.test_foo.Class.get_bar"
function! GetCurrentDotPath()
    let l:current_path = expand("%:p")
    let l:current_buffer = getline(1, '$')
    let l:cursor = getpos(".")
    let l:row = l:cursor[1]
    let l:column = l:cursor[2]

    let l:root = s:get_rez_dot_path(l:current_path)
    let l:tail = s:_get_inner_dot_path(l:current_buffer, l:row - 1, l:column)

    if l:tail == ""
        return l:root
    endif

    return l:root . "." . l:tail
endfunction


" How to send the dot path to the top terminal buffer
"
" `call SendTextToTopTerminal("python -m unittest " . GetCurrentDotPath())`
" `nnoremap <silent> <leader>x :call SendTextToTopTerminal("python -m unittest " . GetCurrentDotPath())<CR>`
"
function! ReportCurrentDotPath()
    let l:dot_path = GetCurrentDotPath()
    let l:full_expression = "python -m unittest " . l:dot_path
    let @+=l:full_expression

    return l:full_expression
endfunction


command! -buffer -nargs=0 ReportCurrentDotPath :echo ReportCurrentDotPath()

autocmd FileType python nnoremap <leader>pd :ReportCurrentDotPath<CR>
