import spacy
from spacy.matcher import Matcher
from datetime import datetime, timedelta
import re

nlp = spacy.load('ru_core_news_sm')
matcher = Matcher(nlp.vocab)

# Паттерны для создания напоминаний
create_patterns = [
    [{"LOWER": {"IN": ["создай", "напомни", "назначь"]}}, {"LOWER": {"IN": ["встречу", "напоминание", "мне"]}}],
    [{"LOWER": "напоминание"}]
]
matcher.add("CREATE_REMINDER", create_patterns)

def process_text(text):
    doc = nlp(text.lower())
    
    # Intent
    intent = "unknown"
    confidence = 0.3
    matches = matcher(doc)
    for match_id, start, end in matches:
        if nlp.vocab.strings[match_id] == "CREATE_REMINDER":
            intent = "create_reminder"
            confidence = 0.9
    
    # Fallback для intent
    if intent == "unknown" and any(word in text.lower() for word in ["создай", "напомни", "назначь"]):
        intent = "create_reminder"
        confidence = 0.7
    
    # Параметры
    params = {"title": "", "description": "", "datetime": None, "date": None, "time": None}
    
    if intent == "create_reminder":
        # Разделяем текст: убираем триггер
        trigger_pattern = r'(создай|напомни|назначь|привет)\s*(мне)?\s*'
        remaining_text = re.sub(trigger_pattern, '', text.lower(), flags=re.IGNORECASE).strip()
        
        # Извлекаем дату/время через NER
        for ent in doc.ents:
            if ent.label_ == "DATE" and ent.text in remaining_text:
                params["date"] = normalize_date(ent.text)
            elif ent.label_ == "TIME" and ent.text in remaining_text:
                params["time"] = re.sub(r'(в|на|к)\s*', '', ent.text).strip()
        
        # Fallback regex для времени
        time_match = re.search(r'(?:в|на|к| )?(\d{1,2}):?(\d{2})?\s*(утра|вечера)?', remaining_text)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            if period == "вечера" and hours < 12:
                hours += 12
            elif period == "утра" and hours == 12:
                hours = 0
            params["time"] = f"{hours:02d}:{minutes:02d}"
        
        # Fallback regex для даты
        if "завтра" in remaining_text:
            date = datetime.now() + timedelta(days=1)
            params["date"] = date.strftime("%Y-%m-%d")
        elif "послезавтра" in remaining_text:
            date = datetime.now() + timedelta(days=2)
            params["date"] = date.strftime("%Y-%m-%d")
        
        # Title и description
        words = [w for w in remaining_text.split() if w]
        if words:
            params["description"] = " ".join(words)
            params["title"] = " ".join(words[:5])
        
        # Сборка datetime
        if params["date"]:
            params["datetime"] = f"{params['date']} {params['time'] or '00:00'}"
    
    # Если нет параметров, снижаем confidence
    if not any(params.values()):
        confidence -= 0.2
    
    return {
        "intent": intent,
        "parameters": params,
        "original_text": text,
        "confidence": max(0.1, confidence)
    }

def normalize_date(date_text):
    now = datetime.now()
    date_text = date_text.lower()
    if "завтра" in date_text:
        return (now + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "послезавтра" in date_text:
        return (now + timedelta(days=2)).strftime("%Y-%m-%d")
    return None