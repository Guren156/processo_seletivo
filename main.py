import os
import logging
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")

if not all([SUPABASE_URL, SUPABASE_KEY, ZAPI_INSTANCE_ID, ZAPI_TOKEN]):
    logger.error("Erro: Faltam tokens ou chaves no seu ficheiro .env")
    exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.error(f"Erro ao conectar ao Supabase: {e}")
    exit(1)

def buscar_contatos():
    """Puxa os contactos da tabela que criou no Supabase"""
    try:
        logger.info("A procurar contactos no Supabase...")
        resposta = supabase.table("contatos").select("nome_contato", "telefone").execute()
        return resposta.data
    except Exception as e:
        logger.error(f"Erro ao ler dados do Supabase: {e}")
        return []

def enviar_mensagem_zapi(nome: str, telefone: str):
    """Envia a mensagem exata usando a infraestrutura da Z-API"""
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    headers = {"Content-Type": "application/json"}
    
    mensagem_texto = f"Olá, {nome} tudo bem com você?"
    
    payload = {
        "phone": telefone,
        "message": mensagem_texto
    }
    
    try:
        resposta = requests.post(url, json=payload, headers=headers, timeout=10)
        if resposta.status_code in [200, 201]:
            logger.info(f"Mensagem enviada com sucesso para {nome} ({telefone})")
            return True
        else:
            logger.warning(f"Falha ao enviar para {nome}. Status: {resposta.status_code} - Erro: {resposta.text}")
            return False
    except Exception as e:
        logger.error(f"Erro de rede ao comunicar com a Z-API: {e}")
        return False

def main():
    logger.info("=== Iniciando Automação do Desafio ===")
    
    contatos = buscar_contatos()
    if not contatos:
        logger.warning("Nenhum contacto encontrado para processar.")
        return

    contatos_para_envio = contatos[:3]
    logger.info(f"Processando {len(contatos_para_envio)} contactos para envio.")

    for contato in contatos_para_envio:
        nome = contato.get("nome_contato")
        telefone = contato.get("telefone")
        
        if nome and telefone:
            enviar_mensagem_zapi(nome, telefone)
        else:
            logger.warning(f"Contacto com dados incompletos ignorado: {contato}")

    logger.info("=== Processo Finalizado com Sucesso ===")

if __name__ == "__main__":
    main()