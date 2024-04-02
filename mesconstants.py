from constants import reqParamsMaximums

mesdict = { # словарь всех сообщений, текстов и !!! настроек запросов к моделям и их vae !!!
  "rus": {
    "start": '''
🫐 Добро  пожаловать  в 🫐
🫐🤖 Blueberry AI Bot 🤖🫐
    ''',
    "help": {
      "menu": "Инструкция:\n(для начала можно прочитать только 1ый подпункт)",
      "end": "Инструкция закрыта",
      "start": 
'''
Создать новый запрос для генерации изображения можно одним из 3х способов:

1. Написать боту любой текст, который будет добавлен в теги нового запроса.
2. Просто скопировать и вставить текст другого запроса, все параметры которого будут присвоены новому.
3. Прислать боту изображение, которое будет использовано в качестве примера для нового запроса.

После задания запроса все параметры можно изменять. Для начала генерации запрос нужно подтвердить. Все русские теги будут автоматически переведены на английский.  
''', 
    "params": 
'''
Параметры запроса:

1. Теги - по этим тегам будет сгенерировано изображение. Теги перечисляются через запятую. Важные теги оборачиваются в скобки: (важный тег), ((ещё более важный тег)), (((пипец очень важный тег))). Теги на русском будут автоматически переведены на английский.
2. Антитеги - работают как обратные теги. 
3. Тип - определяет стиль, в котором будет рисоваться изображение.
4. Кол-во изображений - число генерируемых изображений.
5. Пригодность - определяет то, насколько ИИ может отклоняться от тегов(чем больше значение, тем меньше отклонение).
6. Ширина - ширина генерируемого изображения.
7. Высота - высота генерируемого изображения.
8. Пример картинки - изображение, на основе которого будет генерироваться картинка
9. Схожесть с примером - то, насколько похоже генерируемая картинка на изображение-пример(чем выше значение, тем больше схожесть)
''',
      "upgradeandsimilary": 
"""
Генерация похожего - генерируется одно изображение с теми-же тегами и исходным изображением в качества 'примера картинки'.

Улучшение качества - улучшает качество изображения ровно в 2 раза от исходного. 
""",
      "subscription": 
"""
Пользователи без подписки могут генерировать 10 изображений в день. Обновление происходит каждые 24 часа в 00:00 по МСК.

Подписка стоимостью в 150р оформляется ровно на 30 дней. С ней ограничения на запросы исчезают. Кроме того, пользователи с подпиской получают приоритетную очередь.
""",
      "contacts": "По техническим проблемам, вопросам рекламы и даже покупке исходного кода) пишите <ваш аккаунт>",
    },
    "subscription": {
      "notFound": "Подписка не найдена. Транзакция на оплату создана -",
      "foundOld": "подписка закончилась. Транзакция на оплату создана -",
      "found": "Подписка активна 😎 до"
    },
    "payment": {
      "notFound": "Оплата не найдена",
      "found": "Подписка активирована 😎"
    },
    "generation": {
      "start": "Генерация запущена 🌀\nВаше место в очереди -",
      "successful": "Генерация завершена ✅",
      "error": "Ошибка генерации. Повторите запрос через 3 минуты ❎",
      "wait": "Дождитесь окончания прошлой генерации 🌀",
      "subscribe": "Без подписки можно генерировать только 10 изображений в день",
      "everyImg": 'Бот не несёт ответственности за сгенерированный вами материал',
    },
    "value": {
      "successful": "Значение установлено: ",
      "mustbe": "Значение должно быть числом от 1 до ",
      "edit": {
        "tags": "Напишите новые теги: ", 
        "antitags": "Напишите новые антитеги: ", 
        "imgCount": f"Напишите новое кол-во изображений(до {reqParamsMaximums['imgCount']}): ", 
        "referenceStrength": f"Напишите новую схожесть генерируемого изображения с примером(до {reqParamsMaximums['referenceStrength']}): ",
        "scale": f"Напишите новый параметр пригодности(до {reqParamsMaximums['scale']}): ", 
        "width": f"Напишите новую ширину(до {reqParamsMaximums['width']}): ", 
        "height": f"Напишите новую высоту(до {reqParamsMaximums['height']}): "
      }
    },
    "reference": {
      "set": "Пришлите фото, по которому будет генерироваться изображение или нажмите 'Удалить пример ❎': ",
      "delete": "Пример удален ✅",
      "pleaseset": "Пришлите фото, по которому будет генерироваться изображение или нажмите 'Удалить пример ❎' в панели выше 🔝"
    },
    "model": {
      "set": "Выберите тип: ",
      "pleaseset": "Для продолжения выберите тип в панели выше 🔝",
      "names": {
        "Модель 1": "aom2h.safetensors",
        "Модель 2": "aom3.safetensors",
      },
      "vae": {
        "Модель 1": "om.vae.pt",
        "Модель 2": "om.vae.pt",
      }
    },
    "reqParamsTexts": {
      "tags": "Теги: ", 
      "antitags": "Антитеги: ", 
      "model": "Тип: ", 
      "imgCount": "Кол-во изображений: ", 
      "scale": "Пригодность: ", 
      "width": "Ширина: ", 
      "height": "Высота: ",
      "reference": "Пример картинки: ",
      "referenceStrength": "Схожесть с примером: "
    },
    "hashtagText": "Хэштеги(не влияют на генерацию): ",
    "notStarted": "🫐 Напишите /start для обновления бота 🫐",
    "error": "Ошибка ❎"
  }
}