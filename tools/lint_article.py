#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Линтер SEO-статей для пайплайна проверки.

Запуск: python tools/lint_article.py статья.md [--full] [--gpu] [--quiet]
Домен своего сайта задаётся в SITE_DOMAIN: по нему ссылки делятся на внутренние и внешние.
"""

import re
import sys
from collections import Counter, defaultdict

# ---------------------------------------------------------------- нормативы

SITE_DOMAIN = 'example.com'   # домен своего сайта

VOLUME_MIN = 11000
VOLUME_MAX = 16000
LONG_SENTENCE = 28          # слов, порог пересборки
SHORT_SENTENCE = 8          # слов, нижняя граница
SHORT_SHARE_MAX = 0.25      # доля коротких предложений, критерий отказа
SHORT_RUN_MAX = 2           # подряд коротких, 3 и более — отказ
SUBHEAD_EVERY_MAX = 500     # знаков между подзаголовками
RHYTHM_SD_MIN = 5.0         # замерено 19.10.2026 на шести опубликованных статьях: 5.1 … 6.7
                            # стандартное отклонение длины предложения, ниже — монотонный ритм
WATER_PER_1000_MAX = 12     # канцелярских абстракций на 1000 слов
LEAD_H1_OVERLAP_MIN = 0.4   # доля значимых слов H1, которые должны быть в первом абзаце

# ---------------------------------------------------------------- словари

CONNECTIVES = [
    'при этом', 'важно понимать', 'таким образом', 'в свою очередь',
    'кроме того', 'как правило', 'в целом', 'на самом деле', 'в то же время',
    'следует отметить', 'стоит отметить', 'необходимо отметить',
    'поэтому', 'однако', 'вместе с тем', 'при том что',
]
ABSOLUTES = [
    'исключен', 'исключён', 'исключает', 'исключено', 'исключить полностью',
    'гарантир', 'полностью защищ', 'полностью исключ', 'абсолютн',
    'никогда не', 'всегда работает', 'невозможно', 'отсутствует риск',
    'риск отсутствует', '100% защит', 'обеспечивает полную', 'без исключений',
    'снимает риск', 'решает все', 'закрывает все',
]
CONDESCENDING = [
    'путают', 'путается', 'путаются', 'не понимает', 'не понимают',
    'заблуждаются', 'заблуждение', 'многие думают', 'ошибочно полагают',
    'мало кто знает', 'не задумывается',
]
# Ловушки по фактам продукта и предметной области. Сюда вносятся формулировки,
# которые уже признаны ошибочными: устаревшие цифры, неверные термины.
CANON_TRAPS = [
        (r'плейсхолдер', 'использовать «технические метки»'),
    (r'MI300X[^.]{0,60}HGX|HGX[^.]{0,60}MI300X', 'MI300X не относится к платформе NVIDIA HGX'),
    (r'(MIG|vGPU)[^.]{0,80}(взаимозаменя|вместо)', 'MIG и vGPU дополняют друг друга'),
    (r'подробнее\s+в\s+раздел|см\.\s+раздел|как\s+сказано\s+выше',
     'кросс-ссылки на другие разделы не использовать'),
]
GPU_TRAPS = [
    (r'(4[–-]5|3[–-]7|6[–-]7)\s*%[^.]{0,40}(оверхед|нативн|виртуализац)',
     'снятые цифры оверхеда: VMware 2018 и Indiana University не использовать'),
    (r'MIG[^.]{0,40}профил\w+[^.]{0,40}(12|24|48|96)',
     'проверить уровень: профиль MIG-backed или time-sliced на всю карту'),
    (r'A16[^.]{0,60}MIG|MIG[^.]{0,60}A16',
     'проверить формулировку: A16 не поддерживает MIG, отрицание допустимо'),
    (r'NVLink[^.]{0,30}\d+[,.]?\d*\s*(ТБ/с|ГБ/с)',
     'указать уровень: 1,8 ТБ/с на GPU = 14,4 ТБ/с на узел из 8 GPU'),
    (r'vGPU[^.]{0,40}(лучше|хуже)[^.]{0,20}MIG|MIG[^.]{0,40}(лучше|хуже)[^.]{0,20}vGPU',
     'сравниваются разные уровни: vGPU это способ поставки, MIG режим разделения'),
    (r'DGX[^.]{0,40}HGX|HGX[^.]{0,40}DGX', 'HGX это baseboard, DGX готовая система'),
    (r'\bпроброс\w*\b', 'жаргон: «передача карты целиком» или PCIe Passthrough'),
    (r'\bжелез\w+\b', 'жаргон: «оборудование» или «аппаратные ресурсы»'),
    (r'банк\w+\s+L2', 'калька: «блоки кеш-памяти второго уровня»'),
    (r'бенчмарк', 'жаргон, заменить на «тест», ловится и внутри составных слов'),
    (r'\bburst\b', 'термина нет у NVIDIA: «гарантированная доля» или «доступ по остаточному принципу»'),
    (r'[а-яё]\s+VM\b|\bVM\s+[а-яё]', 'аббревиатуру писать кириллицей: ВМ'),
    (r'(?m)^\s*(\$|sudo |python3? |git clone|\./|nvidia-smi )',
     'командная строка в тексте: статьи кластера не инженерный гайд'),
    (r'\s--[a-z]{2,}\b', 'флаг утилиты: инструмент называем, команды не приводим'),
]
# Отклонённые/чужие цифры из индекса канона: если попали в текст — почти
# наверняка утечка из старого черновика или из чужого материала.
REJECTED_TRAPS = [
    (r'DORA[^.]{0,60}2024', 'DORA 2024 устарела и развернулась в 2025, не цитировать'),
    (r'35\s*%[^.]{0,40}(рекомендац|Amazon)|Amazon[^.]{0,40}35\s*%',
     'Amazon «35% выручки от рекомендаций» — источника нет'),
    (r'75\s*%[^.]{0,40}(просмотр|Netflix)|Netflix[^.]{0,40}75\s*%',
     'Netflix «75% просмотров» — не подтверждено, верно 80% часов'),
    (r'росс\w+\s+ускорител\w+[^.]{0,30}SOPHGO|SOPHGO[^.]{0,30}росс\w+',
     'SOPHGO — китайский производитель, не «российский ускоритель»'),
]
IMPERSONAL_OPENINGS = [
    (r'^У\s+\S+(?:\s+\S+){0,6}\s+есть\s+(?:обратн\w*\s+сторон\w*|цена\b|своя\s+цена)',
     'безличный зачин «у X есть обратная сторона/цена»'),
    (r'^Это\s+имеет\s+цену', 'безличный зачин «это имеет цену»'),
    (r'^Отдельн\w+\s+(?:ограничени\w*|особенност\w*|момент\w*)\s+касается',
     'безличный зачин «отдельное ограничение касается»'),
    (r'^Есть\s+(?:ограничени\w*|особенност\w*),\s+котор\w+\s+касается',
     'безличный зачин «есть ограничение, которое касается»'),
]
SCHOOL_NUMBERING = re.compile(
    r'\b(?:Перв\w+|Втор\w+|Треть\w+|Четверт\w+)\s*[:,]\s|'
    r'\bво-(?:первых|вторых|третьих)\b|'
    r'\bЕсть\s+и\s+(?:втор\w+|треть\w+)\s+(?:причин\w+|способ\w*|аргумент\w*)\b',
    re.I)
PARTICIPLE_CALQUE = re.compile(
    r'\b(?:описывает|заявляет|представляет|называет)\s+\S+(?:\s+\S+){0,3}\s+как\s+\w*(?:ющ|ущ|ащ|ящ)\w*',
    re.I)
# «ключ» намеренно не включён: в GPU/AI-статьях это почти всегда API-ключ,
# SSH-ключ или ключ шифрования, а не жаргонное «ключевое слово». Проверять
# глазами по канону, автоматика даёт слишком много ложных срабатываний.
SEO_JARGON = [r'\bинтент\w*\b', r'\bанкор\w*\b', r'\bв\s+выдач\w*\b']
GRAMMAR_FIXES = [
    (r'до\s+того\s+момента,\s+пока', 'до тех пор, пока'),
]
CLOSING_MARKERS = ['ценност', 'вывод', 'итог', 'обобщ']
MODEL_COUNT = r'(?:\d{2,3}\s*\+|более\s+чем\s+\d{2,3}|более\s+\d{2,3}|свыше\s+\d{2,3})\s*(?:языков\w+\s+)?(?:модел|LLM)'
RU_LOCALES_BAD = r'/ru-(?!ru)(?:kz|uz|by|kg|am|az|ge|md|tj|uа)/'
DRAFT_JUNK = [
    (r'\[\d+\](?:\[\d+\])*', 'маркеры сносок'),
    (r'(?i)инфографика\s*\d*\s*[:«]', 'технические метки инфографики'),
    (r'(?i)\bTODO\b|\bFIXME\b|\bXXX\b|\?\?\?', 'служебные пометки'),
    (r'(?i)lorem ipsum', 'рыба'),
    (r'(?i)в\s+исходной\s+версии\s+стать|в\s+предыдущей\s+редакци',
     'редакторская ремарка о самой статье'),
    (r'\s+[.,:;!?](?:\s|$)', 'пробел перед знаком препинания'),
    (r'[ \t]{2,}', 'двойной пробел'),
]
CALQUES = [
    'компаундир', 'имплементац', 'челлендж', 'юзкейс', 'воркфлоу', 'пайплайн',
    'бенефит', 'экспертиз', 'коллаборац', 'релевантност',
    'скейлинг', 'перформанс', 'аджастить', 'фиксить', 'чекать', 'апдейт',
    'фича', 'таргет', 'инсайт', 'драйвер рост', 'быть в фокусе',
]
CATEGORICAL = [
    'главная ошибка', 'главное заблуждение', 'не существует', 'никакого',
    'ничего общего', 'единственно верн', 'все думают', 'принято считать',
]
WATER = [
    'как правило', 'в целом', 'в частности', 'в том числе и', 'ряд ',
    'некоторые', 'различные', 'определённ', 'определенн', 'соответствующ',
    'данный', 'данная', 'данные о', 'указанн', 'вышеуказанн', 'необходимо отметить',
    'является', 'производит ', 'представляет собой',
    'зачастую', 'в ряде случаев', 'тот или иной',
    'та или иная', 'в рамках', 'с точки зрения', 'на сегодняшний день',
    'в настоящее время', 'играет важную роль', 'имеет значение',
]
EDITOR_REMARKS = [
    'практический вывод', 'разберём', 'разберем', 'рассмотрим подробнее',
    'о чём речь', 'о чем речь', 'что важно в этом', 'подведём итог',
    'практический путь', 'отдельная задача —', 'на практике это значит',
    'вот так выглядит', 'корректная формулировка для',
]
YO_PAIRS = [('все', 'всё'), ('еще', 'ещё'), ('дает', 'даёт'), ('идет', 'идёт'),
            ('нее', 'неё'), ('чем', 'чём'), ('счет', 'счёт'), ('учет', 'учёт')]
STOPWORDS = set('''и в во не что он на я с со как а то все она так его но да ты к у же
вы за бы по только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг
ли если уже или ни быть был него до вас нибудь опять уж вам ведь там потом себя ничего
ей может они тут где есть надо ней для мы тебя их чем была сам чтоб без будто чего раз
тоже себе под будет ж тогда кто этот того потому этого какой ним здесь этом один почти
мой тем чтобы нее сейчас были куда зачем всех никогда можно при наконец два об другой
хоть после над больше тот через эти нас про всего них какая много разве три эту моя
впрочем хорошо свою этой перед иногда лучше чуть том нельзя такой им более всегда
конечно всю между это'''.split())

VERB_HINT = re.compile(
    r'(?:ть|ти|чь|ет|ёт|ут|ют|ит|ат|ят|ает|яет|еет|уют|ируют|ся|сь|шь|'
    r'ется|ится|ются|атся|ялся|лся|лась|лось|лись|ено|ена|ано|ана)$', re.I)

# ---------------------------------------------------------------- разбор

WORD_RE = re.compile(r'[А-Яа-яЁёA-Za-z0-9][А-Яа-яЁёA-Za-z0-9\-]*')
LINK_RE = re.compile(r'\[([^\]]*)\]\(([^)\s]+)[^)]*\)')
BARE_URL_RE = re.compile(r'(?<!\()https?://[^\s<>)\]]+')


def words(s):
    return WORD_RE.findall(s)


def split_sentences(text):
    t = text
    t = re.sub(r'\b(ст|стр|п|пп|ч|абз|рис|табл|см|др|тыс|млн|млрд|руб|гг|г|вв|в|им|проц)\.',
               '\\1\x01', t, flags=re.I)
    t = t.replace('т.е.', 'т\x01е\x01').replace('т.д.', 'т\x01д\x01')
    t = t.replace('т.п.', 'т\x01п\x01').replace('т. е.', 'т\x01 е\x01')
    t = re.sub(r'(\d)\.(\d)', '\\1\x01\\2', t)
    parts = re.split(r'(?<=[.!?…])[»"\'\)\]]*\s+', t)
    out = []
    for p in parts:
        p = p.replace('\x01', '.').strip()
        if p and words(p):
            out.append(p)
    return out


class Block:
    __slots__ = ('kind', 'text', 'num', 'h2', 'h3', 'level')

    def __init__(self, kind, text, num, h2, h3, level=0):
        self.kind = kind
        self.text = text
        self.num = num
        self.h2 = h2
        self.h3 = h3
        self.level = level

    def where(self):
        head = self.h3 or self.h2 or 'лид'
        if len(head) > 26:
            head = head[:25] + '…'
        return 'абз. %s (%s)' % (self.num, head)


def parse(raw):
    raw = raw.replace('\r\n', '\n').replace(' ', ' ')
    chunks = re.split(r'\n\s*\n', raw)
    blocks = []
    h2 = h3 = ''
    n = 0
    for ch in chunks:
        ch = ch.strip('\n')
        if not ch.strip():
            continue
        lines = [l for l in ch.split('\n') if l.strip()]
        first = lines[0].strip()
        m = re.match(r'^(#{1,6})\s*(.+?)\s*#*$', first)
        if m and len(lines) == 1:
            lvl = len(m.group(1))
            title = m.group(2).strip()
            if lvl == 1:
                h2, h3 = '', ''
            elif lvl == 2:
                h2, h3 = title, ''
            else:
                h3 = title
            blocks.append(Block('head', title, None, h2, h3, lvl))
            continue
        if first.startswith('|'):
            blocks.append(Block('table', ch, None, h2, h3))
            continue
        if re.match(r'^\s*(?:[-*+•]|\d+[.)])\s+', first):
            n += 1
            blocks.append(Block('list', ch, n, h2, h3))
            continue
        n += 1
        blocks.append(Block('prose', ' '.join(l.strip() for l in lines), n, h2, h3))
    return blocks


def clean(s):
    s = LINK_RE.sub(r'\1', s)
    s = re.sub(r'[*_`>]+', '', s)
    s = re.sub(r'^\s*(?:[-*+•]|\d+[.)])\s+', '', s, flags=re.M)
    return re.sub(r'\s+', ' ', s).strip()


def frag(s, n=52):
    s = clean(s)
    return s[:n] + ('…' if len(s) > n else '')


def short_url(u, n=48):
    u = re.sub(r'^https?://(?:www\.)?', '', u)
    u = re.sub(r'^' + re.escape(SITE_DOMAIN), '', u)
    return ('…' + u[-n:]) if len(u) > n else u


def plural(n, one, few, many):
    n = abs(n) % 100
    if 11 <= n <= 14:
        return many
    n %= 10
    if n == 1:
        return one
    if 2 <= n <= 4:
        return few
    return many


# ---------------------------------------------------------------- отчёт

class Report:
    def __init__(self):
        self.sections = []
        self.gate = []

    def add(self, title, lines):
        if lines:
            self.sections.append((title, lines))

    def fail(self, cond, text):
        self.gate.append(('ОТКАЗ' if cond else 'ок', text))

    def render(self, summary, quiet=False):
        out = ['СВОДКА'] + summary + ['']
        if not quiet:
            for title, lines in self.sections:
                out.append(title)
                out += ['  ' + l for l in lines]
                out.append('')
        out.append('ГЕЙТ ЭТАПА 6')
        for status, text in self.gate:
            mark = '✗' if status == 'ОТКАЗ' else '·'
            out.append('  %s %s' % (mark, text))
        bad = sum(1 for s, _ in self.gate if s == 'ОТКАЗ')
        out.append('')
        out.append('Критериев отказа сработало: %d' % bad)
        return '\n'.join(out)


# ---------------------------------------------------------------- проверки

def analyse(raw, full=False, gpu=False):
    blocks = parse(raw)
    rep = Report()

    prose = [b for b in blocks if b.kind == 'prose']
    lists = [b for b in blocks if b.kind == 'list']
    tables = [b for b in blocks if b.kind == 'table']
    heads = [b for b in blocks if b.kind == 'head']
    body = [b for b in blocks if b.kind in ('prose', 'list')]

    plain = clean(' '.join(b.text for b in body))
    chars = len(plain)
    chars_ns = len(plain.replace(' ', ''))
    nwords = len(words(plain))

    h2s = [b for b in heads if b.level <= 2]
    h3s = [b for b in heads if b.level >= 3]
    faq_q = [b.text for b in heads if '?' in b.text]

    # --- предложения
    sents = []          # (block, sentence, wordcount)
    for b in prose:
        for s in split_sentences(clean(b.text)):
            sents.append((b, s, len(words(s))))
    total_s = len(sents) or 1
    avg_len = sum(w for _, _, w in sents) / total_s
    sd_len = (sum((w - avg_len) ** 2 for _, _, w in sents) / total_s) ** 0.5

    long_s = [(b, s, w) for b, s, w in sents if w > LONG_SENTENCE]
    short_s = [(b, s, w) for b, s, w in sents if w < SHORT_SENTENCE]
    short_share = len(short_s) / total_s

    runs, cur = [], 0
    for _, _, w in sents:
        if w < SHORT_SENTENCE:
            cur += 1
        else:
            if cur > SHORT_RUN_MAX:
                runs.append(cur)
            cur = 0
    if cur > SHORT_RUN_MAX:
        runs.append(cur)

    # абзацы, начинающиеся с самого короткого своего предложения (антипаттерн №9)
    shortest_first = 0
    multi = 0
    sf_addrs = []
    for b in prose:
        ss = split_sentences(clean(b.text))
        if len(ss) < 2:
            continue
        multi += 1
        lens = [len(words(x)) for x in ss]
        if lens[0] == min(lens):
            shortest_first += 1
            sf_addrs.append(b.where())
    sf_share = shortest_first / multi if multi else 0

    # --- структура
    summary = [
        '  Объём: %d зн. с пробелами, %d без пробелов, %d слов%s' % (
            chars, chars_ns, nwords,
            '' if VOLUME_MIN <= chars <= VOLUME_MAX
            else '  ← вне нормы %d–%d' % (VOLUME_MIN, VOLUME_MAX)),
        '  Структура: H2 %d, H3 %d, абзацев %d, списков %d, таблиц %d, FAQ %d' % (
            len(h2s), len(h3s), len(prose), len(lists), len(tables), len(faq_q)),
        '  Подзаголовок каждые %d зн.%s' % (
            chars // max(1, len(h2s) + len(h3s)),
            '' if chars // max(1, len(h2s) + len(h3s)) <= SUBHEAD_EVERY_MAX else '  ← реже нормы'),
        '  Средняя длина предложения: %.1f слова (предложений %d)' % (avg_len, total_s),
        '  Разброс длин: %.1f%s' % (
            sd_len, '' if sd_len >= RHYTHM_SD_MIN else '  ← ритм однородный, текст читается ровно'),
        '  Длинных >%d слов: %d   коротких <%d слов: %d (%.0f%%)' % (
            LONG_SENTENCE, len(long_s), SHORT_SENTENCE, len(short_s), short_share * 100),
    ]

    # объём разделов, диспропорция
    sec = defaultdict(int)
    order = []
    for b in body:
        key = b.h2 or '(лид)'
        if key not in sec:
            order.append(key)
        sec[key] += len(clean(b.text))
    if len(order) > 2:
        vals = [(k, sec[k]) for k in order]
        mx = max(v for _, v in vals)
        mn = min(v for _, v in vals)
        if mx > mn * 4:
            rep.add('ДИСПРОПОРЦИЯ РАЗДЕЛОВ (max/min = %.1f)' % (mx / max(1, mn)),
                    ['%5d зн.  %s' % (v, k[:44]) for k, v in vals])

    # --- длинные и короткие
    rep.add('ПРЕДЛОЖЕНИЯ СВЫШЕ %d СЛОВ' % LONG_SENTENCE,
            ['%s  %d сл.  %s' % (b.where(), w, frag(s)) for b, s, w in long_s])
    if short_share > SHORT_SHARE_MAX or runs:
        lines = ['доля коротких %.0f%% (норма до %.0f%%)' % (short_share * 100, SHORT_SHARE_MAX * 100)]
        if runs:
            lines.append('серии подряд: %s' % ', '.join('%d' % r for r in runs))
        rep.add('РУБЛЕНЫЙ ТЕКСТ', lines)

    # --- одиночный обрубок в конце абзаца (антипаттерн №1, позиция)
    tail_stub = []
    for b in prose:
        ss = split_sentences(clean(b.text))
        if len(ss) >= 2:
            last = ss[-1]
            last_w = len(words(last))
            if last_w < SHORT_SENTENCE and ',' not in last and not last.endswith(':'):
                tail_stub.append('%s  %s' % (b.where(), frag(last, 40)))
    rep.add('ОДИНОЧНЫЙ ОБРУБОК В КОНЦЕ АБЗАЦА (антипаттерн №1, кандидаты, проверить глазами)', tail_stub[:14])

    # --- шаблон «короткий зачин + длинное пояснение» (антипаттерн №9), адреса
    if sf_share > 1 / 3:
        rep.add('ШАБЛОН «КОРОТКИЙ ЗАЧИН + ДЛИННОЕ ПОЯСНЕНИЕ» (антипаттерн №9), адреса',
                sf_addrs[:16])

    # --- назывные предложения
    nominal = []
    for b, s, w in sents:
        if w <= 5 and not any(VERB_HINT.search(t) for t in words(s)):
            nominal.append('%s  %s' % (b.where(), frag(s, 40)))
    rep.add('НАЗЫВНЫЕ ПРЕДЛОЖЕНИЯ (кандидаты, проверить глазами)', nominal[:12])

    # --- зачины с «И»
    and_start = ['%s  %s' % (b.where(), frag(s, 40))
                 for b, s, _ in sents if re.match(r'^И\s+[а-яё]', s)]
    rep.add('ЗАЧИН С «И»', and_start)

    # --- безличные зачины (антипаттерн №5)
    impers = []
    for b, s, w in sents:
        for pattern, note in IMPERSONAL_OPENINGS:
            if re.search(pattern, s, re.I):
                impers.append('%s  %s  ← %s' % (b.where(), frag(s, 40), note))
    rep.add('БЕЗЛИЧНЫЕ ЗАЧИНЫ (антипаттерн №5)', impers)

    # --- скрытый список: нумерация словами в прозе (антипаттерн №6)
    school = []
    for b in prose:
        for m in SCHOOL_NUMBERING.finditer(clean(b.text)):
            school.append('%s  %s' % (b.where(), frag(m.group(0), 30)))
    rep.add('СКРЫТЫЙ СПИСОК: НУМЕРАЦИЯ СЛОВАМИ В ПРОЗЕ (антипаттерн №6, кандидаты — оформить списком, если это перечисление)', school)

    # --- разрывные конструкции
    breaks, commas, brackets = [], [], []
    for b, s, w in sents:
        dashes = len(re.findall(r'\s[—–]\s', s))
        definition = bool(re.match(r'^[^—–]{2,70}\s[—–]\s(?:это|то\s+есть)\b', s))
        if definition and dashes == 1:
            pass
        elif dashes >= 2:
            breaks.append('%s  %d тире  %s' % (b.where(), dashes, frag(s)))
        elif dashes == 1 and re.search(r'^[^—–]{10,70}\s[—–]\s[^—–,]{5,}[,.]', s):
            breaks.append('%s  вставка  %s' % (b.where(), frag(s)))
        if re.search(r'\w\s*,\s+это\s+', s):
            commas.append('%s  %s' % (b.where(), frag(s)))
        for m in re.finditer(r'\(([^)]{25,})\)', s):
            if len(words(m.group(1))) >= 4:
                brackets.append('%s  (%s)' % (b.where(), frag(m.group(1), 34)))
    rep.add('ДВОЙНОЕ ТИРЕ И ВСТАВКИ', breaks)
    rep.add('ТИРЕ ЗАМЕНЕНО ЗАПЯТОЙ («X , это Y»)', commas)
    rep.add('СКОБОЧНЫЕ ВСТАВКИ', brackets[:10])

    # --- причастная калька (антипаттерн №11)
    participle = []
    for b, s, w in sents:
        if PARTICIPLE_CALQUE.search(s):
            participle.append('%s  %s' % (b.where(), frag(s, 44)))
    rep.add('ПРИЧАСТНАЯ КАЛЬКА (антипаттерн №11, кандидаты — только «описывает/заявляет X как Y-ющий»)',
            participle[:14])

    # --- хеджи
    hedges, direct = [], 0
    for b in body:
        t = clean(b.text)
        for m in re.finditer(r'\bсто(?:ит|ило)\b((?:\s+\S+){0,3})', t, re.I):
            tail = m.group(1)
            if re.search(r'\b\w+(?:ть|ти|чь)\b', tail):
                hedges.append('%s  стоит %s' % (b.where(), frag(tail, 30)))
            else:
                direct += 1
        for m in re.finditer(r'\bследует\b((?:\s+\S+){0,3})', t, re.I):
            if re.search(r'\b\w+(?:ть|ти|чь)\b', m.group(1)):
                hedges.append('%s  следует %s' % (b.where(), frag(m.group(1), 30)))
    rep.add('ХЕДЖИ «стоит / следует» + инфинитив%s' % (
        '  (прямых значений «стоит»: %d)' % direct if direct else ''), hedges)

    # --- связки
    conn_hits = defaultdict(list)
    for b in body:
        low = clean(b.text).lower()
        for c in CONNECTIVES:
            for _ in re.finditer(r'\b' + re.escape(c) + r'\b', low):
                conn_hits[c].append(b.num)
    lines = []
    for c, nums in sorted(conn_hits.items(), key=lambda x: -len(x[1])):
        adjacent = any(b - a == 1 for a, b in zip(sorted(set(nums)), sorted(set(nums))[1:]))
        lines.append('%-20s %2d  абз. %s%s' % (
            c, len(nums), ', '.join(str(n) for n in nums[:12]),
            '   ← в соседних абзацах' if adjacent else ''))
    rep.add('СВЯЗКИ', lines)

    # --- «не X, а Y»
    nea = ['%s  %s' % (b.where(), frag(m.group(0), 44))
           for b in body
           for m in re.finditer(r'\bне\s+[\wё-]+,\s+а\s+[\wё-]+', clean(b.text), re.I)]
    rep.add('КОНСТРУКЦИЯ «не X, а Y»', nea)

    # --- однотипность зачинов
    openings = defaultdict(list)
    for b in prose:
        ws = words(clean(b.text))
        if len(ws) >= 2:
            openings[' '.join(w.lower() for w in ws[:2])].append(b.num)
    lines = ['«%s»  %d раз  абз. %s' % (k, len(v), ', '.join(map(str, v)))
             for k, v in openings.items() if len(v) >= 3]
    rep.add('ОДНОТИПНЫЕ ЗАЧИНЫ АБЗАЦЕВ', lines)

    # --- однотипные концовки разделов (антипаттерн №12)
    last_prose_by_h2 = {}
    for b in prose:
        key = b.h2 or '(лид)'
        last_prose_by_h2[key] = b   # перезаписывается, остаётся последний абзац раздела
    closing_hits = defaultdict(list)
    for key, b in last_prose_by_h2.items():
        ss = split_sentences(clean(b.text))
        if not ss:
            continue
        last = ss[-1].lower()
        for marker in CLOSING_MARKERS:
            if marker in last:
                closing_hits[marker].append((key, b.where(), frag(ss[-1], 40)))
    lines = []
    for marker, items in closing_hits.items():
        if len(items) >= 2:
            for key, where, fr in items:
                lines.append('«%s»  %s: %s  %s' % (marker, key[:24], where, fr))
    rep.add('ОДНОТИПНЫЕ КОНЦОВКИ РАЗДЕЛОВ (антипаттерн №12, кандидаты)', lines[:14])

    # --- подзаголовки: рубрикаторы и дубли
    pat = defaultdict(list)
    for b in heads:
        m = re.match(r'^\s*(?:\d+[.)]\s*)?(Что|Какие|Какая|Чем|Почему|Как|Где|Кому|Зачем|Нужн\w+)\b',
                     b.text, re.I)
        if m:
            pat[m.group(1).lower()].append(b.text[:34])
    lines = ['«%s…»  %d шт.: %s' % (k, len(v), ' | '.join(v[:4]))
             for k, v in pat.items() if len(v) >= 3]
    titles = [b.text.lower().strip() for b in heads]
    dup = [t for t, c in Counter(titles).items() if c > 1]
    for t in dup:
        lines.append('дубль заголовка: «%s» × %d' % (t[:44], titles.count(t)))
    for i, a in enumerate(heads):
        for b2 in heads[i + 1:]:
            sa, sb = set(words(a.text.lower())), set(words(b2.text.lower()))
            if len(sa) >= 3 and len(sa & sb) / max(1, len(sa | sb)) >= 0.6 and a.text != b2.text:
                lines.append('почти дубль: «%s» / «%s»' % (a.text[:32], b2.text[:32]))
    rep.add('ПОДЗАГОЛОВКИ: РУБРИКАТОРЫ И ДУБЛИ', lines[:14])

    # --- оверклеймы, снисходительность, ремарки
    def scan(terms, label):
        hits = []
        for b in body:
            low = clean(b.text).lower()
            for t in terms:
                for m in re.finditer(re.escape(t), low):
                    s, e = max(0, m.start() - 24), m.end() + 24
                    hits.append('%s  …%s…' % (b.where(), low[s:e]))
        rep.add(label, hits[:14])

    scan(ABSOLUTES, 'АБСОЛЮТНЫЕ ОБЕЩАНИЯ')
    scan(CONDESCENDING, 'СНИСХОДИТЕЛЬНАЯ РАМКА')
    scan(EDITOR_REMARKS, 'РЕДАКТОРСКИЕ РЕМАРКИ')

    # --- SEO-жаргон (антипаттерн №4)
    seo = []
    for b in body:
        low = clean(b.text).lower()
        for patt in SEO_JARGON:
            for m in re.finditer(patt, low, re.I):
                seo.append('%s  …%s…' % (b.where(), low[max(0, m.start() - 16):m.end() + 16]))
    rep.add('SEO-ЖАРГОН (антипаттерн №4, только в отчётах, не в статьях; «ключ» не автоматизирован — проверить глазами)', seo[:14])

    # --- грамматические автозамены
    gram = []
    for patt, fix in GRAMMAR_FIXES:
        for m in re.finditer(patt, raw, re.I):
            gram.append('«%s» → «%s»' % (m.group(0), fix))
    rep.add('ГРАММАТИКА', gram)

    # --- канон (включая отклонённые цифры из индекса)
    canon = []
    whole = clean(raw)
    traps = CANON_TRAPS + REJECTED_TRAPS + (GPU_TRAPS if gpu else [])
    for pattern, note in traps:
        for m in re.finditer(pattern, whole, re.I):
            canon.append('%s  ← %s' % (frag(m.group(0), 40), note))
    counts = ['%s  %s' % (b.where(), frag(m.group(0), 44))
              for b in body for m in re.finditer(MODEL_COUNT, clean(b.text), re.I)]
    if counts:
        canon.append('счётчик моделей: %d %s' % (
            len(counts), plural(len(counts), 'упоминание', 'упоминания', 'упоминаний')))
        canon += ['   ' + c for c in counts]
    rep.add('КАНОН', canon)

    # --- ссылки
    links = []
    for b in blocks:
        for m in LINK_RE.finditer(b.text):
            links.append((b, m.group(1).strip(), m.group(2).strip()))
    bare = [(b, m.group(0)) for b in blocks for m in BARE_URL_RE.finditer(b.text)]
    internal = [(b, a, u) for b, a, u in links if SITE_DOMAIN in u or u.startswith('/')]
    external = [(b, a, u) for b, a, u in links if not (SITE_DOMAIN in u or u.startswith('/'))]
    lines = ['всего %d, внутренних %d, внешних %d, голых URL %d' % (
        len(links), len(internal), len(external), len(bare))]
    url_count = Counter(u for _, _, u in internal)
    for u, c in url_count.most_common():
        if c > 1:
            lines.append('повтор адреса ×%d: %s' % (c, short_url(u)))
    for b, a, u in links:
        if not a:
            lines.append('пустой анкор → %s' % short_url(u))
        elif len(words(a)) == 1:
            lines.append('анкор в одно слово «%s» → %s' % (a, short_url(u, 38)))
        if re.search(r'[.,;:]\s*$', a):
            lines.append('анкор захватил знак: «%s»' % a[-34:])
        if re.search(RU_LOCALES_BAD, u):
            lines.append('чужая локаль: %s' % short_url(u))
    if not external:
        lines.append('внешних источников нет ни одного')
    rep.add('ССЫЛКИ', lines[:22])

    # --- цифры без ссылки в абзаце
    num_re = re.compile(r'\d+[,.]?\d*\s*(?:%|процент|млн|млрд|тыс|раз[а]?\b)')
    unsourced = []
    for b in body:
        if num_re.search(b.text) and not LINK_RE.search(b.text) and not BARE_URL_RE.search(b.text):
            found = ', '.join(sorted({m.group(0).strip() for m in num_re.finditer(b.text)})[:5])
            unsourced.append('%s  %s' % (b.where(), found))
    rep.add('ЦИФРЫ БЕЗ ССЫЛКИ В АБЗАЦЕ (проверить атрибуцию)', unsourced[:18])

    # --- остатки черновика
    junk = []
    for pattern, note in DRAFT_JUNK:
        hits = list(re.finditer(pattern, raw))
        if hits:
            junk.append('%s: %d → %s' % (note, len(hits),
                                         ' | '.join(repr(h.group(0))[:18] for h in hits[:4])))
    for a, b2 in YO_PAIRS:
        ra = len(re.findall(r'\b%s\b' % a, plain, re.I))
        rb = len(re.findall(r'\b%s\b' % b2, plain, re.I))
        if ra and rb:
            junk.append('е/ё вперемешку: «%s» ×%d и «%s» ×%d' % (a, ra, b2, rb))
    rep.add('ОСТАТКИ ЧЕРНОВИКА И ТЕХНИКА', junk)

    # --- тяжёлые предложения: несколько знаков-разделителей в одном
    heavy = []
    for b, sent, w in sents:
        commas = sent.count(',')
        colons = sent.count(':') + sent.count(';')
        dashes = len(re.findall(r'\s[—–]\s', sent))
        if w >= 14 and commas >= 2 and (colons + dashes) >= 2:
            heavy.append('%s  %d зн. разделителей  %s' % (
                b.where(), commas + colons + dashes, frag(sent)))
        elif w >= 18 and commas >= 3 and (colons + dashes) >= 1:
            heavy.append('%s  %d зн. разделителей  %s' % (
                b.where(), commas + colons + dashes, frag(sent)))
    rep.add('ТЯЖЁЛЫЕ ПРЕДЛОЖЕНИЯ (запятые плюс двоеточие или тире)', heavy[:14])

    # --- кальки с английского
    calq = []
    for b in body:
        low = clean(b.text).lower()
        for t in CALQUES:
            for m in re.finditer(re.escape(t), low):
                calq.append('%s  …%s…' % (b.where(), low[max(0, m.start() - 16):m.end() + 16]))
    rep.add('КАЛЬКИ С АНГЛИЙСКОГО', calq[:14])

    # --- категоричные зачины до доказательства
    categ = []
    for b in prose:
        first = split_sentences(clean(b.text))
        if not first:
            continue
        low = first[0].lower()
        for t in CATEGORICAL:
            if t in low:
                categ.append('%s  %s' % (b.where(), frag(first[0], 46)))
                break
    rep.add('КАТЕГОРИЧНЫЙ ЗАЧИН ДО ДОКАЗАТЕЛЬСТВА', categ[:10])

    # --- цепочки однопредложенческих абзацев
    runs_single, cur_run, start = [], 0, None
    for b in prose:
        if len(split_sentences(clean(b.text))) == 1:
            if cur_run == 0:
                start = b.num
            cur_run += 1
        else:
            if cur_run >= 3:
                runs_single.append((start, cur_run))
            cur_run = 0
    if cur_run >= 3:
        runs_single.append((start, cur_run))
    rep.add('ЦЕПОЧКИ ОДНОПРЕДЛОЖЕНЧЕСКИХ АБЗАЦЕВ (скрытые перечисления)',
            ['с абз. %s подряд %d абзацев по одному предложению' % (a, n) for a, n in runs_single])

    # --- вода и канцелярит
    water = []
    for b in body:
        low = clean(b.text).lower()
        for t in WATER:
            for m in re.finditer(re.escape(t), low):
                water.append('%s  …%s…' % (b.where(), low[max(0, m.start() - 18):m.end() + 18]))
    wdens = len(water) / max(1, nwords) * 1000
    if water:
        rep.add('ВОДА И КАНЦЕЛЯРИТ (%.0f на 1000 слов, норма до %d)' % (wdens, WATER_PER_1000_MAX),
                water[:16])

    # --- лид против заголовка
    h1 = next((b.text for b in heads if b.level == 1), '')
    lead = prose[0].text if prose else ''
    overlap = 0.0
    if h1 and lead:
        hw = {w.lower() for w in words(h1) if len(w) > 3 and w.lower() not in STOPWORDS}
        lw = {w.lower() for w in words(clean(lead))}
        if hw:
            overlap = len(hw & lw) / len(hw)
            if overlap < LEAD_H1_OVERLAP_MIN:
                rep.add('ЛИД НЕ ОТВЕЧАЕТ ЗАГОЛОВКУ (%.0f%% значимых слов H1 в первом абзаце, норма %.0f%%)' % (
                    overlap * 100, LEAD_H1_OVERLAP_MIN * 100),
                    ['нет в лиде: ' + ', '.join(sorted(hw - lw)[:10])])

    # --- повторяющиеся фразы
    toks = [w.lower() for w in words(plain)]
    sh = Counter()
    for i in range(len(toks) - 2):
        tri = toks[i:i + 3]
        if all(t in STOPWORDS or len(t) < 3 for t in tri):
            continue
        sh[' '.join(tri)] += 1
    lines = ['«%s» × %d' % (k, c) for k, c in sh.most_common(30) if c >= 3][:10]
    rep.add('ПОВТОРЯЮЩИЕСЯ ФРАЗЫ (3 слова, 3+ раза)', lines)

    # --- отглагольные существительные
    vn = Counter(w.lower() for w in words(plain)
                 if re.search(r'(?:ание|ения|ение|аций|ация|ирование|ированию|ённость|енность)$', w, re.I))
    dens = sum(vn.values()) / max(1, nwords) * 1000
    if vn:
        rep.add('ОТГЛАГОЛЬНЫЕ СУЩЕСТВИТЕЛЬНЫЕ (%.0f на 1000 слов)' % dens,
                [', '.join('%s ×%d' % (k, c) for k, c in vn.most_common(12))])

    # --- латиница рядом с русским
    lat = Counter(w for w in words(plain) if re.match(r'^[A-Za-z][A-Za-z\-]{1,}$', w))
    if lat:
        rep.add('ЛАТИНИЦА (проверить пару «русский + английский»)',
                [', '.join('%s ×%d' % (k, c) for k, c in lat.most_common(18))])

    # --- гейт
    rep.fail(short_share > SHORT_SHARE_MAX,
             'доля предложений короче %d слов: %.0f%% (порог %.0f%%)' % (
                 SHORT_SENTENCE, short_share * 100, SHORT_SHARE_MAX * 100))
    rep.fail(bool(runs), 'серии из 3+ коротких предложений подряд: %d' % len(runs))
    rep.fail(sf_share > 1 / 3,
             'абзацев, начинающихся с самого короткого предложения: %.0f%% (порог 33%%)' % (sf_share * 100))
    rep.fail(bool(breaks), 'разрывные конструкции с тире: %d' % len(breaks))
    rep.fail(len(and_start) > 1, 'предложений с зачином «И»: %d (норма не более 1)' % len(and_start))
    rep.fail(any(len(v) >= 3 for v in pat.values()),
             'однотипные подзаголовки-рубрикаторы: %s' % (
                 ', '.join('%s×%d' % (k, len(v)) for k, v in pat.items() if len(v) >= 3) or 'нет'))
    rep.fail(not (VOLUME_MIN <= chars <= VOLUME_MAX),
             'объём %d зн. вне нормы %d–%d (превышение допустимо осознанно)' % (
                 chars, VOLUME_MIN, VOLUME_MAX))
    rep.fail(not external, 'внешних источников: %d' % len(external))
    rep.fail(sd_len < RHYTHM_SD_MIN,
             'разброс длин предложений: %.1f (порог %.1f, ниже — однородный ритм)' % (sd_len, RHYTHM_SD_MIN))
    rep.fail(wdens > WATER_PER_1000_MAX,
             'вода и канцелярит: %.0f на 1000 слов (порог %d)' % (wdens, WATER_PER_1000_MAX))

    return rep, summary


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    flags = {a for a in sys.argv[1:] if a.startswith('--')}
    if not args:
        print(__doc__)
        sys.exit(1)
    with open(args[0], encoding='utf-8') as f:
        raw = f.read()
    rep, summary = analyse(raw, full='--full' in flags, gpu='--gpu' in flags)
    print(rep.render(summary, quiet='--quiet' in flags))


if __name__ == '__main__':
    main()
