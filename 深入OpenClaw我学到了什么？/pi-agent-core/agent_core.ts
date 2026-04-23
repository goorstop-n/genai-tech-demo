import { Agent, type AgentEvent } from "@mariozechner/pi-agent-core";
import { getModel } from "@mariozechner/pi-ai";
import { weather } from "./weather_tool";

const agent = new Agent({
    initialState: {
        systemPrompt: "You are a helpful assistant.",
        model: getModel("openrouter","deepseek/deepseek-v3.2"),
        messages: [],
        tools: [ weather ]
    },
});

const unsubscribe = agent.subscribe((event) => {
    switch (event.type) {
        case 'agent_start':
            console.log(`\n[agent_start]\nAgent is starting...`);
            break;
        case 'agent_end':
            console.log(`\n[agent_end]\nAgent has finished.\nMessages: ${JSON.stringify(event.messages)}`);
            break;
        case 'turn_start':
            console.log(`\n[turn_start]\nA new turn is starting...`);
            break;
        case 'turn_end':
            console.log(`\n[turn_end]\nTurn has ended.
                \nMessage: ${JSON.stringify(event.message)}
                \nToolResults: ${JSON.stringify(event.toolResults)}`);
            break;
        case 'message_start':
            console.log(`\n[message_start]\nA new message is starting...
                \nMessage: ${JSON.stringify(event.message)}`);
            break;
        case 'message_update':
            // console.log(`\n[message_update]\nMessage is updating...
            //     \nMessage: ${JSON.stringify(event.message)}
            //     \nEvent: ${JSON.stringify(event.assistantMessageEvent)}`);
            // if (event.assistantMessageEvent.type === 'text_delta') {
            //     process.stdout.write(event.assistantMessageEvent.delta)
            // }
            break;
        case 'message_end':
            console.log(`\n[message_end]\nMessage has ended...
                \nMessage: ${JSON.stringify(event.message)}`);
            break;
        case 'tool_execution_start':
            console.log(`\n[tool_execution_start]\nTool execution is starting...
                \nToolCallId: ${event.toolCallId}
                \nToolName: ${event.toolName}
                \nArguments: ${JSON.stringify(event.args)}`);
            break;
        case 'tool_execution_update':
            console.log(`\n[tool_execution_update]\nTool execution is updating...
                \nToolCallId: ${event.toolCallId}
                \nToolName: ${event.toolName}
                \nArguments: ${JSON.stringify(event.args)}
                \nPartialResult: ${JSON.stringify(event.partialResult)}`);
            break;
        case 'tool_execution_end':
            console.log(`\n[tool_execution_end]\nTool execution has ended...
                \nToolCallId: ${event.toolCallId}
                \nToolName: ${event.toolName}
                \nResult: ${JSON.stringify(event.result)}
                \nIsError: ${event.isError}`);
            break;
    }
});
try {
    const promptPromise = agent.prompt("北京天气怎么样？");

    setTimeout(() => {
        // agent.steer({role: "user", content: "先停止这个任务。", timestamp: Date.now()});
    }, 100);
    agent.followUp({role: "user", content: "以小孩的口吻输出结果。", timestamp: Date.now()});

    await promptPromise;
} finally {
    unsubscribe(); // Call this function to stop listening to agent events
}