import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';

// REAPER language keywords and built-ins
const KEYWORDS = [
    'corpse', 'soul', 'crypt', 'grimoire', 'tomb', 'wraith', 'phantom', 
    'specter', 'shadow', 'void', 'eternal', 'infect', 'raise', 'harvest',
    'reap', 'shamble', 'decay', 'soulless', 'spawn', 'if', 'otherwise',
    'judge', 'case', 'default', 'flee', 'persist', 'rest', 'this', 'from',
    'to', 'in', 'for', 'infiltrate', 'risk', 'catch', 'finally', 'throw',
    'breach', 'await', 'corrupt', 'infest', 'banish'
];

const BUILTIN_FUNCTIONS = [
    'harvest', 'rest', 'raise_corpse', 'steal_soul', 'summon', 'final_rest',
    'curse', 'absolute', 'lesser', 'greater', 'raise_phantom', 'excavate',
    'bury', 'excavate_bytes', 'bury_bytes', 'inspect', 'list_graves',
    'create_grave', 'remove_grave', 'join_paths', 'split_path', 'normalize_path',
    'encode_soul', 'decode_soul', 'ritual_args'
];

const BUILTIN_CONSTANTS = ['DEAD', 'RISEN', 'void'];

export function activate(context: vscode.ExtensionContext) {
    console.log('REAPER Language extension is now active!');

    // Register completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        'reaper',
        {
            provideCompletionItems(
                document: vscode.TextDocument,
                position: vscode.Position,
                token: vscode.CancellationToken,
                context: vscode.CompletionContext
            ): vscode.ProviderResult<vscode.CompletionItem[] | vscode.CompletionList> {
                const items: vscode.CompletionItem[] = [];

                // Add keywords
                for (const keyword of KEYWORDS) {
                    const item = new vscode.CompletionItem(keyword, vscode.CompletionItemKind.Keyword);
                    item.documentation = `REAPER keyword: ${keyword}`;
                    items.push(item);
                }

                // Add built-in functions
                for (const func of BUILTIN_FUNCTIONS) {
                    const item = new vscode.CompletionItem(func, vscode.CompletionItemKind.Function);
                    item.documentation = `Built-in function: ${func}()`;
                    item.insertText = new vscode.SnippetString(`${func}($0)`);
                    items.push(item);
                }

                // Add built-in constants
                for (const constant of BUILTIN_CONSTANTS) {
                    const item = new vscode.CompletionItem(constant, vscode.CompletionItemKind.Constant);
                    item.documentation = `Built-in constant: ${constant}`;
                    items.push(item);
                }

                return items;
            }
        }
    );

    // Register hover provider
    const hoverProvider = vscode.languages.registerHoverProvider('reaper', {
        provideHover(document: vscode.TextDocument, position: vscode.Position) {
            const wordRange = document.getWordRangeAtPosition(position);
            if (!wordRange) {
                return null;
            }

            const word = document.getText(wordRange);

            // Provide hover info for built-ins
            if (BUILTIN_FUNCTIONS.includes(word)) {
                return new vscode.Hover({
                    language: 'reaper',
                    value: `**Built-in Function**: \`${word}()\`\n\nREAPER built-in function.`
                });
            }

            if (BUILTIN_CONSTANTS.includes(word)) {
                let value = '';
                if (word === 'DEAD') value = '0 (false)';
                else if (word === 'RISEN') value = '1 (true)';
                else if (word === 'void') value = 'null/None';

                return new vscode.Hover({
                    language: 'reaper',
                    value: `**Built-in Constant**: \`${word}\`\n\nValue: ${value}`
                });
            }

            if (KEYWORDS.includes(word)) {
                return new vscode.Hover({
                    language: 'reaper',
                    value: `**REAPER Keyword**: \`${word}\``
                });
            }

            return null;
        }
    });

    // Register command: Run REAPER file
    const runFileCommand = vscode.commands.registerCommand('reaper.runFile', (uri?: vscode.Uri) => {
        const fileUri = uri || vscode.window.activeTextEditor?.document.uri;
        if (!fileUri || !fileUri.fsPath.endsWith('.reaper')) {
            vscode.window.showErrorMessage('Please open a .reaper file to run');
            return;
        }

        const terminal = vscode.window.createTerminal('REAPER');
        const config = vscode.workspace.getConfiguration('reaper');
        const executable = config.get<string>('executablePath', 'python reaper_main.py');
        terminal.sendText(`${executable} "${fileUri.fsPath}"`);
        terminal.show();
    });

    // Register command: Compile to bytecode
    const compileCommand = vscode.commands.registerCommand('reaper.compileBytecode', (uri?: vscode.Uri) => {
        const fileUri = uri || vscode.window.activeTextEditor?.document.uri;
        if (!fileUri || !fileUri.fsPath.endsWith('.reaper')) {
            vscode.window.showErrorMessage('Please open a .reaper file to compile');
            return;
        }

        const config = vscode.workspace.getConfiguration('reaper');
        const executable = config.get<string>('executablePath', 'python reaper_main.py');
        const terminal = vscode.window.createTerminal('REAPER');
        terminal.sendText(`${executable} --compile-bc "${fileUri.fsPath}"`);
        terminal.show();
        vscode.window.showInformationMessage(`Compiling ${path.basename(fileUri.fsPath)} to bytecode...`);
    });

    // Register diagnostic provider (basic syntax checking)
    const diagnosticCollection = vscode.languages.createDiagnosticCollection('reaper');
    const diagnosticProvider = vscode.workspace.onDidChangeTextDocument((e) => {
        if (e.document.languageId === 'reaper') {
            checkSyntax(e.document, diagnosticCollection);
        }
    });

    // Check syntax on open
    vscode.workspace.textDocuments.forEach(doc => {
        if (doc.languageId === 'reaper') {
            checkSyntax(doc, diagnosticCollection);
        }
    });

    context.subscriptions.push(
        completionProvider,
        hoverProvider,
        runFileCommand,
        compileCommand,
        diagnosticProvider,
        diagnosticCollection
    );
}

