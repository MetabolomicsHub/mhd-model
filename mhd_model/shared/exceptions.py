class MhdValidationError(Exception):
    pass


class MhdFileSchemaError(MhdValidationError):
    pass


class MhdFileProfileError(MhdValidationError):
    pass
