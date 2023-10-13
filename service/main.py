import asyncio

import uvicorn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from service.common.api.config import api_server_config
from service.common.api.main import create_application
from service.common.config import db_config
from service.common.utils import get_db_url
from service.domain.models import Base
from service.common.orm import reinit_models

app = create_application()


@app.on_event('startup')
async def startup():
    # db_url = get_db_url(db_config.driver,
    #                     db_config.host,
    #                     db_config.port,
    #                     db_config.user,
    #                     db_config.password,
    #                     db_config.name)
    # engine = create_async_engine(db_url)
    # async_session = async_sessionmaker(engine, expire_on_commit=False)

    # await reinit_models(engine, Base)
    pass


if __name__ == "__main__":
    # asyncio.run(startup())
    uvicorn.run(app, host=api_server_config.host, port=api_server_config.port)
