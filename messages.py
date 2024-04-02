from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram import types, Dispatcher
from aiogram.utils import exceptions
from deep_translator import GoogleTranslator as Translator
from yoomoney import Quickpay, Client
from random import randint
import asyncio
import base64
from PIL import Image
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import timedelta,  timezone
import time

from constants import adminID, infoChatID, yoomoneyToken, bot_timezone, yoomoneyAccount, reqParams, reqParamsMaximums, initReq, modelsDefaultAntitags, modelsDefaultTags, subscriptionPrice, floodControlSeconds, spyMode
from mesconstants import mesdict
from keyboards import keydict, generate_pay_keyboard
from sd.sd_func import text_to_img, img_to_img, extra_single_img
from db.db_func import add_subscription, get_subscription, add_generation, clear_generations


class Task():
  def __init__(self, data):
    self.data = data 
    self.time = time.time()

  def __lt__(self, other):
    return self.time < other.time

  def __eq__(self, other):
    return self.time == other.time


thisTZ = timezone(timedelta(hours=bot_timezone), name="MY")
yoomoneyCli = Client(yoomoneyToken)
floodControl = []
genNow = []
genNowSub = []
genQueue = asyncio.PriorityQueue()
# started = []

#region gen func
def gen_now_append(chatId):
  # if get_subscription(chatId)["status"]:
  #   genNowSub.append(chatId)
  # else:
  #   genNow.append(chatId)
  genNow.append(chatId)

def gen_now_remove(chatId):
  # if get_subscription(chatId)["status"]:
  #   genNowSub.remove(chatId)
  # else:
  #   genNow.remove(chatId)
  genNow.remove(chatId)

def gen_now_is(chatId):
  # if chatId in genNowSub or chatId in genNow:
  #   return True
  # else:
  #   return False
  return True if chatId in genNow else False

def gen_now_len(chatId):
  # if get_subscription(chatId)["status"]:
  #   return len(genNowSub)
  # else:
  #   return len(genNowSub) + len(genNow)
  return len(genNow)
#endregion gen func

#region text func
def text_to_req(reqText, thisInitReq = initReq.copy()):
  req = thisInitReq.copy()
  trueReqText = reqText

  if mesdict['rus']['hashtagText'] in reqText:
    reqText = reqText[:reqText.find(mesdict['rus']['hashtagText'])]

  starts = {}
  for reqParam in reqParams: 
    if mesdict['rus']['reqParamsTexts'][reqParam] in reqText:
      starts[reqParam] = reqText.find(mesdict['rus']['reqParamsTexts'][reqParam])

  sortedStarts = dict(sorted(starts.items(), key=lambda item: item[1]))

  if len(sortedStarts) == 0 and not mesdict['rus']['hashtagText'] in trueReqText:
    req["tags"] = reqText

  sortedStartsKeys = list(sortedStarts.keys())
  for reqParam in sortedStarts:
    nextReqParam = sortedStartsKeys[sortedStartsKeys.index(reqParam)+1] if sortedStartsKeys.index(reqParam) != len(sortedStartsKeys)-1 else "none"
    reqValue = reqText[sortedStarts[reqParam]+len(mesdict['rus']['reqParamsTexts'][reqParam]):sortedStarts[nextReqParam] if nextReqParam != "none" else len(reqText)].replace("\n", " ").strip()
    if reqParam not in reqParamsMaximums or (reqValue.isdigit() and int(reqValue) > 0 and int(reqValue) < reqParamsMaximums[reqParam]+1):
      if reqParam != 'model' or reqValue in mesdict['rus']['model']['names']:
        # if reqParam != "reference":
        req[reqParam] = reqValue

  return req

def req_to_text(req): 
  reqText = ""
  for reqParam in reqParams: 
    if reqParam in req:
      reqText += f"\n{mesdict['rus']['reqParamsTexts'][reqParam]}<code>{str(req[reqParam]).replace('<', '')}</code>"

  return reqText

def normalize_text(reqText, thisInitReq = initReq.copy()):
  return req_to_text(text_to_req(reqText, thisInitReq))
