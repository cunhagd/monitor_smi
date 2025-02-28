import os
import psycopg2
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Configurações do banco de dados
DB_CONFIG = {
    'dbname': 'railway',
    'user': 'postgres',
    'password': 'HomctJkRyZIGzYhrlmFRdKHZPJJmWylh',
    'host': 'metro.proxy.rlwy.net',
    'port': '30848'
}

# Configurações de e-mail
SENDER_EMAIL = "devssecom@gmail.com"
SENDER_PASSWORD = "qzzo ymcg kkwn sztb"  # Use uma senha de app
RECIPIENTS = ["devssecom@gmail.com", "gustavo.cunha@governo.mg.gov.br", "isabela.bento@governo.mg.gov.br", 
              "monitoramentogovernodeminas@gmail.com", "camilakifer@gmail.com", "alinegbh@gmail.com", 
              "gustavo.medeiros@governo.mg.gov.br"]  # Lista de destinatários
ERROR_RECIPIENT = ["gustavo.cunha@governo.mg.gov.br", "isabela.bento@governo.mg.gov.br"]  # E-mail para erros

def get_max_id_from_db():
    """Conecta ao banco e retorna o maior ID da tabela 'noticias'."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM noticias")
        max_id = cursor.fetchone()[0] or 0  # Retorna 0 se NULL
        cursor.close()
        conn.close()
        return max_id
    except Exception as e:
        raise Exception(f"Erro ao acessar o banco: {e}")

def get_last_id_from_file():
    """Lê o último ID salvo no arquivo 'valor_id.txt' na raiz do projeto."""
    file_path = os.path.join(os.path.dirname(__file__), 'valor_id.txt')
    try:
        with open(file_path, 'r') as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0  # Retorna 0 se o arquivo não existir
    except ValueError:
        return 0  # Retorna 0 se o valor no arquivo for inválido

def save_id_to_file(id_value):
    """Salva o novo ID no arquivo 'valor_id.txt' na raiz do projeto."""
    file_path = os.path.join(os.path.dirname(__file__), 'valor_id.txt')
    try:
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)  # Cria o diretório se não existir
        with open(file_path, 'w') as file:
            file.write(str(id_value))
    except Exception as e:
        raise Exception(f"Erro ao salvar no arquivo: {e}")

def send_email(subject, body, recipients):
    """Envia e-mail usando SMTP do Gmail."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(recipients)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipients, msg.as_string())
        print(f"E-mail enviado para {', '.join(recipients)} com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        raise

def monitor_system():
    """Função principal para monitoramento."""
    try:
        # Passo 3: Ler o maior ID no banco
        max_id_db = get_max_id_from_db()
        print(f"Maior ID no banco: {max_id_db}")

        # Passo 4: Ler o último ID salvo no arquivo
        last_id_file = get_last_id_from_file()
        print(f"Último ID no arquivo: {last_id_file}")

        # Passo 5: Calcular a diferença
        difference = max_id_db - last_id_file
        print(f"Diferença entre IDs: {difference}")

        # Depuração: Confirmar os valores antes de enviar o e-mail
        print(f"Verificando corpo do e-mail: Usando diferença = {difference}")

        # Passo 6: Enviar e-mail baseado na diferença
        if difference <= 0:
            subject = "Alerta: Sistema de Monitoramento de Imprensa - SECOM"
            body = "O Sistema de Monitoramento de Imprensa - SECOM não salvou nenhuma notícia na última hora."
            send_email(subject, body, RECIPIENTS)
        else:
            subject = "Relatório: Sistema de Monitoramento de Imprensa - SECOM"
            body = f"O Sistema de Monitoramento de Imprensa - SECOM captou {difference} notícias na última hora."
            send_email(subject, body, RECIPIENTS)

        # Salvar o novo ID no arquivo para a próxima rodagem
        save_id_to_file(max_id_db)
        print(f"Novo ID ({max_id_db}) salvo em valor_id.txt para a próxima execução.")

    except Exception as e:
        subject = "Erro no Sistema de Monitoramento de Imprensa - SECOM"
        body = f"Ocorreu um erro ao processar o monitoramento: {str(e)}"
        send_email(subject, body, ERROR_RECIPIENT)

if __name__ == "__main__":
    monitor_system()