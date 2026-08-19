from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_translate_api_key = fields.Char(
        string="Google Translate API Key",
        config_parameter="auto_translate.google_api_key"
    )
    enable_auto_translation = fields.Boolean(
        string="Enable Auto Translation",
        config_parameter="auto_translate.enable_auto_translation"
    )