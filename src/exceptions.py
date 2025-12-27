"""
Custom exceptions for the debate system
"""


class DebateError(Exception):
    """Base exception for debate system"""
    pass


class AgentExecutionError(DebateError):
    """Exception raised when agent execution fails"""
    pass


class ConfigurationError(DebateError):
    """Exception raised when configuration is invalid"""
    pass


class StorageError(DebateError):
    """Exception raised when storage operation fails"""
    pass


class TimeoutError(DebateError):
    """Exception raised when operation times out"""
    pass


class DebateNotFoundError(StorageError):
    """Exception raised when debate is not found in storage"""
    pass
