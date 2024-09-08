class Lesson:
    def __init__(self, sign, instruction):
        self.sign = sign
        self.instruction = instruction

    def get_instruction(self):
        return self.instruction

    def get_sign(self):
        return self.sign


class LessonManager:
    def __init__(self):
        self.lessons = []

    def add_lesson(self, sign, instruction):
        lesson = Lesson(sign, instruction)
        self.lessons.append(lesson)

    def get_lessons(self):
        return self.lessons

# Sử dụng LessonManager để tạo các bài học
if __name__ == "__main__":
    lesson_manager = LessonManager()
    lesson_manager.add_lesson("A", "Giơ tay lên và duỗi các ngón tay ra.")
    lesson_manager.add_lesson("B", "Đặt ngón cái và ngón trỏ lại với nhau.")
    lessons = lesson_manager.get_lessons()

    for lesson in lessons:
        print(f"Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()}")
