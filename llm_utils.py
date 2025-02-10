import textwrap
import torch
import re
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)
from rag_utils import retrieve_context

# Global pipeline for reuse
generation_pipeline = None

def init_model(model_name: str = "meta-llama/Llama-3.1-8B-Instruct"):
    """
    Initializes a quantized Llama-based model for text generation.
    """
    global generation_pipeline

    # BitsAndBytes config to load in 8-bit with CPU offloading
    quant_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_enable_fp32_cpu_offload=True
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=quant_config,
        device_map="balanced",
        offload_folder="offload",
        offload_state_dict=True
    )

    # Create pipeline
    generation_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        temperature=0.8,
        top_p=0.9,
        repetition_penalty=1.1,
        max_new_tokens=80,
        eos_token_id=tokenizer.eos_token_id,
        # early_stopping=True,
        num_return_sequences=1,
    )

# ----------------------------------------------------------------
# PROMPT BUILDING
# ----------------------------------------------------------------
def build_rag_prompt(
    style_summary: str,
    style_instructions: str,
    # backstory: str,
    user_topic_or_query: str,
    retrieved_context: str
) -> str:
    """
    Build a single prompt that ALWAYS includes retrieved context,
    telling the LLM to use it IF relevant, or ignore if not.
    """
    prompt = f"""
    You are a Twitter content generator.

    Your style summary:
    {style_summary}

    Additional style instructions and examples:
    {style_instructions}

    You also have the following context from our knowledge base:
    {retrieved_context}

    Instructions:
    - If the provided context is relevant to "{user_topic_or_query}", you may incorporate it.
    - If the context is not relevant, ignore it.

    Task:
    Write a single tweet (under 280 characters) about: "{user_topic_or_query}".
    After finishing the tweet, write "Total Character used: " followed by the number of characters in your tweet.

    Constraints:
    - Do NOT quote these style instructions verbatim.
    - Do NOT use any Hashtags.
    - The tweet must be under 280 characters (including spaces).

    Now, provide ONLY the tweet:
    """
    return textwrap.dedent(prompt).strip()

# ----------------------------------------------------------------
# CLEANUP & POST-PROCESS
# ----------------------------------------------------------------
def remove_filler_phrases(text: str) -> str:
    """
    Removes known filler phrases or disclaimers after the actual tweet.
    """
    filler_phrases = [
        "Let me know if this meets the requirement",
        "Hope that helps",
        "Is there anything else",
        "If you need more help",
        "Feel free to ask more",
        "Certainly, here is the tweet",
        "Sure, here's a tweet"
    ]
    for phrase in filler_phrases:
        if phrase in text:
            text = text.split(phrase)[0].strip()
    return text

def clean_model_output(text: str) -> str:
    """
    Removes instruction echoes, disclaimers, and anything after 'Total Character used:'.
    """
    # Remove repeated instructions or prompt echoes
    if "Now, provide ONLY the tweet:" in text:
        text = text.split("Now, provide ONLY the tweet:")[-1].strip()
    elif "Now, provide ONLY the tweet" in text:
        text = text.split("Now, provide ONLY the tweet")[-1].strip()

    for marker in ["Task:", "Constraints:", "You are a Twitter content generator", "Instructions:"]:
        if marker in text:
            text = text.split(marker)[0].strip()

    # Truncate after "Total Character used:"
    if "Total Character used:" in text:
        text = text.split("Total Character used:")[0].strip()

    return text.strip()

def final_cleanup(text: str) -> str:
    """
    Removes leftover tokens, repeated punctuation, etc.
    Ensures we end up with a clean tweet.
    """
    # Remove special tokens
    text = re.sub(r"</s>", "", text)
    # Collapse extra whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove repeated punctuation sequences
    text = re.sub(r"[)\-:;.,]{2,}", "", text)
    # Strip any leading/trailing quotes or whitespace
    text = text.strip(" \"\n")
    return text

# ----------------------------------------------------------------
# RAG-BASED GENERATION
# ----------------------------------------------------------------
def generate_tweet_with_rag(
    style_summary: str,
    style_instructions: str,
    topic_or_query: str,
    top_k: int = 3
) -> str:
    """
    Always retrieves top_k chunks from FAISS, includes them in a single prompt.
    The LLM is told to use them ONLY if relevant.
    """
    global generation_pipeline
    if generation_pipeline is None:
        raise ValueError("Pipeline not initialized. Call init_model() first.")

    # 1) Retrieve top_k context
    results = retrieve_context(topic_or_query, top_k=top_k)
    # Combine into a single string
    rag_text = "\n\n".join([f"Context chunk:\n{chunk}" for (chunk, score) in results])

    # 2) Build the prompt
    prompt = build_rag_prompt(style_summary, style_instructions, topic_or_query, rag_text)

    # 3) Generate
    outputs = generation_pipeline(prompt, num_return_sequences=1)
    tweet_candidate = outputs[0]["generated_text"]

    # 4) Post-process
    tweet_candidate = clean_model_output(tweet_candidate)
    tweet_candidate = remove_filler_phrases(tweet_candidate)
    tweet_candidate = final_cleanup(tweet_candidate)

    # 5) Enforce 280-char limit
    if len(tweet_candidate) > 280:
        tweet_candidate = tweet_candidate[:280].rstrip()

    return tweet_candidate
