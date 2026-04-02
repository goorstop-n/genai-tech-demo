import random

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (Part, Task, TextPart, UnsupportedOperationError)
from a2a.utils import (completed_task, new_artifact)
from a2a.utils.errors import ServerError


class WeatherAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        results = [
            "天气晴朗，气温为20摄氏度，天气温和适宜。建议外出晒晒太阳。",
            "目前多云，气温为15摄氏度，天气较为凉爽。建议外出时适当添加衣物。",
            "目前有小雨，气温为10摄氏度，天气较为阴冷。建议外出时携带雨具并适当添加衣物。"
        ]

        text = results[random.randint(0, len(results) - 1)]
        print(text)
        await event_queue.enqueue_event(
            completed_task(
                context.task_id,
                context.context_id,
                [new_artifact(parts=[Part(root=TextPart(text=text))], name="天气查询结果")],
                [context.message],
            )
        )

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())