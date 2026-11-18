#!/usr/bin/env python3
"""Génère le PDF A4 depuis la semaine du guide (macOS, Swift fourni par Xcode)."""
from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
GUIDE = ROOT / 'guides/organiser-repas-famille-gouts-differents'


class Week(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = []
        self.current = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'li' and a.get('class') == 'week-day':
            self.current = {'day': '', 'title': '', 'description': ''}
        if self.current is not None:
            if tag == 'h3':
                self.field = 'title'
            if tag == 'p':
                self.field = 'day' if a.get('class') == 'day-name' else 'description'

    def handle_endtag(self, tag):
        if tag in ('h3', 'p'):
            self.field = None
        if tag == 'li' and self.current is not None:
            self.days.append(self.current)
            self.current = None

    def handle_data(self, data):
        if self.current is not None and self.field:
            self.current[self.field] += data


def build():
    week = Week()
    week.feed((GUIDE / 'index.html').read_text(encoding='utf-8'))
    if len(week.days) != 7 or any(not all(day.values()) for day in week.days):
        raise SystemExit('Le guide doit contenir sept jours complets avant génération.')
    with tempfile.TemporaryDirectory(prefix='madeleine-pdf-') as cache:
        subprocess.run([
            'xcrun', 'swift', '-module-cache-path', cache,
            str(ROOT / 'scripts/build_planning_pdf.swift'),
            str(GUIDE / 'planning-repas-famille.pdf'),
        ], input=json.dumps(week.days, ensure_ascii=False), text=True, check=True)


if __name__ == '__main__':
    build()
