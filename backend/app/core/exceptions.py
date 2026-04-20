class RatingAppException(Exception):
    pass


class ImportValidationError(RatingAppException):
    pass


class EmployeeNotFoundError(RatingAppException):
    pass


class SnapshotNotFoundError(RatingAppException):
    pass

