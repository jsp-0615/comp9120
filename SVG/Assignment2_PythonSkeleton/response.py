class Response:
    def __init__(self, success: bool, message: str, status_code: int, data=None):
        self.success = success
        self.message = message
        self.status_code = status_code
        self.data = data

    @classmethod
    def success(cls, message="Success", data=None):
        return cls(True, message, 200, data)

    @classmethod
    def error(cls, message="Error", status_code=400):
        return cls(False, message, status_code)

    def to_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "status_code": self.status_code,
            "data": self.data
        }
