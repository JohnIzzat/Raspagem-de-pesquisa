from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import re
import csv
import logging

# Configuração do logging
logging.basicConfig(
    filename="app.log",             # Nome do arquivo onde os logs serão salvos
    # Define o nível dos logs (DEBUG registra tudo)
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato do log
    datefmt="%Y-%m-%d %H:%M:%S",     # Formato da data
)


def executar_busca(rede_social, nicho, email, telefone, telefone2, max_pages, search_engine="google"):
    # Usa exatamente o valor que veio da interface para o nicho
    formatted_niche = nicho
    query = (
        f"site:{rede_social.lower()}.com {formatted_niche} "
        f"({email}) (\"({telefone})\" OR \"({telefone2})\" OR \"+55\")"
    )

    logging.info(f"Executando busca com query: {query}")
    logging.debug(f"Parâmetros: Rede Social={rede_social}, Nicho={nicho}, "
                  f"Email={email}, Telefones=({telefone}, {telefone2}), "
                  f"Máx. Páginas={max_pages}, Motor de busca={search_engine}")

    # Chama a função de scraping passando o parâmetro search_engine
    results = search_and_scrape(
        query, rede_social, max_pages=max_pages, search_engine=search_engine)
    save_to_csv(results)
    return results


def search_and_scrape(query, rede_social, max_pages=5, search_engine="google"):
    logging.info(f"Iniciando scraping no {search_engine}...")

    # Configurações do Chrome
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Acessa o site conforme o search_engine escolhido
    logging.info(f"Acessando {search_engine}...")

    if search_engine.lower() == "duckduckgo":
        driver.get("https://duckduckgo.com/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q")))
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article")))
    else:  # Google
        driver.get("https://google.com/")
        time.sleep(5)
        logging.info(f"Pesquisa iniciada para query: {query}")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb")
            )
        )

    results = []
    current_page = 1
    while current_page <= max_pages:
        logging.info(f"Buscando resultados na página {current_page}...")
        print(f"Buscando página {current_page}...")
        try:
            if search_engine.lower() == "duckduckgo":
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "article"))
                )
                results_containers = driver.find_elements(
                    By.CSS_SELECTOR, "article")
            else:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb")
                    )
                )
                results_containers = driver.find_elements(
                    By.CSS_SELECTOR, "div.VwiC3b.yXK7lf.p4wth.r025kc.hJNv6b.Hdw6tb")
                logging.info(
                    f"{len(results_containers)} resultados encontrados na página {current_page}.")
        except TimeoutException:
            print("Timeout ao carregar os resultados.")
            logging.warning(
                f"Timeout ao carregar resultados na página {current_page}.")
            break

        page_results = 0
        for container in results_containers:
            try:
                # Extração dos dados
                snippet = container.text.strip()
                emails = re.findall(
                    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", snippet)
                phones = re.findall(r"\(?\d{2}\)?\s?\d{4,5}-\d{4}", snippet)

                # Registra os dados extraídos
                logging.debug(f"Snippet encontrado: {snippet[:50]}...")
                logging.debug(f"E-mails encontrados: {emails}")
                logging.debug(f"Telefones encontrados: {phones}")

                # Extração da URL e do username varia conforme o search engine
                if search_engine.lower() == "duckduckgo":
                    try:
                        a_tag = container.find_element(By.TAG_NAME, "a")
                        url = a_tag.get_attribute("href")
                    except Exception:
                        url = ""
                else:
                    try:
                        parent = container.find_element(
                            By.XPATH, "./ancestor::div[@class='g']")
                        a_tag = parent.find_element(By.TAG_NAME, "a")
                        url = a_tag.get_attribute("href")
                    except Exception:
                        url = ""
                username = extract_username(url, rede_social) if url else ""
                results.append({
                    "emails": emails,
                    "phones": phones,
                    "snippet": snippet,
                    "rede_social_user": username
                })
                page_results += 1
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                logging.error(f"Erro ao processar resultado: {e}")
                print(f"Erro ao processar resultado: {e}")

        print(f"Resultados encontrados nesta página: {page_results}")
        try:
            if search_engine.lower() == "duckduckgo":
                next_page_button = driver.find_element(By.ID, "more-results")
                next_page_button.click()
                time.sleep(random.uniform(2, 4))
                current_page += 1
            else:
                next_page_button = driver.find_element(By.LINK_TEXT, "Mais")
                next_page_button.click()
                time.sleep(5)
                current_page += 1
        except NoSuchElementException as e:
            logging.critical(f"Erro grave no scraping: {e}")
            if search_engine.lower() == "duckduckgo":
                print("Botão 'Mais resultados' não encontrado. Fim da pesquisa.")
            else:
                print("Não há mais páginas.")
            break

    driver.quit()
    logging.info(f"Scraping finalizado. Total de resultados: {len(results)}")
    return results


def extract_username(url, rede_social):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return ""
    parts = path.split("/")
    # Para redes como o Instagram, o primeiro segmento é o username.
    return parts[0]


def save_to_csv(results, filename="resultados.csv"):
    logging.info(f"Salvando {len(results)} resultados em {filename}...")
    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Rede Social", "E-mails", "Telefones", "Snippet"])
        for result in results:
            writer.writerow([
                result.get("rede_social_user", ""),
                ", ".join(result['emails']) if result['emails'] else 'Nenhum',
                ", ".join(result['phones']) if result['phones'] else 'Nenhum',
                result['snippet']
            ])
    logging.info(f"Arquivo {filename} salvo com sucesso.")


if __name__ == "__main__":
    print("Back-end iniciado. Aguardando chamadas do front-end.")
