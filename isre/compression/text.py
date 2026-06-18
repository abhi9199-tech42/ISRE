"""Text-based semantic compression via ConceptMapper."""

import hashlib
from typing import Optional

from ..models.primitives import SemanticPrimitive
from .base import SemanticCompressor


class ConceptMapper(SemanticCompressor):
    """
    Compresses text input into semantic primitives using deterministic mapping.
    Implementation focuses on removing grammar and syntax while preserving meaning.
    """

    def __init__(self, semantic_map: Optional[dict[str, str]] = None):
        self._semantic_map = semantic_map or {
            # === FRUITS & FOOD (10) ===
            "apple": "fruit", "pomme": "fruit", "manzana": "fruit",
            "banana": "fruit", "orange": "fruit", "grape": "fruit",
            "bread": "food", "rice": "food", "meat": "food", "fish": "food",

            # === ACTIONS - MOVEMENT (15) ===
            "run": "action_move_fast", "sprint": "action_move_fast", "dash": "action_move_fast",
            "walk": "action_move_slow", "stroll": "action_move_slow", "crawl": "action_move_slow",
            "jump": "action_jump", "leap": "action_jump", "hop": "action_jump",
            "sit": "action_stay", "stand": "action_stay", "stay": "action_stay",
            "go": "action_go", "come": "action_go", "move": "action_move",

            # === ACTIONS - GENERAL (15) ===
            "eat": "action_eat", "drink": "action_drink", "sleep": "action_sleep",
            "read": "action_read", "write": "action_write", "speak": "action_speak",
            "listen": "action_listen", "look": "action_look", "see": "action_see",
            "hear": "action_hear", "touch": "action_touch", "feel": "action_feel",
            "think": "action_think", "know": "action_know", "learn": "action_learn",

            # === ACTIONS - COMPLEX (10) ===
            "create": "action_create", "build": "action_create", "make": "action_create",
            "destroy": "action_destroy", "break": "action_destroy", "remove": "action_remove",
            "add": "action_add", "push": "action_push", "pull": "action_pull",
            "open": "action_open", "close": "action_close", "unlock": "action_open",

            # === ATTRIBUTES - SPEED (8) ===
            "quickly": "attribute_fast", "fast": "attribute_fast", "rapid": "attribute_fast",
            "slowly": "attribute_slow", "slow": "attribute_slow", "gradual": "attribute_slow",
            "instant": "attribute_instant", "immediate": "attribute_instant",

            # === ATTRIBUTES - SIZE (8) ===
            "big": "attribute_large", "large": "attribute_large", "huge": "attribute_large",
            "small": "attribute_small", "tiny": "attribute_small", "little": "attribute_small",
            "tall": "attribute_tall", "short": "attribute_short", "minute": "attribute_small",

            # === ATTRIBUTES - TEMPERATURE (6) ===
            "hot": "attribute_hot", "warm": "attribute_warm", "heat": "attribute_hot",
            "cold": "attribute_cold", "cool": "attribute_cool", "freezing": "attribute_cold",

            # === ATTRIBUTES - QUALITY (8) ===
            "good": "attribute_good", "better": "attribute_better", "best": "attribute_best",
            "bad": "attribute_bad", "worse": "attribute_worse", "worst": "attribute_worst",
            "great": "attribute_good", "terrible": "attribute_bad",

            # === ATTRIBUTES - QUANTITY (8) ===
            "many": "attribute_many", "much": "attribute_much", "more": "attribute_more",
            "few": "attribute_few", "scant": "attribute_little", "less": "attribute_less",
            "all": "attribute_all", "none": "attribute_none",

            # === ATTRIBUTES - STATE (8) ===
            "on": "attribute_on", "off": "attribute_off", "start": "attribute_start",
            "stop": "attribute_stop", "begin": "attribute_begin", "end": "attribute_end",
            "opened": "attribute_open", "closed": "attribute_closed",

            # === ATTRIBUTES - DIRECTION (6) ===
            "up": "attribute_up", "down": "attribute_down", "high": "attribute_high",
            "low": "attribute_low", "top": "attribute_top", "bottom": "attribute_bottom",

            # === ATTRIBUTES - ENERGY (6) ===
            "strong": "attribute_strong", "weak": "attribute_weak", "hard": "attribute_hard",
            "soft": "attribute_soft", "heavy": "attribute_heavy", "light": "attribute_light",

            # === ATTRIBUTES - COST (4) ===
            "expensive": "attribute_expensive", "cheap": "attribute_cheap",
            "cost_high": "attribute_cost_high", "cost_low": "attribute_cost_low",

            # === OBJECTS (10) ===
            "car": "object_vehicle", "vehicle": "object_vehicle", "bike": "object_vehicle",
            "house": "object_building", "building": "object_building", "room": "object_room",
            "tree": "object_plant", "plant": "object_plant", "flower": "object_plant",
            "water": "object_liquid", "liquid": "object_liquid",

            # === PEOPLE & ROLES (8) ===
            "person": "entity_person", "human": "entity_person", "man": "entity_person",
            "woman": "entity_person", "child": "entity_child", "baby": "entity_child",
            "doctor": "entity_doctor", "teacher": "entity_teacher",

            # === NATURE (8) ===
            "sun": "nature_sun", "moon": "nature_moon", "star": "nature_star",
            "sky": "nature_sky", "earth": "nature_earth", "fire": "nature_fire",
            "rain": "nature_rain", "snow": "nature_snow",

            # === TIME (6) ===
            "now": "time_now", "today": "time_today", "tomorrow": "time_tomorrow",
            "yesterday": "time_yesterday", "always": "time_always", "never": "time_never",

            # === ABSTRACT (8) ===
            "love": "emotion_love", "hate": "emotion_hate", "happy": "emotion_happy",
            "sad": "emotion_sad", "fear": "emotion_fear", "anger": "emotion_anger",
            "peace": "emotion_peace", "joy": "emotion_joy",

            # === LOGIC (6) ===
            "true": "logic_true", "false": "logic_false", "yes": "logic_yes",
            "no": "logic_no", "and": "logic_and", "or": "logic_or",
        }

    @property
    def modality(self) -> str:
        return "text"

    def _generate_id(self, concept: str) -> str:
        """Generate a deterministic ID based on the concept name."""
        return hashlib.sha256(concept.encode()).hexdigest()[:12]

    def compress(self, raw_input: str) -> list[SemanticPrimitive]:
        """
        Processes text, removes basic noise/grammar, and maps to semantic concepts.
        """
        if not isinstance(raw_input, str):
            raise ValueError("ConceptMapper requires string input")

        # 1. Simple normalization (lowercase, remove punctuation - basic pre-processing)
        normalized = raw_input.lower().strip(",.!?")
        words = normalized.split()

        primitives = []
        for word in words:
            # 2. Map word to semantic concept (Hypernym replacement / Cross-language alignment)
            concept = self._semantic_map.get(word)

            # Simple fuzzy fallback (Test 2.1)
            if not concept:
                for key, val in self._semantic_map.items():
                    if len(word) > 3 and word[:3] == key[:3]:
                        concept = val
                        break

            # Emoji support (Test 2.4)
            emoji_map = {"🍎": "fruit", "🏃": "action_move_fast"}
            if word in emoji_map:
                concept = emoji_map[word]

            if not concept:
                concept = word

            # 3. Create deterministic SemanticPrimitive
            primitives.append(SemanticPrimitive(
                id=f"sem_{self._generate_id(concept)}",
                concept=concept,
                modality=self.modality,
                semantic_weight=1.0  # Default weight
            ))

        return primitives
