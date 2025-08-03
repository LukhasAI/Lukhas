#!/usr/bin/env python3
"""
Dream Interpreter Web App - Flask version
A web-based dream interpreter with multi-language support
"""

from flask import Flask, render_template, request, jsonify
import json
import locale
import os
from dream_interpreter import DreamInterpreter
import openai


app = Flask(__name__)


class WebDreamInterpreter(DreamInterpreter):
    """Web-enabled version of the dream interpreter"""

    def __init__(self, app_locale=None):
        super().__init__(app_locale)

    def to_json(self):
        """Convert interpretation to JSON format for web response"""
        if not self.interpretation:
            return None

        return {
            "mainThemes": self.interpretation.main_themes,
            "emotionalTone": self.interpretation.emotional_tone,
            "symbols": [
                {"symbol": s.symbol, "meaning": s.meaning}
                for s in self.interpretation.symbols
            ],
            "personalInsight": self.interpretation.personal_insight,
            "guidance": self.interpretation.guidance
        }

    def get_translations_for_locale(self):
        """Get all translations for the current locale"""
        return self.TRANSLATIONS.get(self.locale, self.TRANSLATIONS['en-US'])


# Global interpreter instance
interpreter = WebDreamInterpreter()


# Mock AI function - replace with your actual AI integration
def ai_complete_function(prompt):
    """Replace this with your actual AI completion function"""
    # This is a mock response - integrate with OpenAI, Claude, or other AI service
    return json.dumps({
        "mainThemes": ["Transformation", "Journey", "Discovery"],
        "emotionalTone": "The dream carries undertones of curiosity and mild anxiety, suggesting you're on the verge of an important personal discovery.",
        "symbols": [
            {"symbol": "Path", "meaning": "Your life journey and the choices ahead"},
            {"symbol": "Light", "meaning": "Clarity and enlightenment coming into your life"}
        ],
        "personalInsight": "This dream suggests you're at a crossroads where important decisions will shape your future. Trust your intuition.",
        "guidance": "Take time for reflection before making major decisions. The answers you seek are within you."
    })


@app.route('/')
def index():
    """Main page"""
    return render_template('dream_interpreter.html',
                         translations=interpreter.get_translations_for_locale(),
                         locale=interpreter.locale)


@app.route('/interpret', methods=['POST'])
def interpret_dream():
    """API endpoint to interpret a dream"""
    try:
        data = request.get_json()
        dream_text = data.get('dreamText', '').strip()

        if not dream_text:
            return jsonify({'error': 'No dream text provided'}), 400

        # Set locale if provided
        if 'locale' in data:
            interpreter.locale = interpreter._find_matching_locale(data['locale'])

        interpreter.set_dream_text(dream_text)
        interpretation = interpreter.interpret_dream_with_ai(ai_complete_function)

        if interpretation:
            return jsonify({
                'success': True,
                'interpretation': interpreter.to_json()
            })
        else:
            return jsonify({
                'success': False,
                'error': interpreter.error or interpreter.t('interpretationError')
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': interpreter.t('interpretationError')
        }), 500


@app.route('/translations/<locale_code>')
def get_translations(locale_code):
    """Get translations for a specific locale"""
    temp_interpreter = WebDreamInterpreter()
    temp_interpreter.locale = temp_interpreter._find_matching_locale(locale_code)
    return jsonify(temp_interpreter.get_translations_for_locale())


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
