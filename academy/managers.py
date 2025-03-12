from django.db.models import Manager


class CommentManager(Manager):
    def all_active(self):
        return self.filter(active = True)

class CommentManager2(Manager):
    def all_active(self):
        return self.filter(active=True)
