from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
#import pandas as pd, pyodbc
#from io import StringIO

#inputs
nome_marca = input("Digite o nome da MARCA: ")
while True:
    entrada = input("Digite o número da CLASSE (1 a 46) ou pressione ENTER para ignorar: ")

    if entrada == "":
        classe_nice = None
        break

    try:
        classe_nice = int(entrada)

        if 1 <= classe_nice <= 46:
            break
        else:
            print("Classe inexistente. Digite um número entre 1 e 46.\n")

    except ValueError:
        print("Entrada inválida. Digite apenas números.\n")

    
print(f"Marca selecionada: {nome_marca}")
if classe_nice:
    print(f"Classe selecionada: {classe_nice}")
else:
    print("Nenhuma classe selecionada.")

#driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 15)

try:
    #loga no INPI
    driver.get("https://busca.inpi.gov.br/pePI/")
    wait.until(
    EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(text(),'Continuar')]")
        )
    ).click()
    
    wait.until(lambda d: len(d.window_handles) > 1)

    abas = driver.window_handles
    aba_original = abas[0]
    aba_nova = abas[1]

    driver.switch_to.window(aba_nova)
    driver.close()
    driver.switch_to.window(aba_original)

    #vai para a página de pesquisa
    driver.get("https://busca.inpi.gov.br/pePI/jsp/marcas/Pesquisa_classe_basica.jsp")

    #marca o tipo de pesquisa como radical
    radio_radical = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@name='buscaExata' and @value='nao']")
        )
    )

    driver.execute_script("arguments[0].click();", radio_radical)

    #preenche os inputs de texto
    inputs = driver.find_elements(By.XPATH, "//input[@type='text']")

    #input de marca
    inputs[0].clear()
    inputs[0].send_keys(nome_marca)

    #input de classificação
    if classe_nice is not None:
        inputs[1].clear()
        inputs[1].send_keys(classe_nice)

    #quantidade de processos por página (100)
    from selenium.webdriver.support.ui import Select

    select = Select(driver.find_element(By.TAG_NAME, "select"))
    select.select_by_visible_text("100")

    #pesquisa
    driver.find_element(By.XPATH, "//input[@type='submit']").click()
    
    #espera a tabela aparecer
    wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
    
    #pega todas as linhas da tabela
    linhas = driver.find_elements(
        By.XPATH,
        "//tr[not(.//img[@alt='Marca Arquivada'])]"
    )

    resultados = []

    #pula cabeçalho
    for linha in linhas[1:]:  
        colunas = linha.find_elements(By.TAG_NAME, "td")
        if len(colunas) > 0:
            dados = [coluna.text.strip() for coluna in colunas]
            resultados.append(dados)

    for r in resultados:
        print(r)

    #verifica se não encontrou resultados
    mensagem_sem_resultado = driver.find_elements(
    By.XPATH,
    "//*[contains(text(),'Nenhum resultado foi encontrado')]"
    )   
    
    #calcula a chance de registro
    # quantidade = max(len(linhas) - 7, 0)

    # if mensagem_sem_resultado:
    #     quantidade = max(quantidade -2, 0)
    #     chance = 100-1
    # else:
    #     quantidade = quantidade
    #     chance = min(math.log10(quantidade + 1) * 50, 100)

    # print(f"Total de resultados: {quantidade}")
    # print(f"Chance estimada de registro: {chance:.1f}%")

except Exception as e:
    print("Erro:", e)