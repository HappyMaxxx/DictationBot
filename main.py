import string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

# Оригінальний текст для порівняння
original = """This is a test text for checking accuracy.
It has multiple lines and punctuation!
Let's see how well it works with Telegram messages."""

# Функція порівняння тексту
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

# Ініціалізація бота
TOKEN = "6770873431:AAGAp6w7fRWH0uHT_PY40Ws9x0rvqStclYU"  # Замініть на ваш токен
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обробник команди /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply(
        "Привіт! Надішли мені текст, і я порівняю його з оригіналом:\n\n" + original
    )

# Обробник текстових повідомлень
@dp.message()
async def handle_text(message: Message):
    entered_text = message.text
    # Перевірка, чи це не команда
    if not entered_text.startswith('/'):
        accuracy = check_accuracy(original, entered_text)
        await message.reply(f"Твоя точність: {accuracy:.2f}%")

# Запуск бота
async def main():
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())