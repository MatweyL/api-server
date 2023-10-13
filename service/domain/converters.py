from pydantic import BaseModel
from sqlalchemy import inspect


def map_schema_to_model(obj_schema: BaseModel, sqlalchemy_model):
    columns = inspect(sqlalchemy_model).c
    columns_names = [column.name for column in columns]
    obj_model = sqlalchemy_model(**{column_name: getattr(obj_schema, column_name)
                                    for column_name in columns_names if hasattr(obj_schema, column_name)})
    return obj_model
