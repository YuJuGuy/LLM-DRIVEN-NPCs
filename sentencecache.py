import json

class SentenceCache:
    def __init__(self, filename="sentence_cache.txt"):
        self.filename = filename
        self.cache = []
        self._load_from_file()

    def _save_to_file(self, sentence):
        try:
            # Convert the sentence dictionary to a JSON string
            sentence_str = json.dumps(sentence)

            # Ensure the sentence is only wrapped in brackets if it isn't already
            if not (sentence_str.startswith('{') and sentence_str.endswith('}')):
                sentence_str = f"{{{sentence_str}}}"
                
            with open(self.filename, 'a') as f:
                f.write(sentence_str + '\n')
        except IOError:
            pass

    def _load_from_file(self):
        try:
            with open(self.filename, 'r') as f:
                self.cache = [json.loads(line) for line in f.readlines()]
                return self.cache
        except IOError:
            return []

    def add_sentence(self, sentence, is_frank=False):
        """
        Adds a sentence to the cache, considering word count and removing the oldest sentence if the cache limit is exceeded.

        Args:
          sentence: The sentence to be added (dictionary).
        """
        if is_frank:
            sentence_dict = {"Frank": sentence}
            self.cache.append(sentence_dict)
            self._save_to_file(sentence_dict)
        else:
            self.cache.append(sentence)
            self._save_to_file(sentence)

    def get_cache(self):
            """
            Returns the current list of sentences in the cache, excluding entries where the key contains "tool_call".
            """
            return [entry for entry in self.cache if not any("tool_call" in key for key in entry)]
    def get_last_interactions(self, max_interactions=10):
        """
        Retrieves the last interactions between Frank and the most recent character, including Frank's initial response if it's the last interaction.

        Args:
        max_interactions: The maximum number of interactions to retrieve (integer).

        Returns:
        A list of the last interactions (list).
        """
        interactions = []
        last_character = None
        character_name = None
        tool_call_encountered = False

        # Start from the bottom of the cache
        for entry in reversed(self.cache):
            # Check if the entry is from Frank or tool_call
            if "Frank" in entry or "tool_call" in entry:
                interactions.append(entry)
                if "Frank" in entry:
                    tool_call_encountered = False  # Reset tool_call flag

            # If it's not from Frank or tool_call, check if it's from a different character
            elif last_character is None or last_character in entry:
                last_character = next(iter(entry))
                character_name = last_character
                interactions.append(entry)
                tool_call_encountered = False  # Reset tool_call flag

            # If the character changes, stop adding entries
            elif last_character != next(iter(entry)):
                # Remove entries after encountering a tool_call if the character changes
                if tool_call_encountered:
                    interactions = interactions[:interactions.index({"Frank": "What can I do for you today?"})]
                break

            # Check for tool_call
            if "tool_call" in entry:
                tool_call_encountered = True

            # Break if the maximum number of interactions is reached
            if len(interactions) >= max_interactions:
                break

        # Remove Frank's initial response if it's the last interaction
        if interactions and "Frank" in interactions[-1]:
            interactions.pop()

        return list(reversed(interactions))
