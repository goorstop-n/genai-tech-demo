import { getModel, stream, complete, validateToolCall, streamSimple } from "@mariozechner/pi-ai";
import type { Tool, Context, AssistantMessage, ToolCall } from "@mariozechner/pi-ai";

import { weather, getWeather } from "./weather_tool";


const model = getModel("openrouter","deepseek/deepseek-v3.2");
console.log("Model loaded:", JSON.stringify(model));
console.log("\n================================\n");

const controller = new AbortController();
// Uncomment the following line to test aborting the stream after 500 miliseconds.
// setTimeout(() => controller.abort(), 100);

const tools: Tool[] = [
    weather
]

async function tool_calls(toolCalls: ToolCall[]) {
    for (const call of toolCalls) {
        let result: string;
        let isError: boolean = false;

        try {
            // When using agentLoop, tool arguments are automatically validated against your TypeBox schemas
            // before execution. If validation fails, the error is returned to the model as a tool result,
            // allowing it to retry.
            // When implementing your own tool execution loop with stream() or complete(), use validateToolCall
            // to validate arguments before passing them to your tools.
            const validatedArgs = validateToolCall(tools, call);
            if (call.name === 'get_weather') {
                result = await getWeather(validatedArgs);
            } else {
                result = `no implementation for tool ${call.name}`;
            }
        } catch (error) {
            result = `error occurred while validating tool call: ${call.name},
                        error: ${(error as Error).message}`;
            isError = true;
        }

        context.messages.push({
            toolCallId: call.id,
            toolName: call.name,
            role: 'toolResult',
            content: [{ type: 'text', text: result }],
            timestamp: Date.now(),
            isError: isError
        });
    }
}

const context: Context = {
    systemPrompt: "You are a helpful assistant.",
    messages: [
        {
            role: "user",
            content: "北京天气怎么样?",
            timestamp: Date.now(),
        }
    ],
    tools,
}

console.log("Starting the assistant...\n");

const s = stream(model, context, {
    onPayload: (payload) => {
        console.log("\n📦 [payload received]:", JSON.stringify(payload));
    },
    signal: controller.signal
});

for await (const event of s) {
    switch (event.type) {
        case 'start':
            console.log(`\n[start] with ${event.partial.model}`);
            break;
        case 'text_start':
            console.log('\n💡 [text_start]');
            break;
        case 'text_delta':
            process.stdout.write(event.delta);
            break;
        case 'text_end':
            console.log('\n💡 [text_end]');
            break;
        case 'thinking_start':
            console.log('\n💭 [thinking_start]');
            break;
        case 'thinking_delta':
            process.stdout.write(event.delta);
            break;
        case 'thinking_end':
            console.log('💭 [thinking_end]');
            break;
        case 'toolcall_start':
            console.log(`\n⚙️ [toolcall_start]: index ${event.contentIndex}`);
            break;
        case 'toolcall_delta':
            // partial tool arguments are being streamed.
            const partialCall = event.partial.content[event.contentIndex];
            if (partialCall !== undefined && partialCall.type === 'toolCall') {
                console.log(`[streaming args for ${partialCall.name}]`);
            }
            break;
        case 'toolcall_end':
            console.log(`\n⚙️ [toolcall_end]: ${event.toolCall.name}`);
            console.log(`arguments: ${JSON.stringify(event.toolCall.arguments)}`);
            break;
        case 'done':
            console.log(`\n✅ [done]: ${event.reason}`);
            break;
        case 'error':
            console.error(`[error]: ${event.error}`);
            break;
    }
}

// stream结束或者等待调用工具；
const response = await s.result();
context.messages.push(response);

// 调用工具；
const toolCalls = response.content.filter(c => c.type === 'toolCall');
await tool_calls(toolCalls);

let finalAnswer : AssistantMessage = response;

if (toolCalls.length > 0) {
    const continuation = await complete(model, context, {
        onPayload: (payload) => {
            console.log("\n📦 [payload received during continuation]:", JSON.stringify(payload));
        }
    });
    context.messages.push(continuation);
    finalAnswer = continuation;
}

if (finalAnswer.stopReason === 'error' || finalAnswer.stopReason === 'aborted') {
    console.error('\n❌ final answer ended with reason:', finalAnswer.errorMessage);
} else {
    console.log('\n✅ final answer:\n', finalAnswer.content);
}

console.log(`total tokens: ${response.usage.input} in, ${response.usage.output} out`);
console.log(`cost: $${response.usage.cost.total.toFixed(4)}\n`);