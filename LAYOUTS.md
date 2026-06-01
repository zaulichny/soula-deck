# Справочник макетов SOULA Deck

Поля каждого макета и пример «рыбы» из шаблона. В заголовке (`headline`) одно слово оборачивай в `*звёздочки*` — станет розовым акцентом.


## `title` — Титульный слайд

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | TEAM SYNC · MAY 2026 |
| `headline` | заголовок c *акцентом* | Your presentation title, felt and clear. |
| `subtitle` | строка | A one-line frame for what this deck is about — keep it to a single calm sentence the room can hold onto. |
| `presenter_label` | строка | PRESENTER |
| `presenter` | строка | Your Name |
| `team_label` | строка | TEAM |
| `team` | строка | Product · Soula |
| `date_label` | строка | DATE |
| `date` | строка | 29 May 2026 |

## `section` — Разделитель раздела

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `number` | строка | 01 |
| `eyebrow` | строка | SECTION |
| `headline` | заголовок c *акцентом* | Where we are, plainly. |
| `subtitle` | строка | A short framing sentence for the chapter that follows. |

## `context` — Контекст: тезис + поддержка

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | CONTEXT |
| `headline` | заголовок c *акцентом* | A headline that states the one idea of this slide. |
| `lead` | строка | Lead paragraph. Open with the takeaway, then give it room to breathe — two or three sentences at most. The reader should get the point before they finish the first line. |
| `supporting` | строка | Supporting column. Use this for the secondary detail, the caveat, or the "why it matters" — the part people read if they want more, and skip if they don't. |
| `note` | строка | Keep paragraphs short. White space is part of the brand. |

## `two-columns` — Две колонки

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | TWO COLUMNS |
| `headline` | заголовок c *акцентом* | Two points that sit side by side. |
| `colA_tag` | строка | A |
| `colA_heading` | строка | First column heading |
| `colA_body` | строка | Use parallel structure across both columns — same shape of sentence, same length. The contrast does the work. Good for option A vs option B, or now vs next. |
| `colB_tag` | строка | B |
| `colB_heading` | строка | Second column heading |
| `colB_body` | строка | When the two columns mirror each other, the slide reads in a glance. Resist the urge to add a third column — split into another slide instead. |

## `agenda` — Повестка / список (до 4 пунктов)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | AGENDA |
| `headline` | заголовок c *акцентом* | A short list, each line earning its place. |
| `item1_num` | строка | 01 |
| `item1_heading` | строка | First point |
| `item1_body` | строка | One line of supporting copy — what it is and why it's here. |
| `item2_num` | строка | 02 |
| `item2_heading` | строка | Second point |
| `item2_body` | строка | Keep each item to a heading plus one calm sentence. |
| `item3_num` | строка | 03 |
| `item3_heading` | строка | Third point |
| `item3_body` | строка | Four to five items is the sweet spot — past that, split the slide. |
| `item4_num` | строка | 04 |
| `item4_heading` | строка | Fourth point |
| `item4_body` | строка | The hair-lines give rhythm; the pink numbers give the eye an anchor. |

## `numbers` — Цифры / метрики (3 показателя)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | BY THE NUMBERS |
| `headline` | заголовок c *акцентом* | Let the figures speak. |
| `intro` | строка | One framing line above, then three numbers big enough to read from the back of the room. |
| `stat1_value` | часть строки (цифра/единица) | 68 |
| `stat1_unit` | часть строки (цифра/единица) | % |
| `stat1_label` | строка | Short label describing what this number measures. |
| `stat2_value` | часть строки (цифра/единица) | 2.4 |
| `stat2_unit` | часть строки (цифра/единица) | × |
| `stat2_label` | строка | Keep labels to a single line where you can. |
| `stat3_value` | часть строки (цифра/единица) | 12 |
| `stat3_unit` | часть строки (цифра/единица) | k |
| `stat3_label` | строка | Unit in pink, value in ink — that's the pattern. |

## `before-after` — Было / Стало

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | BEFORE / AFTER |
| `headline` | заголовок c *акцентом* | Show the shift, not just the destination. |
| `before_tag` | строка | BEFORE |
| `before_heading` | строка | The old way |
| `before_lines` | строки (через \n) | State the friction in the reader's words. |
| `after_tag` | строка | AFTER |
| `after_heading` | строка | The new way |
| `after_lines` | строки (через \n) | Mirror each line from the left panel. |

