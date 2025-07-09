from django.contrib import admin
from django import forms
from markdownx.admin import MarkdownxModelAdmin
from .widgets import EditorMDWidget
from .models import Article  # 👈 這樣引用


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'content': EditorMDWidget()
        }


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm


admin.site.register(Article, ArticleAdmin)


# @admin.register(models.Article)
# class ArticleAdmin(MarkdownxModelAdmin):
#     class Media:
#         js = (
#             'markdownx/js/markdownx.js',
#             'library/markdown_buttons.js',  # 自訂語法按鍵
#         )
#         css = {
#             'all': ('markdownx/css/markdownx.css',),
#         }
#     list_display = ['title', 'content', 'created_at', 'updated_at']
#     list_editable = ['content']
#     list_per_page = 20
