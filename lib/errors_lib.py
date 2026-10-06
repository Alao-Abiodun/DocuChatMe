class AppError(Exception):
    status_code = 500

    def __init(self, message):
        self.message = message
        super().__init__(message)

class ForbiddenError(AppError):
    status_code = 403

class NotFoundError(AppError):
    status_code = 404

    