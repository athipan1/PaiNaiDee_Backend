import json
from sqlalchemy.types import TypeDecorator, TEXT


class JSONEncodedDict(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return "{}"
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == "":
            return {}
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}
