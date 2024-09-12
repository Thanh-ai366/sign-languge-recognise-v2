class Lesson:
    def __init__(self, sign, instruction, image_path=None):
        self.sign = sign
        self.instruction = instruction
        self.image_path = image_path

    def get_instruction(self):
        return self.instruction

    def get_sign(self):
        return self.sign

    def get_image_path(self):
        return self.image_path


class LessonManager:
    def __init__(self):
        self.lessons = []

    def add_lesson(self, sign, instruction, image_path=None):
        lesson = Lesson(sign, instruction, image_path)
        self.lessons.append(lesson)

    def get_lessons(self):
        return self.lessons

# Sử dụng LessonManager để tạo các bài học
if __name__ == "__main__":
    lesson_manager = LessonManager()
    lesson_manager.add_lesson("A", "Giơ tay lên và duỗi các ngón tay ra.", "images/A.png")
    lesson_manager.add_lesson("B", "Đặt ngón cái và ngón trỏ lại với nhau.", "images/B.png")
    
    lessons = lesson_manager.get_lessons()

    for lesson in lessons:
        print(f"Ký hiệu: {lesson.get_sign()} - Hướng dẫn: {lesson.get_instruction()} - Hình ảnh: {lesson.get_image_path()}")
