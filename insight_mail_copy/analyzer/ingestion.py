import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import gensim
from gensim import corpora

# --- 1. Setup NLTK Resources ---
# We need these for cleaning and VADER as per the methodology [cite: 901, 937]
nltk.download('stopwords')
nltk.download('vader_lexicon')
nltk.download('punkt')

class Phase1Ingestion:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.vader = SentimentIntensityAnalyzer()
        self.lda_model = None
        self.dictionary = None

    # --- Preprocessing Logic [cite: 897, 901, 904] ---
    def clean_text(self, text):
        """
        Removes HTML, special chars, and stop words.
        """
        if not isinstance(text, str):
            return ""
        
        # 1. Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        # 2. Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # 3. Convert to lowercase
        text = text.lower()
        # 4. Remove Stop Words & Tokenize
        tokens = [word for word in text.split() if word not in self.stop_words and len(word) > 2]
        
        return tokens

    # --- Sentiment Labeling (VADER) [cite: 937, 948] ---
    def get_vader_label(self, text):
        """
        Assigns a baseline sentiment score (-1 to 1).
        """
        if not isinstance(text, str):
            return 0.0
        
        # VADER gives a 'compound' score
        score = self.vader.polarity_scores(text)['compound']
        return score

    # --- Topic Labeling (LDA) [cite: 916, 920, 935] ---
    def train_lda_and_label(self, df, num_topics=3):
        """
        Trains LDA on the current batch of emails to discover topics.
        """
        # Prepare data for Gensim
        # The 'clean_tokens' column is needed for LDA
        processed_docs = df['clean_tokens'].tolist()
        
        # Create Dictionary (ID to Word mapping)
        self.dictionary = corpora.Dictionary(processed_docs)
        
        # Create Corpus (Term Frequency)
        corpus = [self.dictionary.doc2bow(text) for text in processed_docs]
        
        # Train LDA Model
        print(f"Training LDA model to find {num_topics} hidden topics...")
        self.lda_model = gensim.models.LdaModel(
            corpus, num_topics=num_topics, id2word=self.dictionary, passes=10
        )
        
        # Assign Dominant Topic to each email
        topics = []
        for doc_bow in corpus:
            # Get topic probabilities
            topic_probs = self.lda_model.get_document_topics(doc_bow)
            # Sort to find the dominant topic
            dominant_topic = sorted(topic_probs, key=lambda x: x[1], reverse=True)[0][0]
            topics.append(dominant_topic)
            
        return topics

    def get_topic_keywords(self):
        """Helper to see what the topics actually are"""
        return self.lda_model.print_topics()

# --- Execution Simulation ---
if __name__ == "__main__":
    # 1. Load Dummy Data (Simulating your raw email stream)
    data = {
        'thread_id': [101, 102, 103, 104, 105],
        'body': [
            "Subject: Pricing. The cost of this subscription is too high. I want a refund.",
            "Subject: Bug. I cannot login to the system. It keeps crashing.",
            "Subject: Thanks. The support team was very helpful and solved my issue.",
            "Subject: Inquiry. Do you have a feature for exporting data to PDF?",
            "Subject: Angry. This service is terrible, I am canceling my account immediately!"
        ]
    }
    df = pd.DataFrame(data)

    # 2. Initialize Engine
    engine = Phase1Ingestion()

    # 3. Apply Cleaning
    print("--- Cleaning Data ---")
    df['clean_tokens'] = df['body'].apply(engine.clean_text)
    
    # 4. Apply VADER (Sentiment)
    print("--- Applying VADER Sentiment ---")
    df['sentiment_score'] = df['body'].apply(engine.get_vader_label)

    # 5. Apply LDA (Topics)
    print("--- Applying LDA Topic Modeling ---")
    df['topic_id'] = engine.train_lda_and_label(df, num_topics=3)

    # 6. Show Result (The "Ground Truth" DataFrame)
    print("\n--- PHASE 1 OUTPUT: Labeled Dataset ---")
    print(df[['thread_id', 'sentiment_score', 'topic_id', 'body']])
    
    print("\n--- Discovered Topics (Keywords) ---")
    for idx, topic in engine.get_topic_keywords():
        print(f"Topic {idx}: {topic}")