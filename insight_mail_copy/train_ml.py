import os
import django
import gensim
from gensim import corpora

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight_mail.settings')
django.setup()

from analyzer.models import Email
from analyzer.ai_engine import clean_text, MODEL_PATH

def train_lda():
    print("Fetching emails from database...")
    emails = Email.objects.all()
    
    if not emails.exists():
        print("No emails found! Sync some emails first.")
        return

    print(f"Preprocessing {emails.count()} emails...")
    doc_clean = [clean_text(e.subject + " " + e.body) for e in emails]

    # 2. Create Dictionary (ID <-> Word)
    print("Creating Dictionary...")
    dictionary = corpora.Dictionary(doc_clean)
    dictionary.save(os.path.join(MODEL_PATH, 'lda_dict.gensim'))

    # 3. Create Corpus (Document Term Matrix)
    print("Creating Corpus...")
    corpus = [dictionary.doc2bow(text) for text in doc_clean]

    # 4. Train LDA Model
    print("Training LDA Model (Finding 3 Topics)...")
    lda_model = gensim.models.ldamodel.LdaModel(
        corpus, 
        num_topics=3, 
        id2word=dictionary, 
        passes=20
    )
    lda_model.save(os.path.join(MODEL_PATH, 'lda_model.gensim'))

    print("--- Training Complete! ---")
    print("Topics Found:")
    for idx, topic in lda_model.print_topics(-1):
        print(f"Topic: {idx} \nWords: {topic}\n")

if __name__ == "__main__":
    train_lda()