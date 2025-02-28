from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
from uuid import UUID



class RunStepStatus(Enum):
    in_progress = 'in_progress'
    cancelled = 'cancelled'
    failed = 'failed'
    completed = 'completed'
    expired = 'expired'

class RunStepType(Enum):
    message_creation = 'message_creation'
    tool_calls = 'tool_calls'

class RunStep(BaseModel):
    id: UUID
    type: RunStepType
    # run_id: UUID
    conversation_id: UUID
    status: RunStepStatus
    created_at: Optional[int] = None
    cancelled_at: Optional[int] = None
    completed_at: Optional[int] = None
    step_details: Any