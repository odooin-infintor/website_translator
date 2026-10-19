from odoo import models, fields


class AutoTranslateCache(models.Model):
    _name = "auto.translate.cache"
    _description = "Auto Translation Cache"

    src = fields.Text(required=True)
    lang = fields.Char(required=True)
    value = fields.Text()

    _auto_translate_cache_unique_src_lang = models.Constraint(
        'unique(src, lang)',
        "Translation already exists",
    )