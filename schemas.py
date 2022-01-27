from urllib.parse import ParseResult, urlparse

import validators
from pydantic import BaseModel, validator


class VisitedLinksIn(BaseModel):
    """
        Проводит валидацию входящих ссылок
    """
    links: set[str]

    class Config:
        schema_extra = {
            "example": {
                "links": [
                    "https://ya.ru",
                    "https://ya.ru?q=123",
                    "funbox.ru",
                    "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
                ]
            }
        }


    @validator('links', each_item=True, pre = True)
    def validate_links(cls, value: str):
        if not (is_url := validators.url(value)):
            if not (is_domain := validators.domain(value)):
                raise ValueError(f"ValueError: {value!r} must me a 'url' or 'domain'")

        
        parsed_value: ParseResult = urlparse(value)
        return parsed_value.netloc if is_url else parsed_value.path

    


    

    


    

