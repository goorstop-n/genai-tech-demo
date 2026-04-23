import {Type, type Static, type Tool} from "@mariozechner/pi-ai"


const WeatherParamsSchema = Type.Object({
    location: Type.String({description: "The location to get the weather for, e.g. '北京'."})
});

type WeatherParams = Static<typeof WeatherParamsSchema>;

export const weather: Tool = {
    name: "get_weather",
    description: "Get the current weather for a given location",
    parameters: WeatherParamsSchema
}

export async function getWeather(params: WeatherParams): Promise<string> {
    const { location } = params;
    return `${location}天气晴朗, 现在温度25°。`;
}
