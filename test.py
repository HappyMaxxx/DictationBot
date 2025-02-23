import string

def check_accuracy(original, entered_text):
    def clean_text(text):
        # Розбиваємо на слова, зберігаючи пунктуацію, враховуючи багатостроковість
        # Замінюємо переноси рядків на пробіли та розбиваємо на слова
        text = text.replace('\n', ' ').strip()
        return text.lower().split()
    
    def remove_punctuation(word):
        # Видаляємо пунктуацію для базового порівняння слова
        translator = str.maketrans("", "", string.punctuation)
        return word.translate(translator)
    
    def has_punctuation(word):
        # Перевіряємо, чи є в слові пунктуація
        return any(char in string.punctuation for char in word)
    
    def word_similarity(orig_word, entered_word):
        # Обчислюємо схожість між двома словами (відсоток збігу символів)
        orig_no_punct = remove_punctuation(orig_word)
        entered_no_punct = remove_punctuation(entered_word)
        
        if not orig_no_punct or not entered_no_punct:
            return 0
        
        min_len = min(len(orig_no_punct), len(entered_no_punct))
        matches = sum(1 for i in range(min_len) if orig_no_punct[i] == entered_no_punct[i])
        return matches / len(orig_no_punct)
    
    def compare_texts(original_words, entered_words):
        total_words = len(original_words)  # Кількість слів в оригіналі
        
        if not entered_words:
            return 0
        
        # Створюємо матрицю схожості між усіма словами
        similarity_matrix = []
        for orig in original_words:
            row = [word_similarity(orig, entered) for entered in entered_words]
            similarity_matrix.append(row)
        
        # Знаходимо найкращі збіги (максимальна схожість для кожного слова)
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
                # Штраф за пунктуацію, якщо є схожість
                if max_similarity > 0:
                    if has_punctuation(original_words[i]) and not has_punctuation(entered_words[best_j]):
                        punctuation_penalty += 1
                    elif not has_punctuation(original_words[i]) and has_punctuation(entered_words[best_j]):
                        punctuation_penalty += 1
        
        # Обчислюємо базову точність
        base_accuracy = (word_scores / total_words) * 100 if total_words > 0 else 0
        
        # Штраф за неправильну пунктуацію (максимум 20%)
        punctuation_factor = (punctuation_penalty / total_words) * 20 if total_words > 0 else 0
        total_accuracy = max(0, base_accuracy - punctuation_factor)
        
        return total_accuracy
    
    # Очищаємо тексти
    cleaned_original = clean_text(original)
    cleaned_entered_text = clean_text(entered_text)
    
    # Обчислюємо точність
    accuracy_percentage = compare_texts(cleaned_original, cleaned_entered_text)
    
    return accuracy_percentage

# Приклад багатострокового оригінального тексту
original = """This is a test text for checking accuracy.
It has multiple lines and punctuation!
Let's see how well it works with Telegram messages."""

print("Original text:")
print(original)
print("\nEnter your text below (press Ctrl+D or Ctrl+Z and Enter when finished):")

while True:
    try:
        lines = []
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        entered_text = '\n'.join(lines)
        accuracy = check_accuracy(original, entered_text)
        print(f"\nYour accuracy: {accuracy:.2f}%")
        break