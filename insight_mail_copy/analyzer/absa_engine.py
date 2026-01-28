import spacy

# Load the small English model (efficient for CPU)
nlp = spacy.load("en_core_web_sm")

class AspectEngine:
    def __init__(self):
        # Define keywords we care about (The "Aspects")
        # You can expand this list based on your specific business
        self.target_aspects = {
            "price": ["cost", "price", "expensive", "bill", "charge", "rate"],
            "support": ["support", "agent", "service", "reply", "wait", "staff"],
            "product": ["app", "website", "login", "feature", "bug", "system", "crash"],
            "delivery": ["shipping", "delivery", "arrive", "tracking", "package"]
        }

    def get_aspect_sentiment(self, text):
        """
        Finds nouns (Aspects) and their linked adjectives (Sentiment).
        Returns: { 'price': 'Negative', 'support': 'Positive' }
        """
        doc = nlp(text.lower())
        results = {}

        # 1. Iterate through every word in the email
        for token in doc:
            
            # 2. Check if the word is an adjective (e.g., "bad", "great", "slow")
            if token.pos_ == "ADJ":
                
                # 3. Find which Noun this adjective describes (Dependency Parsing)
                # 'token.head' gives the word this adjective is attached to
                noun = token.head.text
                
                # 4. Check if this Noun is one of our Target Aspects
                category = self._map_noun_to_category(noun)
                
                if category:
                    # We found a match! (e.g., "expensive" -> linked to -> "price")
                    # Determine polarity of the adjective
                    sentiment = self._get_adj_polarity(token.text)
                    
                    # Store result (Overwrite if multiple, or could list them)
                    results[category] = sentiment

        return results

    def _map_noun_to_category(self, noun):
        """Maps a word like 'bill' to the category 'price'."""
        for category, keywords in self.target_aspects.items():
            if noun in keywords:
                return category
        return None

    def _get_adj_polarity(self, adjective):
        """
        Simple lookup for adjective polarity. 
        In a real app, you could use VADER score here too.
        """
        # Simple hardcoded lists for speed
        pos_words = ["good", "great", "fast", "friendly", "cheap", "easy", "clean", "nice", "excellent"]
        neg_words = ["bad", "slow", "rude", "expensive", "hard", "broken", "dirty", "terrible", "buggy"]
        
        if adjective in pos_words: return "Positive"
        if adjective in neg_words: return "Negative"
        return "Neutral"

# --- Test Block ---
if __name__ == "__main__":
    engine = AspectEngine()
    text = "The support agent was rude, but the delivery was fast."
    print(engine.get_aspect_sentiment(text))
    # Expected Output: {'support': 'Negative', 'delivery': 'Positive'}