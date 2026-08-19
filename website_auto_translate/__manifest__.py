{
    "name": "Website Auto Translate",
    "version": "19.0.1.0.0",
    "summary": "Automatically translate website content using Google Translate API",
    "description": """
    Website Auto Translate
    ======================
    
    This module automatically translates website content dynamically using the Google Translate API.
    
    Features
    --------
    - Automatic website content translation
    - Google Translate API integration
    - Translation caching to reduce API usage
    - Batch translation requests for performance
    - Works with Odoo website frontend
    
    Developed and maintained by Infintor Solutions.
    """,
    "author": "Infintor Solutions",
    "website": "https://www.infintor.com/",
    "maintainer": "Infintor Solutions",
    "category": "Website",

    # --- Licensing & pricing ---
    'license': 'Other proprietary',
    'price': 5.00,
    'currency': 'USD',
    'images': [
        'static/description/banner.png',
    ],

    "depends": [
        "website"
    ],

    "data": [
        "security/ir.model.access.csv",
        "views/settings.xml",
    ],

    "assets": {
        "web.assets_frontend": [
            "website_auto_translate/static/src/js/trans.js"
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False,
}