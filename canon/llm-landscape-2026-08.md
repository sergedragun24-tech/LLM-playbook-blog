# Канон: ландшафт LLM на август 2026 — версии, цены, лицензии, бенчмарки

Собрано 17.08.2026 при проверке статьи по теме. Дополнено в тот же день данными по Kimi (Moonshot AI) и по мультимодальности всех семейств.

## Актуальные линейки

| Вендор | Актуально на 17.08.2026 | Что устарело |
|---|---|---|
| OpenAI | GPT-5.6 Sol (флагман), GPT-5.6 Terra, GPT-5.6 Luna. Релиз 09.07.2026 | — |
| Anthropic | Claude Opus 5 (24.07.2026), Claude Sonnet 5, Claude Fable 5 (GA 09.06.2026), Claude Haiku 4.5 | — |
| Google | Gemini 3.7 Flash, 3.6 Flash, 3.5 Flash, 2.5 Pro; Gemini 3.1 Pro в превью | — |
| DeepSeek | DeepSeek-V4-Pro (13.08.2026, 1,7T), DeepSeek-V4-Flash (304B). Лицензия **MIT**, контекст 1M | — |
| Alibaba | Qwen3.8-2.4T-A95B (флагман), Qwen3.8-27B; отдельно Qwen3-VL и qwen3.5-ocr | — |
| Moonshot AI | **Kimi K3** (релиз 16.07.2026, веса 27.07), Kimi K2.7-Code (12.06.2026) | K2.5 и moonshot-v1 сворачиваются **31.08.2026**, новым пользователям недоступны |
| Meta | **Muse Glimmer** (~10.08.2026, 30B, **Apache 2.0**), Muse Spark (04.2026) | **Llama заморожена на версии 4.** Последние обновления репозиториев meta-llama — май 2025 |
| Яндекс | **Alice AI**: Alice AI LLM, LLM Flash, VLM, ART | **«YandexGPT» — устаревшее название.** YandexGPT 5.1 Pro/Lite — предыдущее поколение |
| Сбер | GigaChat 3 Ultra (релиз 15.07.2026); линейка GigaChat 2 (30.1, 28.2) Lite/Pro/Max | — |

