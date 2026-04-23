import type { AgentTool, AgentToolResult } from "@mariozechner/pi-agent-core";
import {Type, type Static, type Tool} from "@mariozechner/pi-ai"


const WeatherParamsSchema = Type.Object({
    location: Type.String({description: "The location to get the weather for, e.g. '北京'."})
});
type WeatherParams = Static<typeof WeatherParamsSchema>;

async function getWeather(
    toolCallId: string,
    params: WeatherParams,
    signal?: AbortSignal,
    onUpdate?: (result: AgentToolResult<string>) => void
) : Promise<AgentToolResult<string>> {
    let result = `${params.location}天气晴朗, 现在温度25°。`;
    return {
        content: [{type: 'text', text: result}],
        details: result
    }
}

export const weather: AgentTool<typeof WeatherParamsSchema, string> = {
    label: "get_weather",
    name: "get_weather",
    description: "Get the current weather for a given location",
    parameters: WeatherParamsSchema,
    execute: getWeather
}