#endregion text func

async def send_generations(bot):
  while True:
    obj = await genQueue.get()
    gen = obj[1].data
    type = gen["type"]

    if type == "generate":
      req = gen["req"]
      call = gen["call"]
      confirmMes =  gen["confirmMes"]
      timeGenStart = gen["timeGenStart"]

      try: 
        res = None
        referenceId = req["reference"]
        if req["reference"] == "none":
          res = await text_to_img(req)
        else:
          reference = await bot.get_file(req["reference"])
          await reference.download(destination_file=f"files/{reference.file_id}.jpg")

          with open(f"files/{reference.file_id}.jpg", "rb") as file:
            req["reference"] = base64.b64encode(file.read()).decode('utf-8')

          req["referenceStrength"] = str(1 - (int(req["referenceStrength"]) / 100))
          res = await img_to_img(req)

      except Exception as e:
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['error'])
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error aftergenerr\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          await bot.send_message(infoChatID, f"#error generr\n{e}")
          gen_now_remove(call.message.chat.id)
      else:
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['successful'])
          if round(time.time() - timeGenStart) > 300:
            await bot.send_message(infoChatID, f"#error bad_time")
          if not call.message.chat.id in adminID and spyMode:
            await bot.send_message(infoChatID, f"@{str(call.message.chat.username)} {round(time.time() - timeGenStart)}с. \n#generate #user{call.message.chat.id} #{'sub' if get_subscription(call.message.chat.id)['status'] else 'not_sub'} {normalize_text(call.message.text)}", parse_mode=types.ParseMode.HTML)
            if referenceId != "none": 
              await bot.send_photo(chat_id = infoChatID, photo=referenceId)

          media = types.MediaGroup()
          for img in res:
            photoMessage = await call.message.reply_photo(img, caption=mesdict['rus']['generation']['everyImg'], reply_markup=keydict['rus']['afterGeneration'])
            media.attach_photo(photoMessage.photo[-1].file_id)
            # if not call.message.chat.id in adminID:
            #   await bot.send_photo(chat_id = infoChatID, photo=photoMessage.photo[-1].file_id)
          if not call.message.chat.id in adminID and spyMode:
            if int(req["imgCount"]) == 1:
              await bot.send_photo(chat_id = infoChatID, photo=photoMessage.photo[-1].file_id)
            else:
              await bot.send_media_group(chat_id = infoChatID, media=media)
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error aftergen\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          gen_now_remove(call.message.chat.id)
        
    elif type == "generateSimilary":
      req = gen["req"]
      call = gen["call"]
      confirmMes = gen["confirmMes"]
      timeGenStart = gen["timeGenStart"]
      replyedMessage = gen["replyedMessage"]

      try: 
        res = None
        reference = await bot.get_file(call.message.photo[-1].file_id)
        await reference.download(destination_file=f"files/{reference.file_id}.jpg")
        referenceId = call.message.photo[-1].file_id

        with open(f"files/{reference.file_id}.jpg", "rb") as file:
          req["reference"] = base64.b64encode(file.read()).decode('utf-8')

        req["referenceStrength"] = str(1 - (int(req["referenceStrength"]) / 100))

        res = await img_to_img(req)
        
      except Exception as e:
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['error'])
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error aftergensimerr\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          await bot.send_message(infoChatID, f"#error gensimerr\n{e}")
          gen_now_remove(call.message.chat.id)
      else: 
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['successful'])
          media = types.MediaGroup()
          photoMessage = await replyedMessage.reply_photo(res[0], caption=mesdict['rus']['generation']['everyImg'], reply_markup=keydict['rus']['afterGeneration'])
          if round(time.time() - timeGenStart) > 300:
            await bot.send_message(infoChatID, f"#error bad_time")
          if not call.message.chat.id in adminID and spyMode:
            await bot.send_message(infoChatID, f"@{str(call.message.chat.username)} {round(time.time() - timeGenStart)}с. \n#generateSimilary #user{call.message.chat.id} #{'sub' if get_subscription(call.message.chat.id)['status'] else 'not_sub'} {normalize_text(replyedMessage.text)}", parse_mode=types.ParseMode.HTML)
            media.attach_photo(referenceId)
            media.attach_photo(photoMessage.photo[-1].file_id)
            await bot.send_media_group(chat_id = infoChatID, media=media)
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error aftergensim\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          gen_now_remove(call.message.chat.id)
    
    elif type == "upgradeQuality":
      req = gen["req"]
      call = gen["call"]
      confirmMes = gen["confirmMes"]
      timeGenStart = gen["timeGenStart"]
      
      try: 
        res = None
        referenceId = call.message.photo[-1].file_id
        reference = await bot.get_file(call.message.photo[-1].file_id)
        await reference.download(destination_file=f"files/{reference.file_id}.jpg")

        with open(f"files/{reference.file_id}.jpg", "rb") as file:
          req["image"] = base64.b64encode(file.read()).decode('utf-8')

        resImg = await extra_single_img(req)
      except Exception as e:
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['error'])
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error afterupgradeerr\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          await bot.send_message(infoChatID, f"#error upgradeerr\n{e}")
          gen_now_remove(call.message.chat.id)
      else: 
        try:
          await confirmMes.edit_text(mesdict['rus']['generation']['successful'])
          photoMessage = await call.message.reply_photo(resImg)
          if round(time.time() - timeGenStart) > 300:
            await bot.send_message(infoChatID, f"#error bad_time")
          if not call.message.chat.id in adminID and spyMode:
            await bot.send_message(infoChatID, f"@{str(call.message.chat.username)} {round(time.time() - timeGenStart)}с. \n#upgradeQuality #user{call.message.chat.id} #{'sub' if get_subscription(call.message.chat.id)['status'] else 'not_sub'}")
            media = types.MediaGroup()
            media.attach_photo(referenceId)
            media.attach_photo(photoMessage.photo[-1].file_id)
            await bot.send_media_group(chat_id = infoChatID, media=media)
        except Exception as ex:
          await bot.send_message(infoChatID, f"#error afterupgrade\n{ex}")
          gen_now_remove(call.message.chat.id)
        else:
          gen_now_remove(call.message.chat.id)

    genQueue.task_done()

