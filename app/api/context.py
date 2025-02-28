from contextvars import ContextVar




global_org_id: ContextVar[str] = ContextVar("global_org_id", default=None)

def get_global_org_id():
    return global_org_id.get()