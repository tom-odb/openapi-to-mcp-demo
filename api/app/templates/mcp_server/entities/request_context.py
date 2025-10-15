"""
Request context management for MCP server requests.
"""
from contextvars import ContextVar
from typing import Optional, Any, List


class RequestContext:
    """Context object for tracking request state and progress"""
    
    def __init__(self):
        self.progress_messages: List[str] = []
        self.session: Optional[Any] = None
    
    def add_progress(self, message: str):
        """Add a progress message"""
        self.progress_messages.append(message)
    
    def get_progress_summary(self) -> str:
        """Get formatted progress summary"""
        if self.progress_messages:
            return "\n\n--- Progress Log ---\n" + "\n".join(self.progress_messages) + "\n--- End Progress Log ---\n\n"
        return ""


# Context variable to store the current request context
request_context_var: ContextVar[Optional[RequestContext]] = ContextVar('request_context', default=None)


def get_current_context() -> Optional[RequestContext]:
    """Get the current request context"""
    return request_context_var.get()


def set_current_context(context: RequestContext) -> None:
    """Set the current request context"""
    request_context_var.set(context)