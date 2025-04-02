from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from better_search.api.search_route import router as search_router




def get_application() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(search_router)

    return app


app = get_application()
