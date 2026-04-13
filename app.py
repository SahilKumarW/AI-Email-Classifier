from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import os

app = Flask(__name__)
CORS(app)

def classify_email(subject, body):
    """Classify email based on content"""
    full_text = f"{subject}. {body}".lower()
    
    # Billing keywords
    billing_words = ['refund', 'charge', 'payment', 'invoice', 'subscription', 'bill', 'money', 'cost', 'price', 'fee', 'financial']
    # Academic keywords
    academic_words = ['lecture', 'cancelled', 'slides', 'class', 'course', 'module', 'seminar', 'assignment', 'deadline', 'learning central']
    # Hardware keywords
    hardware_words = ['laptop', 'screen', 'keyboard', 'mouse', 'battery', 'charger', 'usb', 'monitor', 'fan', 'printer']
    # Access keywords
    access_words = ['password', 'login', 'vpn', 'account', 'locked', 'permission', 'access', 'admin']
    # Software keywords
    software_words = ['crash', 'freeze', 'slow', 'error', 'excel', 'teams', 'outlook', 'chrome', 'update', 'install']
    # Emergency keywords
    emergency_words = ['help', 'urgent', 'emergency', 'attack', 'danger', 'immediate', 'critical', 'crisis']
    
    # Calculate scores
    scores = {
        'billing': sum(1 for word in billing_words if word in full_text),
        'academic': sum(1 for word in academic_words if word in full_text),
        'hardware': sum(1 for word in hardware_words if word in full_text),
        'access': sum(1 for word in access_words if word in full_text),
        'software': sum(1 for word in software_words if word in full_text),
        'emergency': sum(1 for word in emergency_words if word in full_text),
        'general': 0
    }
    
    # Find best category
    best_category = max(scores, key=scores.get)
    max_score = scores[best_category]
    
    # Calculate confidence
    if max_score == 0:
        best_category = 'general'
        confidence = 30
    else:
        confidence = min(50 + (max_score * 8), 95)
    
    # Determine action
    if best_category == 'emergency':
        action = 'HUMAN REVIEW - URGENT'
        auto_reply = None
    elif confidence >= 65:
        action = 'Auto-Reply'
        auto_reply = get_response_template(best_category)
    else:
        action = 'Human Review Recommended'
        auto_reply = None
    
    # Special cases
    if 'out of office' in full_text or 'annual leave' in full_text:
        best_category = 'out of office'
        action = 'No Action Needed'
        confidence = 90
        auto_reply = None
    
    if 'spam' in full_text or 'test' in full_text:
        best_category = 'spam'
        action = 'Filter / Ignore'
        confidence = 85
        auto_reply = None
    
    return {
        'category': best_category.upper(),
        'confidence': confidence,
        'action': action,
        'auto_reply': auto_reply,
        'matched_keywords': max_score
    }

def get_response_template(category):
    """Return appropriate auto-reply template"""
    templates = {
        'billing': 'Thank you for your billing inquiry. Our finance team will review your request and respond within 2 business days.',
        'academic': 'Thank you for your course notification. This has been noted. For questions, please contact your module coordinator.',
        'hardware': 'Your hardware issue has been logged. Please bring your device to the IT support desk for assessment.',
        'access': 'Your access request has been submitted. You will receive a response within 2 hours.',
        'software': 'Your software issue has been logged. Please try restarting the application. IT will investigate if the problem persists.',
        'general': 'Thank you for your message. The appropriate team will review and respond shortly.'
    }
    return templates.get(category, 'Thank you for your message. The appropriate team will respond.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    subject = data.get('subject', '')
    body = data.get('body', '')
    
    result = classify_email(subject, body)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

# For Vercel serverless
app = app