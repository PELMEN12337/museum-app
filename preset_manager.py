import os
import json
import shutil
import sys

class PresetManager:
    def __init__(self, app_dir=None):
        if app_dir is None:
            if sys.platform == "win32":
                app_data = os.environ.get("APPDATA", os.path.expanduser("~"))
                app_dir = os.path.join(app_data, "MuseumApp")
            else:
                app_dir = os.path.expanduser("~/.museumapp")
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

    # ---------- Обычные залы (список изображений) ----------
    def copy_images_to_preset(self, preset_name, hall_name, level_idx, img_list):
        preset_folder = os.path.join(self.user_data_dir, preset_name, hall_name, f"level_{level_idx}")
        os.makedirs(preset_folder, exist_ok=True)
        new_paths = []
        for img_idx, src in enumerate(img_list):
            if src and os.path.exists(src):
                dst = os.path.join(preset_folder, f"img_{img_idx+1}.png")
                if os.path.normpath(src) == os.path.normpath(dst):
                    new_paths.append(src)
                else:
                    shutil.copy2(src, dst)
                    new_paths.append(dst)
            else:
                print(f"Source file not found: {src}")
                new_paths.append("")
        return new_paths

    # ---------- Зал мастера (основная картинка + 8 цветов) ----------
    def copy_master_images_to_preset(self, preset_name, hall_name, level_idx, level_dict):
        """Копирует основную картинку и цвета для уровня зала мастера."""
        level_folder = os.path.join(self.user_data_dir, preset_name, hall_name, f"level_{level_idx}")
        os.makedirs(level_folder, exist_ok=True)
        new_level = {}

        # Основная картинка
        main_src = level_dict.get("main_image", "")
        if main_src and os.path.exists(main_src):
            dst = os.path.join(level_folder, "main.png")
            if os.path.normpath(main_src) == os.path.normpath(dst):
                new_level["main_image"] = main_src
            else:
                shutil.copy2(main_src, dst)
                new_level["main_image"] = dst
        else:
            new_level["main_image"] = ""

        # Цвета (8 штук)
        new_colors = []
        for i, src in enumerate(level_dict.get("color_images", [])):
            if src and os.path.exists(src):
                dst = os.path.join(level_folder, f"color_{i+1}.png")
                if os.path.normpath(src) == os.path.normpath(dst):
                    new_colors.append(src)
                else:
                    shutil.copy2(src, dst)
                    new_colors.append(dst)
            else:
                new_colors.append("")
        new_level["color_images"] = new_colors
        new_level["correct_indices"] = level_dict.get("correct_indices", [])
        return new_level

    # ---------- Создание стандартного пресета ----------
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

            if hall_name == "Зал мастера (Подбери цвета по картинке)":
                # Особый формат: для каждого уровня – словарь
                for lvl in range(1, levels + 1):
                    level_folder = os.path.join(hall_path, f"level_{lvl}")
                    if not os.path.exists(level_folder):
                        break
                    main_img = os.path.join(level_folder, "main.png")
                    color_imgs = [os.path.join(level_folder, f"color_{i}.png") for i in range(1, 9)]
                    level_dict = {
                        "main_image": main_img,
                        "color_images": color_imgs,
                        "correct_indices": [0, 1, 2, 3]  # пример: первые 4 цвета правильные
                    }
                    level_paths.append(level_dict)
                    correct_answers.append(0)  # не используется
            else:
                # Обычные залы: список путей к изображениям
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

        # Копируем изображения в папку user_data
        for hall_name, hall_data in halls_data.items():
            if hall_name == "Зал мастера (Подбери цвета по картинке)":
                for level_idx, level_dict in enumerate(hall_data["levels"]):
                    new_level = self.copy_master_images_to_preset(default_preset_name, hall_name, level_idx+1, level_dict)
                    hall_data["levels"][level_idx] = new_level
            else:
                for level_idx, img_list in enumerate(hall_data["levels"]):
                    new_paths = self.copy_images_to_preset(default_preset_name, hall_name, level_idx+1, img_list)
                    hall_data["levels"][level_idx] = new_paths

        preset = {
            "name": default_preset_name,
            "halls": halls_data
        }

        self.add_preset(preset)
        print(f"Дефолтный пресет «{default_preset_name}» успешно создан в {self.app_dir}")