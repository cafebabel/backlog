from flask import current_app, url_for
from mongoengine import signals, errors, ValidationError

from ... import db
from ...users.models import User
from ...articles.models import Article


class Translation(Article):
    translator = db.ReferenceField(User, required=True)
    original_article = db.ReferenceField('Article', required=True)

    @property
    def detail_url(self):
        if self.is_draft:
            return url_for('translations.detail', id=self.id)
        else:
            return url_for('articles.detail', slug=self.slug,
                           article_id=self.id)

    @property
    def is_translation(self):
        return True

    @property
    def image_url(self):
        if self.has_image:
            return (f'{current_app.config.get("ARTICLES_IMAGES_URL")}/'
                    f'{self.original_article.id}')

    def clean(self):
        super().clean()
        try:
            Article.objects.get(id=self.original_article.id,
                                language=self.language)
            raise ValidationError('Original article in the same language.')
        except Article.DoesNotExist:
            pass

    @classmethod
    def check_duplicate(cls, sender, document, **kwargs):
        first = Translation.objects(original_article=document.original_article,
                                    language=document.language).first()
        if ((first and first != document)
                or document.language == document.original_article.language):
            raise errors.NotUniqueError(
                'This article already exists in this language.')
        return document


signals.pre_save.connect(Article.update_publication_date, sender=Translation)
signals.pre_save.connect(Translation.check_duplicate, sender=Translation)
signals.pre_save.connect(Article.update_slug, sender=Translation)
signals.post_save.connect(Article.store_image, sender=Translation)
signals.pre_delete.connect(Article.delete_image_file, sender=Translation)
