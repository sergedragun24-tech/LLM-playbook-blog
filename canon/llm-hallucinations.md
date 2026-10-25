# Канон: галлюцинации LLM — проверенные источники и цифры

Собрано 12.08.2026 при проверке статьи по теме.

## Три утверждения, которые нельзя писать (проверено, опровергается источником)

**1. «Внутри модели нет механизма, отличающего "знаю точно" от "звучит правдоподобно»».**
Неверно как категорическое утверждение. Kadavath et al. (Anthropic, 2022): «larger models are well-calibrated on diverse multiple choice and true/false questions when they are provided in the right format»; модели показывают «encouraging performance, calibration, and scaling for P(True)» и «perform well at predicting P(IK)» (вероятность того, что ответ известен). Ограничение там же: «struggle with calibration of P(IK) on new tasks», обобщается только частично.
https://arxiv.org/abs/2207.05221
**Корректная формулировка:** сигнал неопределённости внутри модели есть, но он не выводится в текст ответа по умолчанию и плохо калибруется на незнакомых задачах.

**2. «Модель не говорит "не знаю", потому что отказов мало в обучающих данных».**
Механизм придуман, подтверждения нет. Проверенное объяснение — Kalai, Nachum, Vempala, Zhang (OpenAI, сент. 2025), «Why Language Models Hallucinate»: «language models hallucinate because the training and evaluation procedures reward guessing over acknowledging uncertainty»; «language models are optimized to be good test-takers, and guessing when uncertain improves test performance»; модель, которая всегда угадывает, обгоняет модель, честно сообщающую о неуверенности, «under 0-1 scoring, the basis of most current benchmarks».
https://arxiv.org/abs/2509.04664 · https://openai.com/index/why-language-models-hallucinate/

**3. «Выше temperature — выше риск галлюцинации» (в диапазоне 0–1).**
Прямого подтверждения нет. Renze, Guven, Findings of EMNLP 2024: «changes in temperature from 0.0 to 1.0 do not have a statistically significant impact on LLM performance for problem-solving tasks», результат воспроизводится на разных моделях, промптах и предметных областях.
https://aclanthology.org/2024.findings-emnlp.432/

**Отдельно про структурированный вывод.** Тезис «жёсткий формат сам по себе снижает недостоверность» спорный. Tam et al., EMNLP 2024 (industry track), «Let Me Speak Freely?»: «we observe a significant decline in LLMs' reasoning abilities under format restrictions», «stricter format constraints generally lead to greater performance degradation in reasoning tasks».
https://aclanthology.org/2024.emnlp-industry.91/
Корректно: структурированный вывод делает ошибку машинно-проверяемой (валидация полей, типов, диапазонов), но на задачах с рассуждением жёсткий формат качество ухудшает.

## Проверенные цифры

| Тезис | Формулировка источника | Источник |
|---|---|---|
| Редкий факт → гарантированные ошибки, снизу | «if 20% of birthday facts appear exactly once in the pretraining data, then one expects base models to hallucinate on at least 20% of birthday facts» | Kalai et al., OpenAI, arXiv:2509.04664 |
| Галлюцинации неустранимы не «в принципе», а из-за метрик | «Hallucinations are inevitable only for base models»; «A non-hallucinating model could be easily created, using a question-answer database and a calculator… and otherwise outputs IDK»; лечение — «modifying the scoring of existing benchmarks», а не добавление новых тестов на галлюцинации | там же |
| RAG снижает, но не устраняет — с цифрой | юридические RAG-инструменты Lexis+ AI, Westlaw AI-Assisted Research, Ask Practical Law AI «hallucinate between 17% and 33% of the time»; «the providers' claims are overstated» (они заявляли elimination/avoidance) | Magesh, Surani, Dahl, Suzgun, Manning, Ho. Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools. Journal of Empirical Legal Studies, 2025. https://arxiv.org/abs/2405.20362 · https://onlinelibrary.wiley.com/doi/full/10.1111/jels.12413 |
| Длинный контекст: деградация с цифрами | 13,9%–85% общий диапазон; Llama-3.1-8B на MMLU −24,2%; Mistral на GSM8K −34,2% при 30K токенов; при набивке длины пробелами падение до 48% | Du, Tian, Ronanki et al., Findings of EMNLP 2025. https://aclanthology.org/2025.findings-emnlp.1264.pdf |
| «Потерянное в середине» — первоисточник | модели точнее используют начало и конец длинного контекста, хуже — середину | Liu et al., TACL. https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.tacl2023.pdf |
| Масштаб юридических последствий | база судебных решений, где суд установил опору на выдуманный ИИ-контент: 1868 дел, США 1297, Канада 206, Австралия 97, Великобритания 61, Израиль 55; с Q2 2023; данные на 08.08.2026. Стороны: 1096 — участники без представителя, 724 — юристы | Damien Charlotin (HEC Paris), AI Hallucination Cases. https://www.damiencharlotin.com/hallucinations/ |

