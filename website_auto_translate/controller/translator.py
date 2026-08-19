from odoo import http
from odoo.http import request
import logging
import time

_logger = logging.getLogger(__name__)


class WebsiteAutoTranslate(http.Controller):

    @http.route(
        "/auto_translate_batch",
        type="json",
        auth="public",
        website=True,
        csrf=False
    )
    def auto_translate_batch(self, texts, target_lang, source_lang="en"):

        _logger.info("Auto Translate Controller triggered")
        _logger.info(
            "Received translation request | texts: %s | source: %s | target: %s",
            len(texts), source_lang, target_lang
        )

        start_time = time.time()

        lang = target_lang.replace("-", "_")

        cache_model = request.env['auto.translate.cache'].sudo()
        service = request.env['translation.service']

        translations = []
        texts_to_translate = []
        index_map = []

        # 1️⃣ Cache Check
        for i, text in enumerate(texts):

            if not text or not text.strip():
                translations.append(text)
                continue

            existing = cache_model.search([
                ('src', '=', text),
                ('lang', '=', lang),
            ], limit=1)

            # valid cache
            if existing and existing.value:

                _logger.debug("Cache hit for text: %s", text[:50])
                translations.append(existing.value)

            else:

                translations.append(None)
                texts_to_translate.append(text)
                index_map.append(i)

                if existing:
                    _logger.warning(
                        "Ignoring bad cache entry | src=%s value=%s",
                        text[:50],
                        existing.value[:50] if existing.value else None
                    )

        _logger.info(
            "Cache check completed | cached: %s | to_translate: %s",
            len(texts) - len(texts_to_translate),
            len(texts_to_translate)
        )

        # 2️⃣ Translate uncached texts
        if texts_to_translate:

            _logger.info(
                "Calling translation service for %s texts",
                len(texts_to_translate)
            )

            # Remove duplicates
            unique_texts = list(dict.fromkeys(texts_to_translate))

            _logger.info(
                "Unique texts for translation | before: %s | after: %s",
                len(texts_to_translate),
                len(unique_texts)
            )

            # Call translation service
            result = service.translate_batch(
                unique_texts,
                source_lang[:2],
                lang[:2],
            )

            unique_translations = result["translations"]
            api_success = result["success"]

            # Map results
            translation_map = dict(zip(unique_texts, unique_translations))
            new_translations = [translation_map[t] for t in texts_to_translate]

            for i, translated in enumerate(new_translations):

                original_text = texts_to_translate[i]
                index = index_map[i]
                translations[index] = translated

                # skip caching if API failed and translation unchanged
                if translated.strip() == original_text.strip() and not api_success:

                    _logger.warning(
                        "Skipping cache save because API failed | text: %s",
                        original_text[:50]
                    )
                    continue

                existing_cache = cache_model.search([
                    ('src', '=', original_text),
                    ('lang', '=', lang),
                ], limit=1)

                try:

                    with request.env.cr.savepoint():

                        value_to_store = translated if translated else original_text

                        if existing_cache:

                            existing_cache.write({
                                'value': value_to_store
                            })

                            _logger.debug(
                                "Updated cache entry: %s",
                                original_text[:50]
                            )

                        else:

                            cache_model.create({
                                'src': original_text,
                                'lang': lang,
                                'value': value_to_store,
                            })

                            _logger.debug(
                                "Saved translation to cache: %s",
                                original_text[:50]
                            )

                except Exception:

                    _logger.warning(
                        "Race condition detected while updating cache"
                    )

        # 3️⃣ Fallback
        translations = [
            t if t is not None else texts[i]
            for i, t in enumerate(translations)
        ]

        elapsed = time.time() - start_time

        _logger.info(
            "Translation request finished | total: %s | time: %.2f seconds",
            len(texts),
            elapsed
        )

        return {"translations": translations}