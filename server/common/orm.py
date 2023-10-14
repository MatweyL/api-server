from sqlalchemy.orm import declarative_base

Base = declarative_base()


async def reinit_models(engine, base):
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.drop_all)
        await conn.run_sync(base.metadata.create_all)
