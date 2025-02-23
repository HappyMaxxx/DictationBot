from aiogram import Router, types
from src.models.models import rooms, admins
from aiogram.fsm.context import FSMContext
import re

router = Router()

@router.message(lambda message: re.fullmatch(r"\d{3}", message.text))
async def join_room(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    room_number = message.text

    for existing_room, details in rooms.items():
        if details['admin'] == user_id:
            await message.reply("❌ Ви вже створили кімнату і не можете приєднатися до іншої!")
            return

    user_data = await state.get_data()
    if 'room_number' in user_data and user_data['room_number'] in rooms:
        await message.reply("❌ Ви вже перебуваєте в іншій кімнаті і не можете приєднатися до нової!")
        return

    if room_number not in rooms:
        await message.reply("❌ Такої кімнати не існує!")
        return

    if rooms[room_number]['closed']:
        await message.reply("🚪 Кімната вже закрита, ви не можете приєднатися.")
        return

    if user_id in rooms[room_number]['users']:
        await message.reply("ℹ Ви вже в цій кімнаті!")
        return

    # Додаємо користувача в кімнату
    rooms[room_number]['users'].append(user_id)
    
    # Зберігаємо номер кімнати у стан
    await state.update_data(room_number=room_number)

    await message.reply(f"✅ Ви приєдналися до кімнати {room_number}!")

    # Повідомлення адміністратору
    admin_id = rooms[room_number]['admin']
    await message.bot.send_message(admin_id, f"👤 Користувач {user_name} приєднався до кімнати {room_number}.")

@router.message()
async def handle_user_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = await state.get_data()
    room_number = user_data.get('room_number')

    if not room_number or room_number not in rooms:
        await message.answer("❌ Ви не перебуваєте в жодній кімнаті!")
        return

    if user_id not in rooms[room_number]['users']:
        await message.answer("❌ Ви не є учасником цієї кімнати!")
        return

    if not rooms[room_number]['closed']:
        await message.answer("🔒 Диктант ще не розпочався! Очікуйте на закриття кімнати.")
        return

    if rooms[room_number]['finished']:
        await message.answer("⏹ Диктант завершено, ви більше не можете писати вірші.")
        return

    if user_id in rooms[room_number]['submissions']:
        await message.answer("⚠ Ваш вірш на перевірці, зачекайте.")
        return

    temp_message = await message.reply(f"📝 Ваш вірш:\n\n{message.text}")
    rooms[room_number]['submissions'][user_id] = message.text
    await message.bot.edit_message_text(
        text="🔒 Вірш прийнято і відправлено на перевірку.",
        chat_id=message.chat.id,
        message_id=temp_message.message_id
    )

    admin_id = rooms[room_number]['admin']
    await message.bot.send_message(
        admin_id,
        f"👤 Користувач {message.from_user.full_name} відправив вірш у кімнаті {room_number}:\n\n{message.text}"
    )