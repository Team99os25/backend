# This file makes the routes directory a Python package
# Import and expose all route modules

from app.api.routes import employee, conversation, admin, reports

__all__ = ["employee", "conversation", "admin", "reports"]
