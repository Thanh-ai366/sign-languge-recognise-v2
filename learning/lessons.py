import json

class Lesson:
    def __init__(self, sign, instruction, level="Cơ bản", image_path=None):
        self.sign = sign
        self.instruction = instruction
        self.level = level
        self.image_path = image_path

    def get_instruction(self):
        return self.instruction

    def get_sign(self):
        return self.sign

    def get_image_path(self):
        return self.image_path
    
    def get_level(self):
        return self.level

class LessonManager:
    def __init__(self, lessons_file="learning/lessons_data.json"):
        self.lessons_file = lessons_file
        self.lessons = self.load_lessons()

    def load_lessons(self):
        try:
            with open(self.lessons_file, 'r') as file:
                lessons_data = json.load(file)
                return [Lesson(sign, instruction, level) for level, signs in lessons_data.items() for sign, instruction in signs.items()]
        except FileNotFoundError:
            return []

    def save_lessons(self):
        lessons_data = {}
        for lesson in self.lessons:
            if lesson.get_level() not in lessons_data:
                lessons_data[lesson.get_level()] = {}
            lessons_data[lesson.get_level()][lesson.get_sign()] = lesson.get_instruction()
        
        try:
            with open(self.lessons_file, 'w') as file:
                json.dump(lessons_data, file)
            print("Dữ liệu bài học đã được lưu.")
        except Exception as e:
            print(f"Lỗi khi lưu bài học: {e}")

    def add_lesson(self, sign, instruction, level="Cơ bản", image_path=None):
        lesson = Lesson(sign, instruction, level, image_path)
        self.lessons.append(lesson)
        self.save_lessons()

    def get_lessons_by_level(self, level):
        return [lesson for lesson in self.lessons if lesson.get_level() == level]

    def get_lessons(self):
        return self.lessons

# Sử dụng LessonManager
if __name__ == "__main__":
    lesson_manager = LessonManager()
    lesson_manager.add_lesson("A", "Giơ tay lên và duỗi các ngón tay ra.", "Cơ bản", "images/A.png")
    lesson_manager.add_lesson("B", "Đặt ngón cái và ngón trỏ lại với nhau.", "Cơ bản", "images/B.png")
    lesson_manager.add_lesson("Z", "Xoay cổ tay theo hướng vòng tròn.", "Nâng cao", "images/Z.png")
    
    # Lấy bài học theo cấp độ
    basic_lessons = lesson_manager.get_lessons_by_level("Cơ bản")
    advanced_lessons = lesson_manager.get_lessons_by_level("Nâng cao")

    for lesson in basic_lessons:
        print(f"Cấp độ: {lesson.get_level()} - Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()}")
    
    for lesson in advanced_lessons:
        print(f"Cấp độ: {lesson.get_level()} - Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()}")