## `roadmap` — Дорожная карта (4 фазы)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | ROADMAP |
| `headline` | заголовок c *акцентом* | Four phases, one direction. |
| `phase1_tag` | строка | NOW · Q2 |
| `phase1_heading` | строка | Phase one |
| `phase1_body` | строка | What's happening this quarter — the work in flight right now. |
| `phase2_tag` | строка | NEXT · Q3 |
| `phase2_heading` | строка | Phase two |
| `phase2_body` | строка | The next milestone and what unlocks it. |
| `phase3_tag` | строка | LATER · Q4 |
| `phase3_heading` | строка | Phase three |
| `phase3_body` | строка | Where we're heading once the foundation lands. |
| `phase4_tag` | строка | VISION · 2027 |
| `phase4_heading` | строка | Phase four |
| `phase4_body` | строка | The longer arc — direction, not a dated promise. |

## `overview` — Обзор: тезис слева + пункты справа (до 4)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | OVERVIEW |
| `headline` | заголовок c *акцентом* | A title, with the points that matter. |
| `intro` | строка | Use the left for the frame; let the bullets on the right carry the substance. |
| `bullet1_heading` | строка | First bullet |
| `bullet1_body` | строка | One supporting line — keep it to a single calm sentence. |
| `bullet2_heading` | строка | Second bullet |
| `bullet2_body` | строка | Each point earns its place; cut anything that doesn't. |
| `bullet3_heading` | строка | Third bullet |
| `bullet3_body` | строка | Four to five bullets is the ceiling for one slide. |
| `bullet4_heading` | строка | Fourth bullet |
| `bullet4_body` | строка | The pink dot is the only ornament you need. |

## `steps-screen` — Как это работает + скриншот (3 шага)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `screen_label` | строка | ADD SCREEN |
| `eyebrow` | строка | HOW IT WORKS |
| `headline` | заголовок c *акцентом* | Three steps from open to held. |
| `step1_num` | строка | 01 |
| `step1_heading` | строка | Check in |
| `step1_body` | строка | Name how today feels — two taps, no sentence required. |
| `step2_num` | строка | 02 |
| `step2_heading` | строка | Talk with Soula |
| `step2_body` | строка | A conversation that meets the state you just named. |
| `step3_num` | строка | 03 |
| `step3_heading` | строка | Follow your practice |
| `step3_body` | строка | A short program and picks for right now, tuned to you. |

## `features-screen` — Что получаешь + скриншот (3 пункта)

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `screen_label` | строка | ADD SCREEN |
| `eyebrow` | строка | WHAT YOU GET |
| `headline` | заголовок c *акцентом* | Everything in one soft place. |
| `feature1_heading` | строка | Your current state, at a glance |
| `feature1_body` | строка | The orb reflects how you arrive — before a word is typed. |
| `feature2_heading` | строка | A program that adapts |
| `feature2_body` | строка | Week by week, paced to where you actually are. |
| `feature3_heading` | строка | Practice for right now |
| `feature3_body` | строка | Short audio, a CBT walk, a kind word — one tap away. |

## `steps-alt` — Как это работает (компактно) + скриншот

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | HOW IT WORKS |
| `headline` | заголовок c *акцентом* | Open it, and it meets you. |
| `screen_label` | строка | ADD SCREEN |
| `step1_tag` | строка | 01 · ARRIVE |
| `step1_heading` | строка | Check in |
| `step1_body` | строка | Name the state in two taps. |
| `step2_tag` | строка | 02 · TALK |
| `step2_heading` | строка | Soula's right here |
| `step2_body` | строка | A conversation, not a form. |
| `step3_tag` | строка | 03 · PRACTICE |
| `step3_heading` | строка | Tuned to you |
| `step3_body` | строка | A program and picks for right now. |

## `closing` — Спасибо / контакты

| Поле | Тип | Пример из шаблона |
|------|-----|-------------------|
| `eyebrow` | строка | THANK YOU |
| `headline` | заголовок c *акцентом* | Questions and what's next. |
| `subtitle` | строка | Close with the one thing you want the room to do or remember. |
| `contact1_label` | строка | SLACK |
| `contact1_value` | строка | #team-channel |
| `contact2_label` | строка | EMAIL |
| `contact2_value` | строка | you@soula.care |
| `contact3_label` | строка | DECK |
| `contact3_value` | строка | go/your-deck |