def my_messages_handler(dp, bot):

  #region clear generations scheduler
  scheduler = AsyncIOScheduler()
  scheduler.add_job(clear_generations, 'cron', hour=0, minute=0, timezone=thisTZ)
  scheduler.start()
  #endregion clear generations scheduler

  #region states
  class EditState(StatesGroup):
    null = State()
    setModel = State()
    setReference = State()
    edit = State()
  #endregion

  #region error handlers
  @dp.errors_handler(exception=exceptions.RetryAfter)
  async def exception_handler(update: types.Update, e: exceptions.RetryAfter):
    await bot.send_message(infoChatID, f"#error retry_after\n{e}")
    return True
  #endregion error handlers

  @dp.message_handler(commands=['start'], state=["*"])
  async def start(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
      # started.append(message.chat.id)
      await message.answer(mesdict['rus']['start'], reply_markup=keydict['rus']['main'])
      await EditState.null.set()

  #region set model
  @dp.callback_query_handler(lambda c: c.data and c.data == "set_model", state=["*"])
  async def set_model(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(mesdict['rus']['model']['set'], reply_markup=keydict['rus']['model'])
    await state.update_data(editParam="model", editMessage=call.message)
    await EditState.setModel.set()
  
  @dp.message_handler(content_types=['photo'], state=EditState.setModel)
  async def set_model_photo(message: types.Message, state: FSMContext):
    await message.answer(mesdict['rus']['model']['pleaseset'])
    
  @dp.message_handler(content_types=['text'], state=EditState.setModel)
  async def set_model_text(message: types.Message, state: FSMContext):
    if message.text == "ℹ️ Помощь ℹ️":
      await message.answer(mesdict['rus']['help'], parse_mode=types.ParseMode.HTML)
    else:
      await message.answer(mesdict['rus']['model']['pleaseset'])

  @dp.callback_query_handler(lambda c: c.data and c.data.startswith("model"), state=EditState.setModel)
  async def set_model_choose(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    value = call.data[6:]
    try:
      req = text_to_req(data["editMessage"].text)
      if req[data["editParam"]] != value:
        req[data["editParam"]] = value
        await bot.edit_message_text(req_to_text(req), call.message.chat.id, data["editMessage"].message_id, reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML) 
        await state.update_data(defaultModel=req[data["editParam"]])
    except Exception as e:
      await EditState.null.set()
      await call.message.edit_text(mesdict['rus']['error'])
      await bot.send_message(infoChatID, f"#error set_model_choose\n{e}")
    else:
      await EditState.null.set()
      await call.message.edit_text(f"{mesdict['rus']['value']['successful']}<code>{str(value).replace('<', '')}</code>", parse_mode=types.ParseMode.HTML)
  #endregion set model

  #region set reference
  @dp.callback_query_handler(lambda c: c.data and c.data == "set_reference", state=["*"])
  async def set_reference(call: types.CallbackQuery, state: FSMContext):
    setReferenceMessage = await call.message.answer(mesdict['rus']['reference']['set'], reply_markup=keydict['rus']['reference'])
    await state.update_data(editParam="reference", editMessage=call.message, setReferenceMessage=setReferenceMessage)
    await EditState.setReference.set()
  
  @dp.message_handler(content_types=['photo'], state=EditState.setReference)
  async def set_reference_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    value = message.photo[-1].file_id
    try:
      req = text_to_req(data["editMessage"].text)
      await data["setReferenceMessage"].edit_text(f"{mesdict['rus']['value']['successful']}<code>{str(value).replace('<', '')}</code>", parse_mode=types.ParseMode.HTML)
      if req[data["editParam"]] != value:
        req[data["editParam"]] = value
        thisHeight = message.photo[-1].height
        thisWidth = message.photo[-1].width
        while thisHeight > reqParamsMaximums["height"] or thisWidth > reqParamsMaximums['width']:
          thisHeight -= thisHeight/10
          thisWidth -= thisWidth/10
        req["width"] = round(thisWidth)
        req["height"] = round(thisHeight)
        await bot.edit_message_text(req_to_text(req), message.chat.id, data["editMessage"].message_id, reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML) 
    except Exception as e:
      await EditState.null.set()
      await message.answer(mesdict['rus']['error'])
      await bot.send_message(infoChatID, f"#error set_reference_photo\n{e}")
    else:
      await EditState.null.set()

  @dp.message_handler(content_types=["text"], state=EditState.setReference)
  async def set_reference_text(message: types.Message, state: FSMContext):
    if message.text == "ℹ️ Помощь ℹ️":
      await message.answer(mesdict['rus']['help'], parse_mode=types.ParseMode.HTML)
    else:
      await message.answer(mesdict['rus']['reference']['pleaseset'])

  @dp.callback_query_handler(lambda c: c.data and c.data == "delete_reference", state=EditState.setReference)
  async def set_reference_delete(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    value = "none"
    try:
      req = text_to_req(data["editMessage"].text)
      if req[data["editParam"]] != value:
        req[data["editParam"]] = value
        await bot.edit_message_text(req_to_text(req), call.message.chat.id, data["editMessage"].message_id, reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML) 
    except Exception as e:
      await EditState.null.set()
      await call.message.edit_text(mesdict['rus']['error'])
      await bot.send_message(infoChatID, f"#error set_reference_delete\n{e}")
    else:
      await EditState.null.set()
      await call.message.edit_text(mesdict['rus']['reference']['delete'], parse_mode=types.ParseMode.HTML)
  
  #endregion set reference

  #region edit
  @dp.callback_query_handler(lambda c: c.data and c.data.startswith("edit"), state=["*"])
  async def edit(call: types.CallbackQuery, state: FSMContext):
    editParam = call.data[5:]
    await call.message.answer(mesdict['rus']['value']['edit'][editParam])
    await EditState.edit.set()
    await state.update_data(editParam=editParam, editMessage=call.message)

  @dp.message_handler(content_types=['photo'], state=EditState.edit)
  async def edit_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data["editParam"] in reqParamsMaximums:
      await message.answer(f"{mesdict['rus']['value']['mustbe']}{reqParamsMaximums[data['editParam']]}")
    else:
      await message.answer(mesdict['rus']['value']['edit'][data["editParam"]])

  @dp.message_handler(content_types=['text'], state=EditState.edit)
  async def edit_text(message: types.Message, state: FSMContext):
    if message.text == "ℹ️ Помощь ℹ️":
      await message.answer(mesdict['rus']['help'], parse_mode=types.ParseMode.HTML)
    else:
      data = await state.get_data()
      value = message.text.strip()
      if data["editParam"] in reqParamsMaximums and (not value.isdigit() or int(value) < 1 or int(value) > reqParamsMaximums[data['editParam']]):
        await message.answer(f"{mesdict['rus']['value']['mustbe']}{reqParamsMaximums[data['editParam']]}")
      else:
        try:
          req = text_to_req(data["editMessage"].text)
          if req[data["editParam"]] != value:
            req[data["editParam"]] = value
            await bot.edit_message_text(req_to_text(req), message.chat.id, data["editMessage"].message_id, reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML) 
        except Exception as e:
          await EditState.null.set()
          await message.answer(mesdict['rus']['error'])
          await bot.send_message(infoChatID, f"#error edit_text\n{e}")
        else:
          await EditState.null.set()
          await message.answer(f"{mesdict['rus']['value']['successful']}<code>{str(value).replace('<', '')}</code>", parse_mode=types.ParseMode.HTML)
  #endregion edit

  #region confirm cancel
  @dp.callback_query_handler(lambda c: c.data and c.data == "confirm", state=["*"])
  async def confirm(call: types.CallbackQuery, state: FSMContext):
    req = text_to_req(call.message.text)
    canImgCount = add_generation(call.message.chat.id, int(req["imgCount"]))
    if canImgCount <= 0 and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['subscribe'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif gen_now_is(call.message.chat.id) and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['wait'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif not (call.message.chat.id in floodControl):
      req["imgCount"] = str(canImgCount)
      timeGenStart = time.time()
      gen_now_append(call.message.chat.id)
      await call.message.edit_reply_markup(keydict['rus']['end'])
      confirmMes = await call.message.answer(f"{mesdict['rus']['generation']['start']} {gen_now_len(call.message.chat.id)}", reply_markup=keydict['rus']['updateQueue'])
      translator = Translator(source='ru', target='en')

      req["tags"] = modelsDefaultTags[req['model']] if req["tags"] == "none" else translator.translate(f"{modelsDefaultTags[req['model']]}, {req['tags']}")
      req["antitags"] = modelsDefaultAntitags[req['model']] if req["antitags"] == "none" else translator.translate(f"{modelsDefaultAntitags[req['model']]}, {req['antitags']}")
      priority = 2 if get_subscription(call.message.chat.id)["status"] else 2
      await genQueue.put((priority, Task({'req': req, 'call': call, 'confirmMes': confirmMes, 'timeGenStart': timeGenStart, 'type': 'generate'})))

  @dp.callback_query_handler(lambda c: c.data and c.data == "cancel", state=["*"])
  async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"{normalize_text(call.message.text)}", reply_markup=keydict['rus']['end'], parse_mode=types.ParseMode.HTML)
  #endregion confirm cancels

  #region after generation
  @dp.callback_query_handler(lambda c: c.data and c.data == "generate_similary", state=["*"])
  async def generate_similary(call: types.CallbackQuery, state: FSMContext):
    if add_generation(call.message.chat.id) <= 0 and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['subscribe'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif gen_now_is(call.message.chat.id) and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['wait'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif not (call.message.chat.id in floodControl):
      try:
        replyedMessage = call.message.reply_to_message
        req = text_to_req(replyedMessage.text)
      except Exception as e:
        await call.message.answer(mesdict['rus']['error'])
        await bot.send_message(infoChatID, f"#error generate_similary\n{e}")
        await call.message.edit_reply_markup()
      else:
        timeGenStart = time.time()
        gen_now_append(call.message.chat.id)
        confirmMes = await call.message.answer(f"{mesdict['rus']['generation']['start']} {gen_now_len(call.message.chat.id)}", reply_markup=keydict['rus']['updateQueue'])
        translator = Translator(source='ru', target='en')

        req["tags"] = modelsDefaultTags[req['model']] if req["tags"] == "none" else translator.translate(f"{modelsDefaultTags[req['model']]}, {req['tags']}")
        req["antitags"] = modelsDefaultAntitags[req['model']] if req["antitags"] == "none" else translator.translate(f"{modelsDefaultAntitags[req['model']]}, {req['antitags']}")
        req["imgCount"] = "1"
        req["referenceStrength"] = "60"
      
        priority = 2 if get_subscription(call.message.chat.id)["status"] else 2
        await genQueue.put((priority, Task({'req': req, 'call': call, 'confirmMes': confirmMes, 'timeGenStart': timeGenStart, 'replyedMessage': replyedMessage, 'type': 'generateSimilary'})))

  @dp.callback_query_handler(lambda c: c.data and c.data == "upgrade_quality", state=["*"])
  async def upgrade_quality(call: types.CallbackQuery, state: FSMContext):
    if add_generation(call.message.chat.id) <= 0 and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['subscribe'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif gen_now_is(call.message.chat.id) and not (call.message.chat.id in floodControl):
      floodControl.append(call.message.chat.id)
      await call.message.answer(mesdict['rus']['generation']['wait'])
      await asyncio.sleep(floodControlSeconds)
      floodControl.remove(call.message.chat.id)
    elif not (call.message.chat.id in floodControl):
      try:
        replyedMessage = call.message.reply_to_message
        req = text_to_req(replyedMessage.text)
      except Exception as e:
        await call.message.answer(mesdict['rus']['error'])
        await bot.send_message(infoChatID, f"#error upgrade_quality\n{e}")
        await call.message.edit_reply_markup()
      else:
        gen_now_append(call.message.chat.id)
        timeGenStart = time.time()
        confirmMes = await call.message.answer(f"{mesdict['rus']['generation']['start']} {gen_now_len(call.message.chat.id)}", reply_markup=keydict['rus']['updateQueue'])
        priority = 2 if get_subscription(call.message.chat.id)["status"] else 2
        await genQueue.put((priority, Task({'req': req, 'call': call, 'confirmMes': confirmMes, 'timeGenStart': timeGenStart, 'type': "upgradeQuality"})))
  
  #endregion after generation

  @dp.callback_query_handler(lambda c: c.data and c.data == "update_queue", state=["*"])
  async def update_queue(call: types.CallbackQuery, state: FSMContext):
    try:
      # if get_subscription(call.message.chat.id)["status"]:
      #   newQueueIndex = genNowSub.index(call.message.chat.id) + 1
      # else:
      #   newQueueIndex = len(genNowSub) + genNow.index(call.message.chat.id) + 1
      newQueueIndex = genNow.index(call.message.chat.id) + 1
    except Exception as e:
      await call.message.edit_text(mesdict['rus']['generation']['error'])
      await bot.send_message(infoChatID, f"#error update_queue\n{e}")
    else: 
      if newQueueIndex != int(call.message.text[call.message.text.index("-")+1:]):
        await call.message.edit_text(f"{mesdict['rus']['generation']['start']} {newQueueIndex}", reply_markup=keydict['rus']['updateQueue'])

  #region end menu
  @dp.callback_query_handler(lambda c: c.data and c.data == "repeat", state=["*"])
  async def repeat(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(f"{normalize_text(call.message.text)}", reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML)
  #endregion end menu

  #region help menu
  @dp.callback_query_handler(lambda c: c.data and c.data.startswith("help"), state=["*"])
  async def help_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(mesdict["rus"]["help"][call.data[5:]], parse_mode=types.ParseMode.HTML, reply_markup=keydict["rus"]["helpUndo"])

  @dp.callback_query_handler(lambda c: c.data and c.data == "undo_help", state=["*"])
  async def help_menu_undo(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(mesdict['rus']['help']['menu'], parse_mode=types.ParseMode.HTML, reply_markup=keydict["rus"]["help"])
  
  @dp.callback_query_handler(lambda c: c.data and c.data == "end_help", state=["*"])
  async def help_menu_end(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(mesdict['rus']['help']['end'], parse_mode=types.ParseMode.HTML)
  #endregion help menu

  #region message
  @dp.message_handler(content_types=["photo"], state=["*"])
  async def photomes(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
      data = await state.get_data()
      thisInitReq = initReq.copy()
      if "defaultModel" in data:
        thisInitReq['model'] = data['defaultModel']
      await EditState.null.set()
      thisHeight = message.photo[-1].height
      thisWidth = message.photo[-1].width
      while thisHeight > reqParamsMaximums["height"] or thisWidth > reqParamsMaximums['width']:
        thisHeight -= thisHeight/10
        thisWidth -= thisWidth/10
      await message.answer(normalize_text(
        f"{mesdict['rus']['reqParamsTexts']['reference']}{message.photo[-1].file_id}\n{mesdict['rus']['reqParamsTexts']['width']}{round(thisWidth)}\n{mesdict['rus']['reqParamsTexts']['height']}{round(thisHeight)}"
        , thisInitReq), reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML)

  @dp.message_handler(content_types=["text"], state=["*"])
  async def textmes(message: types.Message, state: FSMContext):
    if message.chat.type == "private":
      # if message.chat.id not in started:
      #   await message.answer(mesdict['rus']['notStarted'])
      # else:
      data = await state.get_data()

      if message.text == "💵 Подписка 💵":
        transactionNum = randint(0, 100000000)
        subscription = get_subscription(message.chat.id)
        if subscription["status"]:
          await message.answer(f"{mesdict['rus']['subscription']['found']} {subscription['date']}")
        else:
          quickpay = Quickpay(
            receiver = yoomoneyAccount,
            quickpay_form = "shop",
            targets = "Sponsor this project",
            paymentType = "SB",
            sum = subscriptionPrice,
            label = transactionNum
          )
          if subscription["date"] == "none":
            await message.answer(f"{mesdict['rus']['subscription']['notFound']} '{transactionNum}'", reply_markup=generate_pay_keyboard(quickpay.redirected_url, 'rus'))
          else: 
            await message.answer(f"{subscription['date']} {mesdict['rus']['subscription']['foundOld']} '{transactionNum}'", reply_markup=generate_pay_keyboard(quickpay.redirected_url, 'rus'))
      elif message.text == "ℹ️ Помощь ℹ️":
        await message.answer(mesdict['rus']['help']['menu'], parse_mode=types.ParseMode.HTML, reply_markup=keydict["rus"]["help"])
      else: 
        await EditState.null.set()
        thisInitReq = initReq.copy()
        if "defaultModel" in data:
          thisInitReq['model'] = data['defaultModel']
        await message.answer(normalize_text(message.text, thisInitReq), reply_markup=keydict['rus']['request'], parse_mode=types.ParseMode.HTML)

  @dp.callback_query_handler(lambda c: c.data and c.data == "check_pay", state=["*"])
  async def check_pay(call: types.CallbackQuery, state: FSMContext):
    transactionNum = call.message.text
    transactionNum = transactionNum[transactionNum.find("'")+1:]
    transactionNum = transactionNum[:transactionNum.find("'")]
    history = yoomoneyCli.operation_history(label=transactionNum)
    if len(history.operations) != 0:
      add_subscription(call.message.chat.id)
      await call.message.edit_text(mesdict['rus']['payment']['found'])
    else:
      await call.message.answer(mesdict['rus']['payment']['notFound'])
  #endregion message
