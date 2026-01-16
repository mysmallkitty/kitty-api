from fastapi import Query
from typing import Optional

class MapFilterParams:
    def __init__(
        self,
        title: Optional[str] = Query(None),
        creator: Optional[str] = Query(None),
        sort: str = Query("latest"),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100)
    ):
        self.title = title
        self.creator = creator
        self.sort = sort
        self.page = page
        self.size = size
        self.offset = (page - 1) * size