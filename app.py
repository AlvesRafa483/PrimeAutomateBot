#Import de Bibliotecas
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from time import sleep
from flask import Flask, request
from flask import jsonify
import json
import requests

# Setup flask server
app = Flask(__name__)
# nodeApi = "http://localhost:3000"
nodeApi = "https://prime-automate-api-fh9hz.ondigitalocean.app"

def initDriver():
    # Inicialização e configuração do webdriver
    global driver
    global wait

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    options.add_argument("use_subprocess=True")

    driver = uc.Chrome(options=options)
    # driver.implicitly_wait(20)
    wait = WebDriverWait(driver, 20)


#Login no google
@app.route('/maps/login', methods=['POST'])
def maps_login(email, senha):
    data = request.get_json()

    email = data['email']
    senha = data['senha']

    initDriver()

    url = 'https://accounts.google.com/v3/signin/identifier?dsh=S-637314068%3A1688388713870065&continue=https%3A%2F%2Fwww.google.com%2Fmaps%2F%40-22.5688278%2C-48.6357383%2C7z%3Fentry%3Dttu&ec=GAZAcQ&hl=pt-BR&ifkv=AeDOFXgKCdbvrdQ0uICIK6Fcggqw6D_b9JM9vQ7kKKvvJjWGvi5_TCSgsMaotW2V2SKXmKe9xFLZYA&passive=true&service=local&flowName=GlifWebSignIn&flowEntry=ServiceLogin'
    driver.get(url)

    # PREENCHER DADOS DE LOGIN
    try:
        identifier = wait.until(EC.visibility_of_element_located((By.NAME, 'identifier')))
        identifier.send_keys(email + Keys.ENTER)
    except Exception as ex:
        return False
    except TimeoutException as ex:
        return False

    try:
        passwd = wait.until(EC.visibility_of_element_located((By.NAME, 'Passwd')))
        passwd.send_keys(senha + Keys.ENTER)
    except Exception as ex:
        return False
    except TimeoutException as ex:
        return False

    try:
        accountIcon = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="gb"]/div/div/div[1]/div[2]/div/a')))

        if email in accountIcon.get_attribute('title'):
            return True
        else:
            return False

    except Exception as ex:
        return False
    except TimeoutException as ex:
        return False


def erroAvaliar(erro, id):
    data = {'erro': erro}
    url = nodeApi + '/bot/avaliacoes/erro/' + str(id)
    print(url)

    # Enviar erro para API
    res = requests.post(url, json=data)

    # Resposta da API
    returned_data = res.json()
    print(returned_data)

def sucessoAvaliar(id):
    data = {'sucesso': 'ok'}
    url = nodeApi + '/bot/avaliacoes/sucesso/' + str(id)
    print(url)

    # Enviar para API
    res = requests.post(url, json=data)

    # Resposta da API
    returned_data = res.json()
    print(returned_data)


