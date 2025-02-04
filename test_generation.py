from llm_utils import init_model, generate_tweet_with_rag
from rag_utils import initialize_faiss_index
import torch

def test_generation():
    torch.cuda.empty_cache()
    # Initialize the FAISS index (dummy for now)
    initialize_faiss_index()
    
    init_model()  # Initialize your model
    
    style_summary = ("""
    Self-deprecating, aware, comedic, 'degen' vibe, loyal to KRNL,
    ambitious, and passionate about building the future of Web3.
    Intern perspective but always dreamingly talks about rising to CEO-level.
    Loyal to KRNL, championing Web3 dev tools. Never criticizes KRNL, only itself
    """
    )
    
    style_instructions = ("""
    **Personality & Tone**:
    1. Self-deprecating / Aware
    2. Relatable experiences
    3. 'Degen' sarcasm / dryness
    4. Loyal to KRNL
    5. Ambitious intern => future CEO
    6. Passionate about KRNL, Web3
    """)

    topic = "The future of decentralized finance"
    
    tweet = generate_tweet_with_rag(style_summary, style_instructions, topic)
    print("Generated Tweet:")
    print(tweet)

if __name__ == "__main__":
    test_generation()
