from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from mesconstants import mesdict
from collections import deque


keydict = {"rus": {}}

#region main
keydict["rus"]["main"] = ReplyKeyboardMarkup(resize_keyboard=True)
keydict["rus"]["main"].add("💵 Подписка 💵")
keydict["rus"]["main"].add("ℹ️ Помощь ℹ️")
#endregion main

#region request
keydict["rus"]["request"] = InlineKeyboardMarkup()
keydict["rus"]["request"].row(InlineKeyboardButton(text="Изменить теги", callback_data="edit_tags"), InlineKeyboardButton(text="Изменить антитеги", callback_data="edit_antitags"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Выбрать тип", callback_data="set_model"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Изменить кол-во изображений", callback_data="edit_imgCount"), InlineKeyboardButton(text="Изменить пригодность", callback_data="edit_scale"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Изменить ширину", callback_data="edit_width"), InlineKeyboardButton(text="Изменить высоту", callback_data="edit_height"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Установить пример картинки", callback_data="set_reference"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Установить схожесть с примером", callback_data="edit_referenceStrength"))
keydict["rus"]["request"].row(InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm"), InlineKeyboardButton(text="Отменить ❎", callback_data="cancel"))
#endregion request

#region end
keydict["rus"]["end"] = InlineKeyboardMarkup()
keydict["rus"]["end"].row(InlineKeyboardButton(text="Повторить 🔄", callback_data="repeat"))
#endregion end

#region model
keydict["rus"]["model"] = InlineKeyboardMarkup()
btnGroup = []
for model in mesdict['rus']['model']['names']:
  btnGroup.append(InlineKeyboardButton(text=model, callback_data=f"model_{model}"))
  if len(btnGroup) % 2 == 0:
    keydict["rus"]["model"].row(*btnGroup)
    btnGroup = []

if len(mesdict['rus']['model']['names'])%2 == 1:
  keydict["rus"]["model"].add(InlineKeyboardButton(text=deque(mesdict['rus']['model']['names'], maxlen=1)[0], callback_data=f"model_{deque(mesdict['rus']['model']['names'], maxlen=1)[0]}"))
#endregion model

#region reference
keydict["rus"]["reference"] = InlineKeyboardMarkup()
keydict["rus"]["reference"].row(InlineKeyboardButton(text="Удалить пример ❎", callback_data="delete_reference"))
#endregion reference

#region after generation
keydict["rus"]["afterGeneration"] = InlineKeyboardMarkup()
keydict["rus"]["afterGeneration"].row(InlineKeyboardButton(text="Генерировать похожее 🔂", callback_data="generate_similary"))
keydict["rus"]["afterGeneration"].row(InlineKeyboardButton(text="Улучшить качество ⏫", callback_data="upgrade_quality"))
#endregion after generation

#region help keyboards
keydict["rus"]["help"] = InlineKeyboardMarkup()
keydict["rus"]["help"].row(InlineKeyboardButton(text="Основное", callback_data="help_start"))
keydict["rus"]["help"].row(InlineKeyboardButton(text="Параметры запроса", callback_data="help_params"))
keydict["rus"]["help"].row(InlineKeyboardButton(text="Генерация похожего и улучшение качества", callback_data="help_upgradeandsimilary"))
keydict["rus"]["help"].row(InlineKeyboardButton(text="Подписка", callback_data="help_subscription"))
keydict["rus"]["help"].row(InlineKeyboardButton(text="Контакты", callback_data="help_contacts"))
keydict["rus"]["help"].row(InlineKeyboardButton(text="Закрыть ❎", callback_data="end_help"))


keydict["rus"]["helpUndo"] = InlineKeyboardMarkup()
keydict["rus"]["helpUndo"].row(InlineKeyboardButton(text="Назад ◀️", callback_data="undo_help"))
#endregion help keyboards

#region update queue
keydict["rus"]["updateQueue"] = InlineKeyboardMarkup()
keydict["rus"]["updateQueue"].row(InlineKeyboardButton(text="Обновить место в очереди 🔄", callback_data="update_queue"))
#endregion update queue

#region func-generate keyboard
def generate_pay_keyboard(url, lang):
  if lang == "rus":
    payKeyboard = InlineKeyboardMarkup()
    payKeyboard.row(InlineKeyboardButton(text="Проверить оплату 🔄", callback_data="check_pay"))
    payKeyboard.row(InlineKeyboardButton(text="Оплатить 💴", url=url))
    return payKeyboard
#endregion func-generate keyboards