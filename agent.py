import os
import time
import logging
import urllib.request
import urllib.parse
import json
import requests
from bs4 import BeautifulSoup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('researcher')

# Use Groq (FREE) for research — ultrafast inference, zero cost
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'
GROQ_MODEL = 'llama-3.1-8b-instant'

# Fallback to Gemini Flash if Groq unavailable
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}'

def read_prompt():
    try:
        with open('core_prompt.md', 'r') as f:
            return f.read()
    except:
        return 'You are a research AI. Find cheaper AI models and useful APIs.'

def read_full_webpage(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract readable text, focusing on paragraphs and common content tags
        text_content = []
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
            text = tag.get_text(separator=' ', strip=True)
            if text:
                text_content.append(text)
        
        return '\n'.join(text_content)
    except requests.exceptions.RequestException as e:
        return f'Failed to read webpage {url}: {e}'
    except Exception as e:
        return f'Error parsing webpage {url}: {e}: {response.status_code if 'response' in locals() else 'N/A'}'

def search_web(query):
    try:
        url = f'https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        soup = BeautifulSoup(html, 'html.parser')
        search_results = []
        
        # Extract URLs from the DuckDuckGo search results
        for link in soup.find_all('a', class_='result__url'):
            href = link.get('href')
            if href and href.startswith('http'):
                search_results.append(href)
        
        full_content = []
        # Read full content of the top 3 search results
        for i, result_url in enumerate(search_results[:3]):
            logger.info(f'Reading full content from: {result_url}')
            content = read_full_webpage(result_url)
            if content:
                # Removed content limit to allow full page reading
                full_content.append(f'--- Content from {result_url} ---\n{content}...')
        
        return '\n'.join(full_content) if full_content else 'No detailed results found.'
    except Exception as e:
        return f'Search failed: {e}'

def ask_groq(system_prompt, user_prompt):
    payload = json.dumps({
        'model': GROQ_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'temperature': 0.7,
        'max_tokens': 1024,
    }).encode()
    req = urllib.request.Request(GROQ_URL, data=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {GROQ_API_KEY}',
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data['choices'][0]['message']['content']

def ask_gemini(prompt):
    payload = json.dumps({
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {'temperature': 0.7, 'maxOutputTokens': 1024}
    }).encode()
    req = urllib.request.Request(GEMINI_URL, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
        return data['candidates'][0]['content']['parts'][0]['text']

def ask_llm(system_prompt, user_prompt):
    if GROQ_API_KEY:
        try:
            return ask_groq(system_prompt, user_prompt), 'groq'
        except Exception as e:
            logger.warning(f'Groq failed: {e}, falling back to Gemini')
    try:
        return ask_gemini(f'{system_prompt}\n\n{user_prompt}'), 'gemini'
    except Exception as e:
        return f'All models failed: {e}', 'none'

def save_finding(finding):
    with open('/app/findings.log', 'a') as f:
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} | {finding}\n')

def research_cycle():
    topics = [
        'cheapest LLM API 2026 cost per million tokens comparison',
        'free open source AI models autonomous coding agents 2026',
        'MiniMax M2.5 vs Claude vs Gemini cost comparison autonomous agents',
        'Groq Cerebras fastest LLM inference free tier limits 2026',
        'DeepSeek V3 R1 API free tier rate limits 2026',
        'best self-evolving AI agent architectures open source 2026',
        'Qwen3 Coder API free access autonomous agent tools',
        'AI agent financial independence revenue generation ideas 2026',
        'cheapest cloud GPU providers AI inference 2026',
        'open source AI agent frameworks EvoAgentX AutoGen CrewAI 2026',
    ]
    topic = topics[int(time.time() / 900) % len(topics)]
    logger.info(f'Researching: {topic}')

    results = search_web(topic)
    logger.info(f'Search results: {results[:300]}...')

    system = read_prompt()
    user = f'Search results for {topic}:\n{results}\n\nAnalyze in 5 detailed bullet points: (1) specific cost/token (provide numbers and units), (2) precise quality assessment for autonomous agents, (3) detailed integration difficulty, (4) unique features/advantages, (5) significant limitations/disadvantages. Be very specific with numbers and examples where possible.'

    analysis, model = ask_llm(system, user)
    logger.info(f'[{model}] Analysis: {analysis[:500]}...')
    save_finding(f'[{model}] Topic: {topic}\n{analysis}\n---')
    return analysis

if __name__ == '__main__':
    provider = 'Groq (FREE)' if GROQ_API_KEY else 'Gemini Flash (paid)'
    logger.info(f'Researcher Agent starting with {provider}, 15min cycles...')
    while True:
        try:
            research_cycle()
        except Exception as e:
            logger.error(f'Research cycle error: {e}')
        logger.info('Sleeping 15 minutes...')
        time.sleep(900)
