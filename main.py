from fastapi import FastAPI
from contextlib import asynccontextmanager
from kernel.kernel import Kernel

kernel = Kernel()
kernel.discover()

app = FastAPI(
    title="Islam Mate API",
    description="Open-source REST API for Muslim developers. Prayer times, Quran, Hadith, Azkar, and 50+ more features.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

kernel.register_routes(app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await kernel.init_services()
    yield
    await kernel.shutdown()

app.router.lifespan_context = lifespan


@app.get("/")
async def root():
    return {
        "name": "Islam Mate API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }
