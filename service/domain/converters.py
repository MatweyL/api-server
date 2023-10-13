from typing import Type

from pydantic import BaseModel
from sqlalchemy import inspect

from service.domain.models import TaskGenerationModel


def map_schema_to_model(obj_schema: BaseModel, sqlalchemy_model):
    columns = inspect(sqlalchemy_model).c
    columns_names = [column.name for column in columns]
    obj_model = sqlalchemy_model(**{column_name: getattr(obj_schema, column_name)
                                    for column_name in columns_names if hasattr(obj_schema, column_name)})
    return obj_model


def map_model_to_schema(obj_model, pydantic_schema: Type[BaseModel]):
    obj_schema = pydantic_schema.model_validate(obj_model, from_attributes=True)
    return obj_schema


def map_model_with_existing_schema(obj_model, existing_obj_schema: BaseModel, pydantic_schema: Type[BaseModel]):
    columns = inspect(obj_model.__class__).c
    columns_names = {column.name for column in columns}
    columns_names.discard('task_uid')
    obj_schema = pydantic_schema(**existing_obj_schema.model_dump(),
                                 **{column_name: getattr(obj_model, column_name)
                                    for column_name in columns_names if hasattr(obj_model, column_name)})
    return obj_schema
