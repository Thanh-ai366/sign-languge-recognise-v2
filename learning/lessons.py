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
    def __init__(self):
        self.lessons = []

    def add_lesson(self, sign, instruction, level="Cơ bản", image_path=None):
        lesson = Lesson(sign, instruction, level, image_path)
        self.lessons.append(lesson)

    def get_lessons_by_level(self, level):
        return [lesson for lesson in self.lessons if lesson.get_level() == level]

    def get_lessons(self):
        return self.lessons

# Sử dụng LessonManager để tạo các bài học với nhiều cấp độ
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
