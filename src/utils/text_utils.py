from __future__ import annotations

import re
from typing import List


ARABIC_DIACRITICS_RE = re.compile(r"[\u0617-\u061A\u064B-\u0652]")
MULTISPACE_RE = re.compile(r"[ \t]+")
MULTINEWLINE_RE = re.compile(r"\n{3,}")
TATWEEL_RE = re.compile(r"ـ+")
ARABIC_CHARS_RE = re.compile(r"[\u0600-\u06FF]")


TRANSLATION_TABLE = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ة": "ه",
    }
)


AR_STOPWORDS = {
    "في", "من", "على", "إلى", "عن", "ما", "ماذا", "هل", "كيف",
    "هذا", "هذه", "ذلك", "تلك", "هناك", "هنا", "ثم", "او", "أو",
    "the", "and", "or"
}


def normalize_arabic(text: str) -> str:
    text = TATWEEL_RE.sub("", text)
    text = ARABIC_DIACRITICS_RE.sub("", text)
    text = text.translate(TRANSLATION_TABLE)
    text = MULTISPACE_RE.sub(" ", text).strip()
    return text


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\xa0", " ")
    text = text.replace("\r", "\n")
    text = text.replace("\t", " ")

    lines = []
    for line in text.splitlines():
        line = MULTISPACE_RE.sub(" ", line).strip()
        if not line:
            continue
        lines.append(line)

    text = "\n".join(lines)
    text = MULTINEWLINE_RE.sub("\n\n", text).strip()
    return text


def detect_language(text: str) -> str:
    if not text:
        return "unknown"

    arabic_chars = len(ARABIC_CHARS_RE.findall(text))
    letters = sum(1 for ch in text if ch.isalpha())

    if letters == 0:
        return "unknown"

    ratio = arabic_chars / letters
    return "ar" if ratio >= 0.25 else "unknown"


def classify_content_type(text: str, title: str = "") -> str:
    hay = normalize_arabic(f"{title} {text}".lower())

    if any(k in hay for k in [
        "مواعيد", "ساعات العمل", "ساعات الزياره", "اوقات الزياره",
        "opening hours", "working hours", "visit hours"
    ]):
        return "visit_info"

    if any(k in hay for k in [
        "خطط لزيارتك", "خطط لزيارتك", "خطط زيارتك", "خطط", "الزياره",
        "plan your visit", "visitor information", "visit information"
    ]):
        return "visit_plan"

    if any(k in hay for k in [
        "تذكر", "تذاكر", "ticket", "tickets", "booking", "حجز"
    ]):
        return "tickets"

    if any(k in hay for k in [
        "خدمات", "الخدمات", "service", "services"
    ]):
        return "services"

    if any(k in hay for k in [
        "مرافق", "المرافق", "facility", "facilities", "amenities"
    ]):
        return "facilities"

    if any(k in hay for k in [
        "تعليمي", "التعليمي", "التعليم", "مركز تعليمي",
        "education", "educational", "learning", "children museum"
    ]):
        return "education"

    if any(k in hay for k in [
        "اتصل", "contact", "العنوان", "location", "address", "يقع", "ميدان", "شارع"
    ]):
        return "contact"

    if any(k in hay for k in [
        "معرض", "exhibit", "gallery", "قاعة"
    ]):
        return "exhibits"

    if any(k in hay for k in [
        "الاسئله الشائعه", "الاسئلة الشائعة", "faq", "frequently asked questions"
    ]):
        return "faq"

    if any(k in hay for k in [
        "فعالي", "event", "news", "اخبار"
    ]):
        return "events"

    return "general"


def simple_tokenize(text: str) -> List[str]:
    text = normalize_arabic(text.lower())
    text = re.sub(r"[^\w\u0600-\u06FF]+", " ", text)
    tokens = [tok for tok in text.split() if tok and tok not in AR_STOPWORDS and len(tok) > 1]
    return tokens