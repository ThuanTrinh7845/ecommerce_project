import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.categories import router as categories_router
from routes.products import router as products_router
from routes.search import router as search_router
from routes.orders import router as orders_router

app = FastAPI(
    title="E-commerce API",
    description="API cho ứng dụng thương mại điện tử",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(search_router)
app.include_router(orders_router)

if __name__ == "__main__":
    print("Đang khởi động máy chủ FastAPI...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True  # Bật log để debug
    )