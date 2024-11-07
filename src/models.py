from pydantic import BaseModel


class DuckDuckGoResult(BaseModel):
    title: str
    href: str
    body: str