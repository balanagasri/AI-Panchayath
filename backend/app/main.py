import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import complaints, dashboard, issues
from app.services.dynamodb_store import dynamodb_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('civicsignal')

app = FastAPI(
    title='CivicSignal API',
    description='Civic complaint and community issue intelligence API.',
    version='0.1.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(complaints.router)
app.include_router(issues.router)
app.include_router(dashboard.router)


@app.on_event('startup')
def startup_event() -> None:
    logger.info('CivicSignal storage backend: %s', dynamodb_store.backend_name)


@app.get('/health', tags=['health'])
def health_check() -> dict[str, str]:
    return {'status': 'ok'}


@app.get('/api/aws-status', tags=['aws'])
def aws_status() -> dict[str, str | bool]:
    mode = dynamodb_store.backend_name
    return {
        'aws_sdk': 'Boto3',
        'production_storage': 'Amazon DynamoDB',
        'mode': mode,
        'aws_configured': mode == 'dynamodb',
    }
