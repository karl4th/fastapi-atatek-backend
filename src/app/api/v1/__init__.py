from .auth import router as auth_router
from .system import router as system_router
from .address import router as address_router
from .tree import router as tree_router
from .ticket import router as ticket_router
from .profile import router as profile_router

def include_routers(app):
    app.include_router(auth_router)
    app.include_router(address_router)
    app.include_router(profile_router)
    app.include_router(tree_router)
    app.include_router(ticket_router)

    
    app.include_router(system_router)

    return app