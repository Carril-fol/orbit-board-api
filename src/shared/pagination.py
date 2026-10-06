from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class PageParams(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="Maximum number of items to return.")
    offset: int = Field(0, ge=0, description="Number of items to skip.")


Pagination = Annotated[PageParams, Query()]
