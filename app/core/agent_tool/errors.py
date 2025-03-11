from typing import Optional, Any, List
from uuid import UUID



class AgentToolError(Exception):
    agent_tool_id: UUID
    description: Optional[str] = None
    actions: Optional[List[Any]]

    def __init__(
        self, 
        agent_tool_id: UUID, 
        description: Optional[str] = None,
        actions: Optional[List[Any]] = None
    ):
        super().__init__()
        self.agent_tool_id = agent_tool_id
        if description is not None:
            self.description = description

        self.actions = actions