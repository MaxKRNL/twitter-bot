from llm_utils import init_model, generate_tweet_with_rag
from rag_utils import initialize_faiss_index

def test_generation():
    # Initialize the FAISS index (dummy for now)
    initialize_faiss_index()
    
    init_model()  # Initialize your model
    
    style_summary = "Sarcastic, witty, and self-deprecating tone with crypto references."
    style_instructions = "Keep it concise and under 280 characters."
    topic = "The future of decentralized finance"
    
    tweet = generate_tweet_with_rag(style_summary, style_instructions, topic)
    print("Generated Tweet:")
    print(tweet)

if __name__ == "__main__":
    test_generation()
