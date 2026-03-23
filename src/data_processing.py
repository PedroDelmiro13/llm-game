import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS = [
    "https://pt.wikipedia.org/wiki/Futevôlei",
    "https://pt.wikipedia.org/wiki/Futebol_de_praia",
    "https://pt.wikipedia.org/wiki/Voleibol_de_praia",
    "https://pt.wikipedia.org/wiki/Teqball",
    "https://pt.wikipedia.org/wiki/Futebol_de_mesa",
    "https://pt.wikipedia.org/wiki/Campeonato_Mundial_de_Voleibol_de_Praia",
    "https://pt.wikipedia.org/wiki/Circuito_Mundial_de_Vôlei_de_Praia",
    "https://pt.wikipedia.org/wiki/Confederação_Brasileira_de_Voleibol",
    "https://pt.wikipedia.org/wiki/Sele%C3%A7%C3%A3o_Brasileira_de_Voleibol_Masculino",
    "https://pt.wikipedia.org/wiki/Sele%C3%A7%C3%A3o_Brasileira_de_Voleibol_Feminino",
    "https://pt.wikipedia.org/wiki/Copa_do_Mundo_de_Futebol_de_Areia",
    "https://pt.wikipedia.org/wiki/Sele%C3%A7%C3%A3o_Brasileira_de_Futebol_de_Areia",
]

def fetch_pages():
    textos = []
    
    for url in URLS:
        try:
            print(f"Coletando: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=15, verify=False, headers=headers)
            
            if response.status_code != 200:
                print(f"  Status {response.status_code} - página ignorada")
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            for elemento in soup.find_all(["script", "style", "nav", "footer", "header"]):
                elemento.decompose()

            paragrafos = []
            
            for tag in [
                "article",
                "main",
                "[role='main']",
                "#content",
                ".content",
                ".post-content",
                ".entry-content",
                ".article-content",
                ".main-content",
                ".page-content",
                "#main-content",
                ".post",
                ".entry",
                ".page"
            ]:
                conteudo = soup.select_one(tag)
                if conteudo:
                    paragrafos = conteudo.find_all("p")
                    break
            if not paragrafos:
                paragrafos = soup.find_all("p")
            
            texto_pagina = " ".join(p.get_text() for p in paragrafos)
            
            # só adiciona se tiver mais de 200 caracteres
            if len(texto_pagina) > 200:
                textos.append(texto_pagina)
                print(f"  {len(texto_pagina)} caracteres")
            else:
                print(f"  Texto muito curto ({len(texto_pagina)} caracteres) - ignorado")
                
            time.sleep(1) 
        except Exception as e:
            print(f"  Erro: {e}")
            continue
    print(f"\nTotal: {len(textos)} páginas coletadas")
    return textos

def clean_text(texto):
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"[^\w\s.,!?\-'\"()áéíóúãõçÁÉÍÓÚÃÕÇ]", "", texto)
    return texto.strip()

def chunk_text(texto, max_caracteres=800, sobreposicao=100):
    frases = re.split(r'(?<=[.!?])\s+', texto)
    
    #remove frases muito curtas (menos de 15 caracteres)
    frases = [f.strip() for f in frases if len(f.strip()) > 15]
    
    if not frases:
        return []
    
    chunks = []
    chunk_atual = []
    tamanho_atual = 0
    
    for frase in frases:
        tamanho_frase = len(frase)
        if tamanho_atual + tamanho_frase <= max_caracteres:
            chunk_atual.append(frase)
            tamanho_atual += tamanho_frase
        else:
            if chunk_atual:
                chunks.append(" ".join(chunk_atual))
            chunk_atual = [frase]
            tamanho_atual = tamanho_frase
    
    if chunk_atual:
        chunks.append(" ".join(chunk_atual))
    return chunks