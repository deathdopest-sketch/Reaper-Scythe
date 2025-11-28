# REAPER Language Syntax Highlighting

Syntax highlighting support for the REAPER programming language.

## VS Code

### Installation

1. Copy the `syntaxes/` and `.vscode/` directories to your VS Code extensions folder, or
2. Install as a VS Code extension (if packaged)

### Manual Setup

1. Open VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Preferences: Open User Settings (JSON)"
4. Add the following:

```json
{
  "files.associations": {
    "*.reaper": "reaper"
  }
}
```

Or create a `.vscode/settings.json` in your project:

```json
{
  "files.associations": {
    "*.reaper": "reaper"
  }
}
```

## Sublime Text

1. Copy `syntaxes/reaper.tmLanguage.json` to:
   - **Windows**: `%APPDATA%\Sublime Text\Packages\User\`
   - **macOS**: `~/Library/Application Support/Sublime Text/Packages/User/`
   - **Linux**: `~/.config/sublime-text/Packages/User/`

2. Rename to `reaper.tmLanguage.json`

3. Restart Sublime Text

## Atom

1. Install the `language-tml` package
2. Copy `syntaxes/reaper.tmLanguage.json` to your Atom packages directory
3. Restart Atom

## Vim/Neovim

For Vim/Neovim, you can use a plugin like `vim-polyglot` or create a custom syntax file.

## Features

- ✅ Keyword highlighting (control flow, types, built-ins)
- ✅ String highlighting with escape sequences
- ✅ Number highlighting (integers, floats, hex, binary)
- ✅ Comment highlighting
- ✅ Operator highlighting
- ✅ Bracket matching
- ✅ Auto-closing pairs

## Color Scheme

The syntax highlighting uses standard TextMate scopes:
- Keywords: `keyword.*`
- Types: `storage.type.*`
- Functions: `support.function.*`
- Strings: `string.quoted.*`
- Numbers: `constant.numeric.*`
- Comments: `comment.*`

Most modern color themes will automatically style these scopes.

---

**The dead code in style.** ☠️

