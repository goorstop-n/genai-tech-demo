import { CombinedAutocompleteProvider, Editor, Key, Loader, Markdown, matchesKey, ProcessTerminal, Text, TUI } from "@mariozechner/pi-tui";
import { defaultEditorTheme, defaultMarkdownTheme } from "./tui_themes";
import chalk from "chalk";
import { Agent } from "@mariozechner/pi-agent-core";
import { getModel } from "@mariozechner/pi-ai";
import { weather } from "../pi-agent-core/weather_tool";

const agent = new Agent({
    initialState: {
        systemPrompt: "You are a helpful assistant.",
        model: getModel("openrouter","deepseek/deepseek-v3.2"),
        messages: [],
        tools: [ weather ]
    },
});

// Create terminal
const terminal = new ProcessTerminal();

// Create TUI
const tui = new TUI(terminal);

// Create chat container with some initial messages
tui.addChild(
	new Text("Welcome to Simple Chat!\n\nType your messages below. Type '/' for commands. Press Ctrl+C to exit."),
);

// Create editor with autocomplete
const editor = new Editor(tui, defaultEditorTheme);
editor.setPaddingX(1);

// Set up autocomplete provider with slash commands and file completion
const autocompleteProvider = new CombinedAutocompleteProvider(
	[
        { name: "quit", description: "Quit the chat." },
	],
	process.cwd(),
);
editor.setAutocompleteProvider(autocompleteProvider);

tui.addChild(editor);

// Focus the editor
tui.setFocus(editor);

// Track if we're waiting for bot response
let isResponding = false;
let firstTurn = true;
let assistantResponse = "";

const loader = new Loader(
    tui,
    (s) => chalk.cyan(s),
    (s) => chalk.dim(s),
    "💭 Thinking...",
);
const toolLoader = new Loader(
    tui,
    (s) => chalk.cyan(s),
    (s) => chalk.dim(s),
    "⚙️ Tool Calling...",
);

// Handle message submission
editor.onSubmit = (value: string) => {
	// Prevent submission if already responding
	if (isResponding) {
		return;
	}

	const trimmed = value.trim();
    if (trimmed === "/quit") {
        gracefullyExit();
        return;
    }

    // If not a command and not empty, submit as user message
	if (trimmed) {
		isResponding = true;
		editor.disableSubmit = true;

        agent.prompt(value);

		const userMessage = new Markdown(value, 1, 1, defaultMarkdownTheme);
		const children = tui.children;
		children.splice(children.length - 1, 0, userMessage);
		children.splice(children.length - 1, 0, loader);
		tui.requestRender();
	}
};

const unsubscribe = agent.subscribe((event) => {
    switch (event.type) {
        case 'message_update':
            if (event.assistantMessageEvent.type === 'text_delta') {
                assistantResponse += event.assistantMessageEvent.delta;

                const botMessage = new Markdown(assistantResponse, 1, 1, defaultMarkdownTheme);
                const children = tui.children;
                if (firstTurn) {
                    firstTurn = false;
                    children.splice(children.length - 1, 0, botMessage);
                } else {
                    children.splice(children.length - 2, 1, botMessage);
                }
                // Request render
                tui.requestRender();
            }
            break;
        case 'turn_end':
            firstTurn = true;
            assistantResponse = "";
            break;
        case 'tool_execution_start':
            const children = tui.children;
            children.splice(children.length - 1, 0, toolLoader);
		    tui.requestRender();
            break;
        case 'agent_end':
            // Re-enable submit
            isResponding = false;
            editor.disableSubmit = false;
            tui.requestRender();
            break;
        }
});

tui.addInputListener((input) => {
    if (matchesKey(input, Key.ctrl("c"))) {
        gracefullyExit();
    }
});

// Start the TUI
tui.start();

async function gracefullyExit() {
    try {
        unsubscribe();
        await terminal.drainInput();
        tui.stop();
        terminal.stop();
    } finally {
        process.exit(0);
    }
}