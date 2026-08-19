import requests
import logging
import time
from odoo import api, models

_logger = logging.getLogger(__name__)


class TranslationService(models.AbstractModel):
    _name = "translation.service"
    _description = "Google Translation Service"

    @api.model
    def translate_batch(self, texts, source_lang, target_lang):

        _logger.info(
            "Google Translate batch request | texts: %s | source: %s | target: %s",
            len(texts), source_lang, target_lang
        )

        config = self.env['ir.config_parameter'].sudo()

        enabled = config.get_param('auto_translate.enable_auto_translation')
        api_key = config.get_param('auto_translate.google_api_key')

        if not enabled or not api_key:
            _logger.warning(
                "Translation skipped | enabled: %s | api_key_present: %s",
                enabled, bool(api_key)
            )
            return {
                "translations": texts,
                "success": False
            }

        if source_lang == target_lang:
            _logger.info(
                "Source and target language are same. Skipping translation."
            )
            return {
                "translations": texts,
                "success": True
            }

        url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"

        google_source = source_lang.split('_')[0].split('-')[0]
        google_target = target_lang.split('_')[0].split('-')[0]

        _logger.info(
            "Google Translate payload | source: %s | target: %s | first_text: %s",
            google_source, google_target, texts[0][:60] if texts else ''
        )

        start_time = time.time()

        try:

            translations = []

            # 🚀 Chunking (Google limit = 128)
            batch_size = 120

            for i in range(0, len(texts), batch_size):

                batch = texts[i:i + batch_size]

                payload = {
                    "q": batch,
                    "source": google_source,
                    "target": google_target,
                    "format": "text",
                }

                _logger.info(
                    "Sending translation batch | size: %s | index: %s",
                    len(batch), i
                )

                response = requests.post(url, json=payload, timeout=10)

                if not response.ok:
                    _logger.error(
                        "Google Translate API failed | status: %s | body: %s",
                        response.status_code,
                        response.text,
                    )

                response.raise_for_status()

                data = response.json()

                batch_translations = [
                    t["translatedText"]
                    for t in data["data"]["translations"]
                ]

                translations.extend(batch_translations)

            elapsed = time.time() - start_time

            _logger.info(
                "Google Translate success | translations: %s | time: %.2f seconds",
                len(translations),
                elapsed
            )

            for src, tr in zip(texts, translations):
                if src.strip() == tr.strip():
                    _logger.warning(
                        "Translation identical to source | text: %s | lang: %s",
                        src[:60],
                        target_lang
                    )

            return {
                "translations": translations,
                "success": True
            }

        except requests.exceptions.HTTPError as e:
            _logger.error("Google Translate HTTP error: %s", e)
            return {
                "translations": texts,
                "success": False
            }

        except Exception as e:
            _logger.error("Google Translate API error: %s", e)
            return {
                "translations": texts,
                "success": False
            }