function checkSyntax(
    document: vscode.TextDocument,
    collection: vscode.DiagnosticCollection
): void {
    const diagnostics: vscode.Diagnostic[] = [];
    const text = document.getText();

    // Basic syntax checks
    const lines = text.split('\n');
    lines.forEach((line, index) => {
        const lineNum = index + 1;

        // Check for unclosed strings
        let inString = false;
        let stringChar = '';
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"' || char === "'") {
                if (!inString) {
                    inString = true;
                    stringChar = char;
                } else if (char === stringChar && (i === 0 || line[i - 1] !== '\\')) {
                    inString = false;
                    stringChar = '';
                }
            }
        }

        if (inString) {
            diagnostics.push({
                range: new vscode.Range(
                    new vscode.Position(index, line.length - 1),
                    new vscode.Position(index, line.length)
                ),
                message: 'Unclosed string literal',
                severity: vscode.DiagnosticSeverity.Error,
                source: 'reaper'
            });
        }

        // Check for common syntax errors
        if (line.trim().endsWith('infect') || line.trim().endsWith('if') || 
            line.trim().endsWith('shamble') || line.trim().endsWith('decay')) {
            // These should typically be followed by something
            if (index === lines.length - 1 || lines[index + 1].trim() === '') {
                diagnostics.push({
                    range: new vscode.Range(
                        new vscode.Position(index, line.length - 1),
                        new vscode.Position(index, line.length)
                    ),
                    message: 'Statement appears incomplete',
                    severity: vscode.DiagnosticSeverity.Warning,
                    source: 'reaper'
                });
            }
        }
    });

    collection.set(document.uri, diagnostics);
}

export function deactivate() {}

