from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from weather_agent_executor import WeatherAgentExecutor


def main(host: str, port: int):
    capabilities = AgentCapabilities(streaming=False)
    weather_skill = AgentSkill(
        id='天气预报',
        name='天气预报',
        description='给出某地的天气预报',
        tags=['天气', '预报'],
        examples=['北京的天气怎么样？'],
    )
    agent_card = AgentCard(
        name='Weather Agent',
        description='提供某地的天气预报',
        url=f'http://{host}:{port}',
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=capabilities,
        skills=[weather_skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=WeatherAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    import uvicorn
    uvicorn.run(server.build(), host=host, port=port)


if __name__ == '__main__':
    main("127.0.0.1", 10000)