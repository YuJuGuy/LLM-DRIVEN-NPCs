
class ReflectionManager:
    def __init__(self, file_path='reflection.txt'):
        self.file_path = file_path
        self.reflections = self.load_reflections()

    def load_reflections(self):
        reflections = {}
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    number, text = line.strip().split(' ', 1)
                    reflections[int(number)] = text
        except FileNotFoundError:
            pass  # If the file doesn't exist, we'll start with an empty dictionary
        return reflections

    def save_reflections(self):
        with open(self.file_path, 'w') as file:
            for number, text in self.reflections.items():
                file.write(f'{number} {text}\n')

    def add_reflection(self, text):
        new_number = max(self.reflections.keys(), default=0) + 1
        self.reflections[new_number] = text
        self.save_reflections()
        return "Reflection added successfully."

    def edit_reflection(self, number, new_text):
        if number in self.reflections:
            self.reflections[number] = new_text
            self.save_reflections()
        else:
            raise KeyError(f'Reflection number {number} not found.')
        return "Reflection edited successfully."

    def delete_reflection(self, number):
        if number in self.reflections:
            del self.reflections[number]
            self.save_reflections()
        else:
            raise KeyError(f'Reflection number {number} not found.')
        return "Reflection deleted successfully."

    def get_reflections(self):
        return self.reflections


