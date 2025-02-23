from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey 
from src.keyboards.keyboards import get_verse_keyboard, get_confirm_keyboard, get_room_management_keyboard
from src.models.models import rooms, admins, shevchenko_poems
import random
import string

router = Router()

dp = None 

class RoomState(StatesGroup):
    selecting_verse = State()
    ready_to_confirm = State()

def check_accuracy(original, entered_text):
    def clean_text(text):
        text = text.replace('\n', ' ').strip()
        return text.lower().split()
    
    def remove_punctuation(word):
        translator = str.maketrans("", "", string.punctuation)
        return word.translate(translator)
    
    def has_punctuation(word):
        return any(char in string.punctuation for char in word)
    
    def word_similarity(orig_word, entered_word):
        orig_no_punct = remove_punctuation(orig_word)
        entered_no_punct = remove_punctuation(entered_word)
        
        if not orig_no_punct or not entered_no_punct:
            return 0
        
        min_len = min(len(orig_no_punct), len(entered_no_punct))
        matches = sum(1 for i in range(min_len) if orig_no_punct[i] == entered_no_punct[i])
        return matches / len(orig_no_punct)
    
    def compare_texts(original_words, entered_words):
        total_words = len(original_words)
        
        if not entered_words:
            return 0
        
        similarity_matrix = []
        for orig in original_words:
            row = [word_similarity(orig, entered) for entered in entered_words]
            similarity_matrix.append(row)
        
        used_entered = set()
        word_scores = 0
        punctuation_penalty = 0
        
        for i in range(len(original_words)):
            max_similarity = 0
            best_j = -1
            for j in range(len(entered_words)):
                if j not in used_entered and similarity_matrix[i][j] > max_similarity:
                    max_similarity = similarity_matrix[i][j]
                    best_j = j
            if best_j != -1:
                word_scores += max_similarity
                used_entered.add(best_j)
                if max_similarity > 0:
                    if has_punctuation(original_words[i]) and not has_punctuation(entered_words[best_j]):
                        punctuation_penalty += 1
                    elif not has_punctuation(original_words[i]) and has_punctuation(entered_words[best_j]):
                        punctuation_penalty += 1
        
        base_accuracy = (word_scores / total_words) * 100 if total_words > 0 else 0
        punctuation_factor = (punctuation_penalty / total_words) * 20 if total_words > 0 else 0
        total_accuracy = max(0, base_accuracy - punctuation_factor)
        
        return total_accuracy
    
    cleaned_original = clean_text(original)
    cleaned_entered_text = clean_text(entered_text)
    accuracy_percentage = compare_texts(cleaned_original, cleaned_entered_text)
    
    return accuracy_percentage

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id

    if not admins:
        admins.add(user_id)

    if user_id in admins:
        keyboard = get_verse_keyboard()
        await message.reply("Вітаю! Обери вірш, щоб почати нову гру:", reply_markup=keyboard)
    else:
        await message.reply("Вітаю! Введіть номер кімнати, щоб приєднатися.")

@router.callback_query()
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    data = callback_query.data

    if user_id not in admins:
        await callback_query.answer("Ви не адміністратор!")
        return

    if data.startswith('verse_'):
        verse_number = int(data.split('_')[1])
        await state.update_data(selected_verse=verse_number)

        keyboard = get_confirm_keyboard()
        poem_text = shevchenko_poems.get(verse_number, "Вірш не знайдено")
        await callback_query.message.edit_text(
            f"Адміністратор вибрав вірш №{verse_number}:\n\n{poem_text}\n\nПідтвердьте, щоб створити кімнату.",
            reply_markup=keyboard
        )

    elif data == 'confirm_room':
        user_data = await state.get_data()
        if 'selected_verse' not in user_data:
            await callback_query.answer("Спочатку оберіть вірш!")
            return

        room_number = str(random.randint(100, 999))
        selected_verse = user_data['selected_verse']
        poem_text = shevchenko_poems.get(selected_verse, "Вірш не знайдено")

        rooms[room_number] = {
            'admin': user_id,
            'users': [],
            'verse': poem_text,
            'verse_number': selected_verse,
            'closed': False,
            'finished': False,
            'submissions': {}
        }

        await state.update_data(room_number=room_number)
        keyboard = get_room_management_keyboard(room_number)
        await callback_query.message.edit_text(
            f"✅ Кімната {room_number} для вірша №{selected_verse} створена!\n\n{poem_text}\n\nОчікую користувачів...",
            reply_markup=keyboard
        )
    
    elif data == 'cancel_room':
        await state.clear()
        keyboard = get_verse_keyboard()
        await callback_query.message.edit_text(
            "Вибір скасовано. Обери вірш:",
            reply_markup=keyboard
        )

    elif data == 'toggle_room':
        user_data = await state.get_data()
        room_number = user_data.get('room_number')
        
        if not room_number or room_number not in rooms:
            await callback_query.answer("Кімната не знайдена!")
            return

        rooms[room_number]['closed'] = not rooms[room_number]['closed']
        poem_text = rooms[room_number]['verse']
        status_text = (
            f"🚪 Кімната {room_number} закрита!\n\n{poem_text}\n\nНіхто більше не може приєднатися."
            if rooms[room_number]['closed']
            else f"🔓 Кімната {room_number} відкрита!\n\n{poem_text}\n\nНові учасники можуть приєднатися."
        )

        await callback_query.message.edit_text(
            status_text,
            reply_markup=get_room_management_keyboard(room_number)
        )

    elif data == 'finish_dictation':
        user_data = await state.get_data()
        room_number = user_data.get('room_number')
        if not room_number or room_number not in rooms:
            await callback_query.answer("Кімната не знайдена!")
            return

        rooms[room_number]['finished'] = True
        original_poem = rooms[room_number]['verse']

        bot_id = callback_query.bot.id 
        player_ratings = []
        for user_id in rooms[room_number]['users']:
            entered_text = rooms[room_number]['submissions'].get(user_id, "")
            accuracy = check_accuracy(original_poem, entered_text) if entered_text else 0
            user_name = (await callback_query.bot.get_chat(user_id)).full_name
            player_ratings.append((user_name, accuracy))

            # Повідомлення користувачу
            await callback_query.bot.send_message(
                user_id,
                f"⏹ Диктант у кімнаті {room_number} завершено!\n\n"
                f"Твоя точність: {accuracy:.2f}%\n\n"
                "Тепер ти можеш приєднатися до нової кімнати!"
            )

            key = StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id)
            user_state = FSMContext(storage=dp.storage, key=key)
            await user_state.clear()

        player_ratings.sort(key=lambda x: x[1], reverse=True)

        rating_text = f"Гра в кімнаті {room_number} завершена!\n\n🏆 Рейтинг гравців:\n"
        for i, (player_name, accuracy) in enumerate(player_ratings, start=1):
            rating_text += f"{i}. {player_name} — {accuracy:.2f}%\n"


        await callback_query.message.edit_text(f"Гра в кімнаті {room_number} завершена!")
        for user_id in rooms[room_number]['users']:
            await callback_query.bot.send_message(user_id, rating_text)
        await callback_query.message.answer(rating_text)

        del rooms[room_number]
        await state.clear()

        await callback_query.message.answer("Оберіть вірш, щоб почати нову гру:", reply_markup=get_verse_keyboard())

    await callback_query.answer()
