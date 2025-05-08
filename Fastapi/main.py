from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from db.config import lifespan
from router.appointment import appointment_router
from router.dentally import dentally_router
from router.elevenlabs import elevanlab_router 



app= FastAPI(lifespan=lifespan)

# cors middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root():
    return {"message": "Hello World"}




app.include_router(router=appointment_router, prefix="/api/v1", tags=["appointments"])
app.include_router(router=dentally_router, prefix="/api/v1", tags=["dentally"])
app.include_router(router=elevanlab_router, prefix="/api/v1", tags=["elevenlabs"])