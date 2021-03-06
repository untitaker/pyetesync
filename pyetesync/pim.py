import peewee as pw
import vobject

from .cache import JournalEntity
from . import db


class BaseContent(db.BaseModel):
    journal = pw.ForeignKeyField(JournalEntity)
    uid = pw.UUIDField(unique=True, null=False, index=True)
    content = pw.BlobField()

    @classmethod
    def apply_sync_entry(cls, journal, sync_entry):
        uid = cls.get_uid(sync_entry)

        if sync_entry.action == 'DELETE':
            try:
                cls.get(uid=uid).delete_instance()
            except cls.DoesNotExist:
                print("WARNING: Failed to delete " + uid)
                pass

            return

        try:
            content = cls.get(uid=uid)
        except cls.DoesNotExist:
            content = cls(journal=journal, uid=uid)

        content.content = sync_entry.content
        content.save()


class Event(BaseContent):
    @classmethod
    def get_uid(cls, sync_entry):
        vobj = vobject.readOne(sync_entry.content)
        return vobj.vevent.uid.value


class Contact(BaseContent):
    @classmethod
    def get_uid(cls, sync_entry):
        vobj = vobject.readOne(sync_entry.content)
        return vobj.uid.value


db.db.create_tables([Event, Contact], safe=True)
