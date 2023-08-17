from django.contrib import admin
from .models import Planet, TermsOfService, Post, Comment, InappropriateWord, Report, VoteTopic, Vote

# Register your models here.

admin.site.register(Planet)
admin.site.register(TermsOfService)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(InappropriateWord)
admin.site.register(Report)
admin.site.register(VoteTopic)
admin.site.register(Vote)
