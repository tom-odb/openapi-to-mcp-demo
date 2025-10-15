"""
Logging utilities for MCP server.
"""
import logging
import sys
from mcp.types import LoggingLevel
from typing import Optional, Any
from entities.request_context import get_current_context


def setup_logging():
    """Setup logging configuration for MCP server"""
    # Configure logging to use stderr (stdout is reserved for MCP JSON-RPC)
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        stream=sys.stderr
    )


class ProgressLogger:
    """Progress logging utility for MCP server operations"""
    
    @staticmethod
    async def send_progress(message: str, level: str = "info"):
        """Store progress message and send log notification to MCP client"""
        logger = logging.getLogger(__name__)
        
        # Store the message for inclusion in the final result
        ctx = get_current_context()
        if ctx:
            ctx.add_progress(message)
            
            # Also try to send as log message (for debugging/console output)
            if hasattr(ctx, 'session') and ctx.session:
                try:
                    # Map string level to LoggingLevel enum
                    log_level = {
                        "debug": LoggingLevel.DEBUG,
                        "info": LoggingLevel.INFO,
                        "warning": LoggingLevel.WARNING,
                        "error": LoggingLevel.ERROR
                    }.get(level.lower(), LoggingLevel.INFO)
                    
                    await ctx.session.send_log_message(
                        level=log_level,
                        data=message
                    )
                except Exception as e:
                    logger.debug(f"Could not send progress notification: {e}")
        
        # Also log to stderr
        logger.debug(message)