Первый громкий кейс для примера — Mata v. Avianca (Стивен Шварц, шесть несуществующих прецедентов, 2023). Проверять по первичному изложению, не по пересказу: русскоязычные материалы приписывают работе OpenAI проценты, которых в ней нет (замечено у Naked Science).

## Не использовать

- **sqmagazine.co.uk** — уже в чёрном списке; именно оттуда в РУ-выдачу («от 15% до 52%, анализ 37 моделей») тянется цифра через sostav.ru.
- Цифры Algorcomp, Pithum, «IBM 2024 — 72% сбоев» из sostav.ru — без рабочих ссылок и первичной атрибуции.
- «47,5% → 14,5% при итеративном саморедактировании» (Хабр/OTUS) — источник в материале не указан.
- Vectara HHEM / Hallucination Leaderboard — использовать можно, но помнить: это узкая задача (грounded summarization на английском), проценты оттуда нельзя подавать как «доля галлюцинаций модели вообще». Именно так их подают Т—Ж («от 3 до 27%») и Beeline Cloud.

## Чего нет — не додумывать

- Цифр по галлюцинациям русскоязычных моделей (GigaChat, YandexGPT, T-Pro, Cotype) и русскоязычных бенчмарков галлюцинаций. Пустая ниша во всей выдаче.
- Стоимости методов контроля: сколько добавляют self-consistency, вторая модель-судья, human-in-the-loop в токенах, латентности и GPU-времени. Никто не считает. Арифметику «второй прогон = второй вызов модели» писать можно, конкретные суммы — нет.
- Порогов приёмки (groundedness / faithfulness) и регламента регресс-теста при смене версии модели.
- Российской правовой рамки: кто отвечает за галлюцинацию в клиентском канале, что логировать для разбора инцидента.

## Строки для индекса

Kalai et al. (OpenAI, сент. 2025, arXiv:2509.04664): модели галлюцинируют, т.к. обучение вознаграждает угадывание; 20% редких фактов гарантируют ошибки; неизбежность только для base models
Renze, Guven (EMNLP 2024): температура 0–1 не влияет статистически значимо на результат
Tam et al. (EMNLP 2024): жёсткий формат вывода снижает способности рассуждения
Magesh et al. (Journal of Empirical Legal Studies, 2025): юридические RAG-сервисы галлюцинируют 17–33% времени
Du et al. (EMNLP 2025): деградация на длинном контексте 13,9–85%; Llama-3.1-8B −24,2% на MMLU, Mistral −34,2% на GSM8K при 30K токенов
Liu et al. (TACL 2023): эффект «потерянное в середине»
Charlotin (HEC Paris): 1868 судебных дел на AI-галлюцинации на 08.08.2026 (США 1297, Канада 206, Австралия 97, UK 61, Израиль 55)
«Внутри модели нет механизма различения» (отклонено); «выше temperature → выше галлюцинации» (отклонено, подтверждения нет)
