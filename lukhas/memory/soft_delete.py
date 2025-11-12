
import datetime

class SoftDeletable:
    def __init__(self):
        self.is_deleted = False
        self.deleted_at = None

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.datetime.now(datetime.timezone.utc)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
