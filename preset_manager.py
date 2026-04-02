import os
import json
import shutil
import sys

class PresetManager:
    def __init__(self, app_dir):
        self.app_dir = app_dir
        self.presets_dir = os.path.join(app_dir, "presets")
        self.user_data_dir = os.path.join(app_dir, "user_data")
        os.makedirs(self.presets_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
        self.presets_file = os.path.join(self.presets_dir, "presets.json")
        self.presets = self.load_presets()
        if not self.presets:
            self.create_default_preset()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_presets(self):
        if os.path.exists(self.presets_file):
            with open(self.presets_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_presets(self):
        with open(self.presets_file, 'w', encoding='utf-8') as f:
            json.dump(self.presets, f, indent=2, ensure_ascii=False)

    def add_preset(self, preset):
        self.presets.append(preset)
        self.save_presets()

    def remove_preset(self, index):
        if 0 <= index < len(self.presets):
            preset = self.presets[index]
            preset_folder = os.path.join(self.user_data_dir, preset.get("name", ""))
            if os.path.exists(preset_folder):
                shutil.rmtree(preset_folder)
            del self.presets[index]
            self.save_presets()

    def get_preset(self, index):
        return self.presets[index] if 0 <= index < len(self.presets) else None

    def copy_images_to_preset(self, preset_name, hall_name, level_idx, img_list):
        preset_folder = os.path.join(self.user_data_dir, preset_name, hall_name, f"level_{level_idx}")
        os.makedirs(preset_folder, exist_ok=True)
        new_paths = []
        for img_idx, src in enumerate(img_list):
            if src and os.path.exists(src):
                dst = os.path.join(preset_folder, f"img_{img_idx+1}.png")
                # Нормализуем пути для сравнения
                if os.path.normpath(src) == os.path.normpath(dst):
                    # Исходный и целевой файлы совпадают – пропускаем копирование
                    new_paths.append(src)
                    print(f"Skipping copy, same file: {src}")
                else:
                    try:
                        shutil.copy2(src, dst)
                        new_paths.append(dst)
                        print(f"Copied {src} -> {dst}")
                    except Exception as e:
                        print(f"Error copying {src} to {dst}: {e}")
                        new_paths.append(src)  # оставляем исходный путь
            else:
                print(f"Source file not found: {src}")
                new_paths.append("")
        return new_paths

    def create_default_preset(self):
        from constants import HALLS, ALL_HALLS

        default_preset_name = "Стандартный"
        default_images_root = self.resource_path("default_preset_images")

        if not os.path.exists(default_images_root):
            print(f"Папка с дефолтными изображениями не найдена: {default_images_root}")
            return

        halls_data = {}
        for hall_name in ALL_HALLS:
            hall_path = os.path.join(default_images_root, hall_name)
            if not os.path.exists(hall_path):
                continue
            levels = HALLS[hall_name]
            level_paths = []
            correct_answers = []
            for lvl in range(1, levels + 1):
                level_folder = os.path.join(hall_path, f"level_{lvl}")
                if not os.path.exists(level_folder):
                    break
                images = sorted([os.path.join(level_folder, f) for f in os.listdir(level_folder)
                                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
                if not images:
                    break
                level_paths.append(images)
                if hall_name == "Зал внимания (Найди лишний)":
                    if lvl == 1:
                        correct_answers.append(0)
                    elif lvl == 2:
                        correct_answers.append(1)
                    elif lvl == 3:
                        correct_answers.append(1)
                    else:
                        correct_answers.append(len(images)-1)
                else:
                    correct_answers.append(len(images)-1)
            if len(level_paths) == levels:
                halls_data[hall_name] = {
                    "levels": level_paths,
                    "correct_answers": correct_answers
                }

        if not halls_data:
            print("Не удалось загрузить дефолтные изображения для создания пресета.")
            return

        for hall_name, hall_data in halls_data.items():
            for level_idx, img_list in enumerate(hall_data["levels"]):
                new_paths = self.copy_images_to_preset(default_preset_name, hall_name, level_idx+1, img_list)
                hall_data["levels"][level_idx] = new_paths

        preset = {
            "name": default_preset_name,
            "halls": halls_data
        }

        self.add_preset(preset)
        print(f"Дефолтный пресет «{default_preset_name}» успешно создан.")