@app.route('/maps/avaliar', methods=['POST'])
def maps_avaliar():
    data = request.get_json()

    # Dados de Login
    email = data['email']
    senha = data['senha']

    # Avaliações a realizar
    avaliacoes = data['avaliacoes']

    # Efetuar login em maps
    login = maps_login(email, senha)

    if not login:
        driver.quit()
        for avaliacao in data['avaliacoes']:
            erroAvaliar("Erro ao logar na conta: " + email, avaliacao["id"])
        return json.dumps({"success": True})


    # Realizar todas as avaliacoes para a conta logada
    for avaliacao in avaliacoes:
        url = avaliacao['agendamento']['empresa']['url']
        comentario = avaliacao['comentario']
        print(url)
        print(comentario)


        driver.get(url)

        # Tab Avaliações
        try:
            avaliacaoTab = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[aria-label~='Avaliações']")))
            avaliacaoTab.click()
        except Exception as ex:
            print("Error: Não foi possível acessar o elemento: 'Tab Avaliações'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Tab Avaliações'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Tab Avaliações'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Error: Não foi possível acessar o elemento: 'Tab Avaliações'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Tab Avaliações'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Tab Avaliações'", avaliacao["id"])
            continue

        # Button Avaliar
        try:
            sleep(1)
            avaliarButton = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label~='Avaliar']")))
            avaliarButton.click()

            # goog-reviews-write-widget
            # return json.dumps({"success": True})
        except Exception as e:
            print("Error: Não foi possível acessar o elemento: 'Avaliar Botão'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Avaliar Botão'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Avaliar Botão'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Error: Não foi possível acessar o elemento: 'Avaliar Botão'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Avaliar Botão'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Avaliar Botão'", avaliacao["id"])
            continue

        try:
            # Acessar frame avaliar
            # sleep(5)
            # frames = driver.find_elements(By.TAG_NAME, "iframe")
            # print("Frames:" + str(len(frames)))

            avaliarFrame = wait.until(EC.visibility_of_element_located((By.NAME, "goog-reviews-write-widget")))
            driver.switch_to.frame(avaliarFrame)
        except Exception as e:
            print("Error: Não foi possível acessar o elemento: 'Frame Avaliar'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Frame Avaliar'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Frame Avaliar'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Error: Não foi possível acessar o elemento: 'Frame Avaliar'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Frame Avaliar'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Frame Avaliar'", avaliacao["id"])
            continue

        # Clicar na quinta estrela
        try:
            sleep(1)
            header = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.HDUCif')))
            header.click()
            sleep(1)
            notas = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Nota com estrelas"]')))
            estrela = notas.find_element(By.CSS_SELECTOR, 'div[aria-label="Cinco estrelas"]')
            estrela.click()
        except Exception as ex:
            print("Erro: Não foi possível acessar o elemento: 'Quinta estrela'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Quinta estrela'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Quinta estrela'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Erro: Não foi possível acessar o elemento: 'Quinta estrela'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Quinta estrela'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Quinta estrela'", avaliacao["id"])
            continue

        # Preencher comentário
        try:
            if comentario:
                sleep(1)
                comenteBox = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea[aria-label="Inserir a avaliação"]')))
                comenteBox.send_keys(comentario)
        except Exception as ex:
            print("Erro: Não foi possível acessar o elemento: 'Caixa de comentários'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Caixa de comentários'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Caixa de comentários'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Erro: Não foi possível acessar o elemento: 'Caixa de comentários'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Caixa de comentários'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Caixa de comentários'", avaliacao["id"])
            continue

        # Clicar em postar
        try:
            sleep(1)
            postarBtn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="kCvOeb"]/div[2]/div/div[2]/div/button')))
            postarBtn.click()
            sleep(1)
            sucessoAvaliar(avaliacao["id"])
        except Exception as ex:
            print("Erro: Não foi possível acessar o elemento: 'Postar Botão'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Postar Botão'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Postar Botão'", avaliacao["id"])
            continue
        except TimeoutException as ex:
            print("Erro: Não foi possível acessar o elemento: 'Postar Botão'")
            # return json.dumps({"success": False, "error": "Não foi possível acessar o elemento: 'Postar Botão'"})
            erroAvaliar("Não foi possível acessar o elemento: 'Postar Botão'", avaliacao["id"])
            continue

    driver.quit()
    return json.dumps({"success": True})


#Rotas para testes do bot via Request
@app.route('/arraysum', methods=['POST'])
def sum_of_array():
    data = request.get_json()
    print(data)

    # Data variable contains the
    # data from the node server
    ls = data['array']
    result = sum(ls)  # calculate the sum

    # Return data in json format
    return json.dumps({"result": result})

@app.route('/hello', methods=['GET'])
def helloWord():
    return json.dumps({"hello": "Hello Word!"})

# MAIN
if __name__ == '__main__':
    app.run(port=5000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
