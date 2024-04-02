isBuild = False # если True - будет обращаться к webui api, иначе будет присылать ./example.jpg
spyMode = False # если True - будет отправлять много информации в infoChatId
API_TOKEN = "<Обязательно заполнить>" # токен бота телеграм
adminID = [] # список юзеров, которые не могут быть прошпионены даже в spyMode=True
infoChatID = "<Обязательно заполнить>" # id чата куда отправляется информация spyMode и ошибки(в любом случае)
yoomoneyToken = "" # yoomoney токен для оплаты
yoomoneyAccount = "" # yoomoney аккаунт для оплаты
floodControlSeconds = 1 # раз в сколько секунд бот будет обрабатывать кнопочки и запросы (чтоб не флудили)
bot_timezone = 3 # временная зона бота
subscriptionPrice = 150 # стоимость подписки
reqParams = ["tags", "antitags", "model", "imgCount", "scale", "width", "height", "reference", "referenceStrength"]
reqParamsMaximums = { # максимумы для изменяемых параметров
  "imgCount": 5, 
  "scale": 100, 
  "width": 900, 
  "height": 900,
  "referenceStrength": 100
}
initReq = { # изначальный запрос
  "tags": "none", 
  "antitags": "none", 
  "model": "Модель 1", 
  "imgCount": "1", 
  "scale": "15", 
  "width": "500", 
  "height": "700",
  "reference": "none",
  "referenceStrength": "50"
}
modelsDefaultAntitags = { # изначальные антитеги для моделей(применяются в любом случае)
  "Модель 1": "(worst quality, low quality:1.4), (lowres:1.1), (monochrome:1.1), (greyscale), badhandv4:1.2",
  "Модель 2": "(worst quality, low quality:1.4), (depth of field, bokeh, blurry:1.4), (realistic, lip, nose, tooth, rouge, lipstick, eyeshadow:1.0), (jpeg artifacts:1.4)",
}
modelsDefaultTags = { # изначальные теги для моделей(применяются в любом случае)
  "Модель 1": "masterpiece, (best quality:1.2)",
  "Модель 2": "masterpiece, (best quality:1.2)",
}