Источники: [developers.openai.com/api/docs/models](https://developers.openai.com/api/docs/models) · [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview) · [ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models) · [api-docs.deepseek.com/news/news260813](https://api-docs.deepseek.com/news/news260813/) · [huggingface.co/Qwen/Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) · [platform.kimi.ai/docs/models](https://platform.kimi.ai/docs/models) · [research.meta.ai](https://research.meta.ai/blog/introducing-muse-glimmer-open-agentic-model) · [ya.ru/ai/aliceai](https://ya.ru/ai/aliceai/) · [developers.sber.ru/docs/ru/gigachat/models/updates](https://developers.sber.ru/docs/ru/gigachat/models/updates)

## Цены за 1М токенов (официальные прайсы)

| Модель | Input | Output |
|---|---|---|
| Claude Opus 5 | $5,00 | $25,00 |
| GPT-5.6 Sol | $2,50 | $15,00 |
| Kimi K3 | $3,00 (cache hit $0,30) | $15,00 |
| GPT-5.6 Terra | $1,00 | $6,00 |
| Kimi K2.7-Code | $0,95 | $4,00 |
| DeepSeek V4 Pro | $0,435 | $0,87 |
| DeepSeek V4 Flash | $0,14 | $0,28 |
| GPT-5.6 Luna | $0,10 | $0,60 |

**«DeepSeek дешевле на порядок» — писать нельзя без уточнения.** Против Claude Opus 5 — 11,5× по input и 28,7× по output. Против GPT-5.6 Sol по input — только 5,7×. Корректно: «в 6–29 раз, в зависимости от того, с чем сравнивать и какие токены считать».

**«Китайская открытая модель = дешёвая» — тоже неверно.** Kimi K3 стоит $3/$15, вровень с GPT-5.6 Sol. Дешёвый вариант внутри семейства — K2.7-Code.

**Разрыв внутри одной линейки OpenAI — 25×** (Sol vs Luna). Утверждения вида «GPT дорог для массовых задач» на уровне семейства фактически неверны: решение принимается на уровне версии. Это ловушка любой обзорной статьи, проговаривать её в тексте явно.

DeepSeek с 16.08.2026 ввёл off-peak тарифы в половину базовых (пик — 01:00–04:00 и 06:00–10:00 UTC).

## Лицензии: где «открытая модель» — неточность

- **DeepSeek V4 — MIT**, полностью открытая. Единственная из перечисленных без оговорок.
- **Muse Glimmer — Apache 2.0**, без ограничения по MAU.
- **Qwen открыт не весь.** Qwen3.8-27B и Qwen3-VL — Apache 2.0, флагман Qwen3.8-2.4T-A95B — собственная лицензия `qwen3.8-max`.
- **Kimi K3 — собственная «Kimi K3 License»** с порогами: отдельное соглашение с Moonshot при выручке MaaS-бизнеса свыше **$20 млн** за 12 месяцев; обязательное указание «Kimi K3» при более **100 млн MAU** или $20 млн выручки в месяц. Для внутреннего корпоративного использования пороги не срабатывают. K2.7-Code — Modified MIT. Писать «MIT» или «Apache» про K3 нельзя.
- **Llama Community License — не open source** по позиции OSI. Порог **700 млн MAU**. ([opensource.org](https://opensource.org/blog/metas-llama-license-is-still-not-open-source))

## Экосистема открытых моделей: Meta проиграла Qwen

- ATOM Report: доля Qwen в новых дообученных версиях выросла с 1% (январь 2024) до **69%** (февраль 2026); у Meta пик 44% (август 2024) → **11%**. ([arxiv.org/html/2604.07190](https://arxiv.org/html/2604.07190))
- State of Open Models (HF, лето 2026): у Qwen **151 448 производных**, в 2,6× больше всего футпринта Meta (~58 000). ([huggingface.co/blog/state-of-open-models-summer-2026](https://huggingface.co/blog/state-of-open-models-summer-2026))

**Тезис «экосистема Llama — самая развитая среди открытых моделей» устарел, во всех статьях помечать как ошибку.**

## Контекстное окно: 1M — это норма, а не отличие

На 1M токенов: Claude Fable 5, Claude Opus 4.8, GPT-5.5, DeepSeek V4 Pro и Flash, Qwen3.8 (1 010 000), Gemini 3.1 Pro, Kimi K3. Максимум на рынке — **Llama 4 Scout, 10M**.

**Формулировку «одно из самых больших окон на рынке» про Gemini не использовать.** Сильная сторона Gemini — нативная мультимодальность: «These models can natively understand text, video, audio, and images». ([ai.google.dev](https://ai.google.dev/gemini-api/docs/long-context))

Работающее окно ≠ заявленное окно — см. канон по галлюцинациям (деградация 13,9–85%).

## Кто реально закрывает сценарий «скан договора → структурированный текст»

Проверено по документации 17.08.2026. Порядок — от сильного к слабому.

| Семейство | Вердикт |
|---|---|
| **Qwen (Alibaba)** | **Да, единственное полноценное решение.** Отдельная линейка qwen3.5-ocr / qwen-vl-ocr: «extracts text and structured data from images — scanned documents, tables, receipts». Принимает **PDF напрямую** (до 50 стр., 100 МБ). Встроенный document parsing: заголовки, таблицы, LaTeX. Русский показан примерами. Открытые веса Qwen3-VL под Apache 2.0, OCR на 32 языках ([github.com/QwenLM/Qwen3-VL](https://github.com/qwenlm/qwen3-vl), [help.aliyun.com](https://help.aliyun.com/en/model-studio/qwen-vl-ocr)) |
| **GigaChat (Сбер)** | Да, с оговоркой. Дословно: «Модели GigaChat умеют распознавать текстовые документы, изображения и аудио». Форматы: txt, doc, docx, **pdf**, epub, ppt, pptx, xlsx; изображение до 15 Мб, одно на сообщение. Отдельного OCR-режима нет, качество на сканах документацией не заявлено ([developers.sber.ru](https://developers.sber.ru/docs/ru/gigachat/guides/working-with-files)) |
| **Alice AI (Яндекс)** | Частично. Чат принимает DOC, DOCX, PDF, TXT до 100 МБ и изображение до 20 МБ, но распознавание сканов вынесено в **отдельный сервис Yandex Vision OCR** (модели page, table, handwritten, math-markdown; паспорта, ВУ, СТС). Писать «Alice AI распознаёт сканы договоров» — оверклейм ([aistudio.yandex.ru](https://aistudio.yandex.ru/docs/ru/vision/concepts/ocr/)) |
| **Kimi (Moonshot AI)** | Нет. Принимает изображения (jpeg, png, gif, webp, bmp, heic; только base64 или file ID, URL не поддерживается). **PDF, OCR и парсинг документов в документации не упоминаются вообще.** Максимум допустимой формулировки — «принимает изображения на вход» ([platform.kimi.ai](https://platform.kimi.ai/docs/guide/use-kimi-vision-model)) |
| **DeepSeek** | Нет через API. V4-Pro и V4-Flash не мультимодальны. Есть отдельная открытая **DeepSeek-OCR-2** (~3B, Apache 2.0, olmOCR-bench 76,3%), но это самостоятельный компонент пайплайна, русский явно не заявлен |

## Бенчмарки: чем можно и чем нельзя аргументировать

**SWE-bench Verified — ретирован, не использовать.** OpenAI официально отказалась 23.02.2026: «59.4% of the 138 problems contained material issues in test design and/or problem description». Замена — SWE-bench Pro. ([openai.com](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/))

**Код — Terminal-Bench 2.1**, официальный лидерборд: 1-е место Claude Code + Fable 5 — **83,8% ± 1,2%**; Codex + GPT-5.6 Terra — 78,4%. ([tbench.ai](https://www.tbench.ai/leaderboard/terminal-bench/2.1))

**Осторожно с самозамерами.** OpenAI приводит «GPT-5.6 Sol 88,8%» на Terminal-Bench, Moonshot — «Kimi K3 88,3%». Обеих строк на независимых лидербордах нет. Давать только с пометкой «по данным разработчика» либо не давать.

**Агентная работа — AA-Briefcase (Artificial Analysis):** Claude Fable 5 — Elo 1574, **Kimi K3 — 1543 (2-е место)**, GPT-5.6 Sol — 1501, Opus 4.8 — 1347. AutomationBench-AA: Kimi K3 — 53%, 1-е место. ([artificialanalysis.ai](https://artificialanalysis.ai/articles/kimi-k3-agentic-knowledge-benchmark))

**Контрапункт к дешевизне Kimi:** 39,5 токенов/с, TTFT 3,28 с, 54-е место по скорости; на AA-Briefcase — $10,57 и 56,4 минуты на задачу, примерно в 2,5× дольше Claude Fable 5. Формула для статей: **низкая цена за токен ≠ дешёвая задача.**

**Фронтенд-код — WebDev Arena:** Claude Opus 5 Max — 1692, **Kimi K3 — 1674 (2-е место)**, Qwen 3.8 Max — 1667.

**Следование инструкции и формату — IFBench.** Топ: Grok 4.3 (83,3%), Grok 4.20 (82,9%), MiniMax-M3 (82,9%). **Claude в топ-3 нет** — претензию на лидерство Claude по формату вывода снимать.

**Общий уровень — Artificial Analysis Intelligence Index:** Claude Opus 5 — 63, Fable 5 — 62, GPT-5.6 Sol — 61, Kimi K3 — 60 (на релизе 57), Qwen3.8 — 58.

**Математика — MathArena:** Claude-Opus-5 max 84,4% · GPT-5.6-Sol max 79,7% · GPT-5.5 xhigh 77,8% · **Kimi K3 Think 69,7% — лучшая открытая модель**.

**GPQA Diamond:** GPT-5.6 Sol 94,1 · Qwen3.8-2.4T-A95B 92,6 · Fable 5 92,6 · Opus 4.8 92,0. Превосходства Qwen на STEM нет, есть паритет.

**Галлюцинации Kimi выросли:** на AA-Omniscience точность K3 поднялась с 33% до 46%, но уровень галлюцинаций — с 39% до 51%. Против позиционирования Kimi как модели для работы с фактурой без проверки.

## Русский язык: MERA опровергает тезис о превосходстве российских моделей

Лидерборд MERA на 17.08.2026 (632 сабмита):

| Место | Модель | Score |
|---|---|---|
| 1 | **Claude-Opus-4.6** | 0,862 |
| 2 | Human Benchmark | 0,852 |
| 3 | BerryLM-XL (Wildberries) | 0,835 |
| 4 | Cotype Pro 3 (MWS AI) | 0,824 |
| 6 | GPT-5.4 | 0,821 |
| 23 | GigaChat-3.1-Ultra | 0,712 |
| 40 | GigaChat 2 Max | 0,670 |
| 42 | T-pro-it-2.0 (Т-Банк) | 0,660 |

ruMMLU, профильные поддомены:

| Модель | jurisprudence | professional_law | professional_accounting |
|---|---|---|---|
| Claude-Opus-4.6 | 0,917 | 0,845 | **0,968** |
| GPT-5.4 | 0,917 | 0,856 | 0,961 |
| GigaChat-3.1-Ultra | 0,843 | 0,632 | **0,649** |

**Тезис «российские модели точнее работают с русской юридической и бухгалтерской терминологией» — снимать во всех статьях.**

**Корректный аргумент за российские модели — доступность и комплаенс**: данные в РФ, 152-ФЗ, отсутствие риска отключения. Не качество русского.

Оговорки: ruMMLU переводной, право и бухучёт там американские — прямого замера на российском праве и РСБУ нет. Alice AI в лидерборде MERA **отсутствует**, публичных сопоставимых замеров по Яндексу нет.

**Alice AI LLM инициализирована весами Qwen3-235B** (техрепорт Яндекса). Аргумент «российская модель = российская языковая база» на этом ломается.

## Доступ из России

Официального запрета по стране в условиях Moonshot нет: ToS запрещают доступ из «any country or region subject to comprehensive sanctions», Россия поимённо не названа. Прямая оплата и стабильный доступ к API из РФ при этом не гарантированы — на практике подключаются через шлюзы-посредники либо разворачивают открытые веса у себя. **Утверждение «Kimi официально заблокирован в России» — неверно, подтверждения нет.**

## Строки для индекса

OpenAI: GPT-5.6 Sol/Terra/Luna, релиз 09.07.2026 → developers.openai.com
Anthropic: Claude Opus 5 (24.07.2026), Sonnet 5, Fable 5 (GA 09.06.2026), Haiku 4.5 → platform.claude.com
Google: Gemini 3.7/3.6/3.5 Flash, 2.5 Pro; 3.1 Pro в превью → ai.google.dev
DeepSeek: V4-Pro (13.08.2026, 1,7T параметров), V4-Flash (304B), контекст 1M, лицензия MIT → api-docs.deepseek.com
Alibaba Qwen: Qwen3.8-2.4T-A95B (флагман), Qwen3.8-27B, Qwen3-VL, qwen3.5-ocr → huggingface.co
Moonshot: Kimi K3 (16.07.2026, веса 27.07), K2.7-Code (12.06.2026); K2.5 сворачивается 31.08.2026 → platform.kimi.ai
Meta: Muse Glimmer (~10.08.2026, 30B, Apache 2.0), Muse Spark (04.2026); Llama заморожена на v4 → research.meta.ai
Яндекс: Alice AI LLM/Flash/VLM/ART; «YandexGPT» устаревшее название → ya.ru/ai/aliceai
Сбер: GigaChat 3 Ultra (15.07.2026); GigaChat 2 Lite/Pro/Max → developers.sber.ru
Цены за 1M токенов: Opus 5 $5/$25, GPT-5.6 Sol $2,50/$15, Terra $1/$6, Luna $0,10/$0,60, DeepSeek V4 Pro $0,435/$0,87, V4 Flash $0,14/$0,28, Kimi K3 $3/$15, K2.7-Code $0,95/$4 → соответствующие вендоры
«DeepSeek дешевле на порядок» — неточно, разброс 5,7–28,7× (отклонено уточнение формулировки)
Разрыв GPT-5.6 Sol vs Luna: 25× по output
DeepSeek V4: лицензия MIT; Muse Glimmer: Apache 2.0 без ограничений MAU; Qwen3.8-27B/Qwen3-VL: Apache 2.0; Qwen3.8-2.4T-A95B: собственная лицензия qwen3.8-max; Kimi K3: собственная с порогами ($20M/12мес выручки MaaS, >100M MAU); K2.7-Code: Modified MIT; Llama Community License — не open source по OSI, порог 700M MAU → opensource.org/blog, 23.02.2026
ATOM Report: доля Qwen в дообученных моделях 1% (янв 2024) → 69% (фев 2026); Meta пик 44% (авг 2024) → 11% (фев 2026) → arxiv.org/html/2604.07190
HF State of Open Models лето 2026: Qwen 151 448 производных, Meta ~58 000 → huggingface.co/blog
«Экосистема Llama самая развитая» (отклонено) — устарело, Qwen лидирует
1M контекст — норма у большинства топ-моделей 2026; максимум на рынке — Llama 4 Scout, 10M
«Одно из самых больших окон» про Gemini (отклонено) — сила Gemini в мультимодальности, не контексте
Qwen для OCR: PDF до 50 стр/100 МБ, document parsing, 32 языка → huggingface.co/qwen3-vl
GigaChat распознаёт документы txt/doc/docx/pdf/epub/ppt/pptx/xlsx, изображение до 15 МБ → developers.sber.ru
Alice AI: OCR вынесен в отдельный Yandex Vision OCR → aistudio.yandex.ru/docs/vision
Kimi K3: изображения только base64/file ID, PDF/OCR не заявлены → platform.kimi.ai
DeepSeek API не мультимодален; отдельная DeepSeek-OCR-2 (~3B, Apache 2.0)
Бенчмарки: Terminal-Bench 2.1 — Fable 5 83,8%±1,2% (1-е место) → tbench.ai; AA-Briefcase — Fable 5 Elo 1574, Kimi K3 1543, GPT-5.6 Sol 1501 → artificialanalysis.ai; Intelligence Index — Opus 5 63, Fable 5 62, GPT-5.6 Sol 61, Kimi K3 60 → artificialanalysis.ai
SWE-bench Verified (отклонено) — ретирован OpenAI 23.02.2026, 59,4% задач с дефектами
MERA 17.08.2026: Claude-Opus-4.6 0,862 (1-е место), GigaChat-3.1-Ultra 0,712 (23-е место) → MERA лидерборд
«Российские модели точнее в русской юридической терминологии» (отклонено) — MERA/ruMMLU не подтверждают; корректный аргумент за российские модели — доступность, комплаенс, 152-ФЗ, отсутствие риска отключения
Alice AI инициализирована весами Qwen3-235B → техрепорт Яндекса
