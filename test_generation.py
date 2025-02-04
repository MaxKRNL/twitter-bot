from llm_utils import init_model, generate_tweet_with_rag

def test_generation():
    init_model()  # Initialize your model
    style_summary = "Sarcastic, witty, and self-deprecating tone with crypto references."
    style_instructions = "Keep it concise and under 280 characters."
    topic = "The future of decentralized finance"
    
    tweet = generate_tweet_with_rag(style_summary, style_instructions, topic)
    print("Generated Tweet:")
    print(tweet)

if __name__ == "__main__":
    test_generation()
