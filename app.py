import eventlet
eventlet.monkey_patch()

import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random
import copy
import re
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'conexao_intima_distancia_2026_prod'

socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='eventlet', 
    transports=['websocket', 'polling'],
    ping_timeout=60, 
    ping_interval=25
)

# 🌐 BARALHO 100% ADAPTADO PARA DISTÂNCIA (ZERO CONTATO PRESENCIAL)
ORIGINAL_CARDS = {
    "fase1": {
        "verdade": {
            "H": [
                "De 0 a 10, quão ansioso {mandante} está para ver {alvo} na câmera e o que ela poderia mostrar agora para chegar ao 10?",
                "Qual foi o pensamento mais safado que {mandante} teve com {alvo} hoje enquanto lembrava do último encontro de vocês?",
                "Confesse para {alvo}: você prefere ver ela na câmera totalmente nua ou de lingerie provocante com salto?",
                "Olhe para a câmera fixamente e diga para {alvo} qual parte do corpo dela você mais queria estar tocando agora.",
                "Se você pudesse ver {alvo} usando qualquer lingerie nova na chamada de vídeo hoje, qual seria?",
                "Qual foi a última fantasia que passou pela sua cabeça enquanto me via trocando de roupa ou por foto?"
            ],
            "M": [
                "Diga para {alvo} o que ele faz na chamada de vídeo ou no tom de voz do áudio que te deixa mais molhada a distância?",
                "Qual é o seu maior fetiche visual? Diga para {alvo} o que ele pode fazer na câmera agora que te ativa na hora.",
                "Se você pudesse fazer um pedido proibido para {alvo} cumprir no vídeo agora, sem julgamentos, qual seria?",
                "Qual brinquedo erótico seu você tem mais desejo de usar na frente da câmera hoje?",
                "Se você pudesse mandar {alvo} tirar apenas uma peça de roupa específica agora na tela, o que seria?"
            ],
            "A": [
                "Qual foi o momento mais marcante ou ousado que já viveram em uma chamada de vídeo até hoje?",
                "Se vocês tivessem que escolher um brinquedo erótico para usar em sincronia no vídeo hoje, qual seria?",
                "Diga uma palavra ou frase safada que o outro sussurra no áudio que te desmonta por inteiro."
            ]
        },
        "desafio": {
            "H": [
                "{mandante}, tire a sua camisa devagar na frente da câmera, fazendo uma pose provocante só para {alvo}.",
                "{mandante} deve enviar um áudio de 15 segundos no WhatsApp com tom de voz bem grave e sussurrado, dizendo exatamente o que vai fazer com {alvo} no próximo final de semana.",
                "{mandante}, ajuste o ângulo da sua câmera para focar no seu abdômen/peitoral e faça um carinho na própria pele por 1 minuto enquanto {alvo} assiste.",
                "{mandante}, pegue o celular, aproxime a câmera bem perto dos seus lábios e dê um beijo lento e provocante na tela para {alvo}.",
                "{mandante} deve dar início a um **Conto Erótico**: comece a inventar uma história curta e safada envolvendo vocês dois em um hotel. Fale por 1 minuto na chamada."
            ],
            "M": [
                "{mandante}, prenda o seu cabelo na câmera, olhe para {alvo} com o olhar mais safado que tiver e lamba os seus próprios lábios devagar.",
                "{mandante}, faça um biquinho sexy e passe as mãos pelos seus próprios seios por cima da roupa olhando para a câmera.",
                "{mandante}, ande lentamente de salto alto/lingerie na frente da câmera, faça uma pose provocante e morda o lábio inferior por 30 segundos.",
                "SPOILER REMOTO: {mandante} deve mandar uma foto surpresa do seu decote ou lingerie no WhatsApp agora para {alvo} guardar.",
                "{mandante}, aproxime a câmera do seu pescoço/saboneteira e dê um suspiro bem provocante no microfone por 20 segundos."
            ],
            "A": [
                "Coloquem a mesma música sensual para tocar ao mesmo tempo no fundo das chamadas de vocês.",
                "Ambos devem dar um gole na bebida e olhar fixamente para a câmera por 45 segundos sem rir e sem piscar."
            ]
        }
    },
    "fase2": {
        "verdade": {
            "H": [
                "O que te dá mais tesão na distância: ouvir os gemidos de {alvo} no áudio ou ver a expressão facial dela no vídeo?",
                "Se {alvo} te mostrasse a intimidade dela na câmera agora, qual o primeiro comando de voz que você daria para ela?",
                "Qual o maior tesão de ver {alvo} se tocando na sua frente através do vídeo?"
            ],
            "M": [
                "Qual foi a última vez que você se masturbou pensando em {alvo} e qual foi a cena exata que você imaginou?",
                "Olhando para {alvo} na tela agora, qual o nível de desejo de ver ele totalmente nu e ereto?",
                "Qual a sensação de se tocar na frente da câmera sabendo o fetiche e o controle que isso exerce sobre ele?"
            ],
            "A": [
                "Vocês preferem quando o clima da chamada é lento e provocante ou quando é direto e dominante?",
                "Qual de vocês fica mais ousado e sem limites na câmera quando o vinho/bebida começa a fazer efeito?"
            ]
        },
        "desafio": {
            "H": [
                "{mandante}, abra a sua calça na câmera, coloque a mão por dentro da cueca e toque o seu membro ereto por 1 minuto enquanto olha fixamente para {alvo}.",
                "{mandante}, fique totalmente nu da cintura para cima e dê ordens sussurradas pelo áudio de como quer que {alvo} toque os próprios seios.",
                "{mandante}, pegue um cubo de gelo ou óleo e passe pelo seu peitoral e abdômen ao vivo na câmera por 1 minuto.",
                "{mandante} deve deitar na cama com a câmera posicionada de cima e se masturbar lentamente no ritmo que {alvo} comandar por 1 minuto e meio."
            ],
            "M": [
                "{mandante}, tire o seu sutiã/blusa de forma bem lenta na câmera, deixando seus seios totalmente livres para {alvo} ver.",
                "{mandante}, tire a sua calcinha discretamente por baixo da roupa e jogue na câmera olhando fixamente para a lente.",
                "{mandante}, deite-se na cama, passe gel lubrificante nos seus dedos e comece a massagear a sua intimidade por 1 minuto e meio enquanto {alvo} assiste.",
                "{mandante}, pegue o vibrador ou sugador de clitóris (a rosa), ligue na velocidade média e use na sua intimidade na câmera por 2 minutos seguidos."
            ],
            "A": [
                "SESSÃO DE FOTOS PRIVADA: {mandante} deve fazer 3 poses sensuais na câmera para {alvo} tirar print do celular e guardar como troféu.",
                "AMBOS NUS DA CINTURA PARA CIMA: Tirem as blusas/camisas imediatamente para o restante desta fase."
            ]
        }
    },
    "fase3": {
        "verdade": {
            "H": [
                "De todas as vezes que jogamos a distância, qual foi o ângulo de {alvo} na tela que ficou gravado na sua memória?",
                "Se você pudesse me ver gozando na câmera agora, em qual posição você gostaria que eu estivesse posicionado(a)?"
            ],
            "M": [
                "Qual palavra ou comando dominante de {alvo} no áudio te faz chegar mais rápido ao orgasmo na distância?",
                "Se você pudesse congelar a imagem da tela agora para durar uma hora, qual ângulo visual você escolheria?"
            ],
            "A": [
                "Quão mais forte fica o desejo de se encontrarem pessoalmente depois de uma noite intensa de jogo a distância?"
            ]
        },
        "desafio": {
            "H": [
                "{mandante}, fique completamente nu na câmera e comece a se masturbar intensamente focado no rosto de {alvo} até a próxima carta.",
                "{mandante}, ajuste a câmera para focar no seu membro ereto e se masturbe no ritmo dos gemidos que {alvo} emitir ao vivo.",
                "COMANDO DOMINANTE: {mandante} deve dar ordens diretas e firmes pelo áudio dizendo exatamente onde e como {alvo} deve tocar a própria intimidade até ela suspirar alto."
            ],
            "M": [
                "{mandante}, fique totalmente nua na câmera, abra bem as pernas e use os dedos ou vibrador na sua intimidade mantendo contato visual com a lente por 2 minutos.",
                "{mandante}, sente-se de frente para a câmera e cavalgue no ar ou no dildo/vibrador no ritmo que {alvo} mandar por 2 minutos.",
                "ORGASMO GUIADO: {mandante} deve focar o estímulo no seu clitóris com o brinquedo ou dedos enquanto escuta {alvo} narrando o que faria se estivessem no mesmo quarto."
            ],
            "A": [
                "CLÍMAX SINCRONIZADO: Esqueçam as cartas. Mantenham as câmeras ligadas e se estimulem ao mesmo tempo até que os dois atinjam o orgasmo ao vivo no vídeo!"
            ]
        }
    }
}

ORIGINAL_DICE = {
    "acao_corpo": {
        "acoes": [
            "Lamber os próprios lábios olhando fixo para a câmera e para",
            "Mostrar bem de perto na tela",
            "Passar a ponta dos dedos bem devagar por",
            "Dar mordidinhas provocantes na própria boca pensando em",
            "Passar óleo/gel corporal e destacar no vídeo"
        ],
        "corpo": {
            "H": ["o peitoral nu", "o abdômen ereto", "o membro ereto"],
            "M": ["os mamilos nus", "a lingerie provocante", "a intimidade molhada"],
            "A": ["os lábios", "o pescoço", "a virilha", "as coxas na câmera"]
        }
    },
    "posicao_local": {
        "locais": ["na cama com iluminação baixa", "no chão encostado na parede", "na cadeira/poltrona de frente para a câmera"],
        "posicoes_por_local": {
            "na cama com iluminação baixa": ["Deitados de costas masturbando-se para o vídeo", "Posição de quatro focando o quadril na tela"],
            "no chão encostado na parede": ["Sentado(a) com pernas abertas mostrando o estímulo", "Apoiado(a) de joelhos olhando para a lente"],
            "na cadeira/poltrona de frente para a câmera": ["Rebolando de salto alto na cadeira", "Sentado(a) na ponta com pernas elevadas"]
        }
    },
    "brinquedos_acessorios": {
        "acoes": [
            "Usar o sugador de clitóris/vibrador ao vivo na câmera em",
            "Usar uma venda nos olhos e se tocar guiado apenas pela voz do par em",
            "Usar uma lingerie ou salto alto e focar a tela em"
        ],
        "foco": {
            "H": ["o membro ereto", "o abdômen"],
            "M": ["o clitóris", "os mamilos"],
            "A": ["a virilha", "as coxas"]
        }
    },
    "clima_intensidade": {
        "estilos": [
            "Voz sussurrada e tom extremamente dominante pelo áudio",
            "Provocação total: se toque por 1 minuto na tela, mas pare antes de gozar",
            "Fazer o estímulo de olhos fechados se guiando pela respiração do outro"
        ],
        "restricoes": [
            "sem poder emitir gemidos altos (apenas sussurros no microfone)",
            "mantendo contato visual ininterrupto com a lente da câmera",
            "falando palavras sujas e confissões safadas no áudio ao vivo"
        ]
    }
}

ORIGINAL_CHALLENGES_TIME = [
    "{mandante} deve se tocar na câmera por 60 segundos sem emitir nenhum som. Se gemer alto antes do tempo, {alvo} ganha 1 ponto!",
    "{mandante} deve aproximar o microfone da boca e descrever a coisa mais proibida que quer fazer no próximo encontro presencial por 45 segundos.",
    "{mandante} deve manter o vibrador/sugador na intimidade por 60 segundos seguidos sem fechar os olhos na câmera."
]

ORIGINAL_NEVER_CARDS = [
    "Eu nunca tirei uma foto ousada para enviar para o meu par no meio do expediente de trabalho.",
    "Eu nunca me masturbei assistindo a uma gravação antiga nossa enquanto estávamos longe.",
    "Eu nunca fiquei com tanta vontade do meu par a distância que precisei parar o que estava fazendo para mandar um áudio proibido."
]

ORIGINAL_PUNISHMENTS = [
    "Tirar mais uma peça de roupa ao vivo na câmera agora mesmo.",
    "Ficar sem falar nenhuma palavra e apenas cumprir os comandos de voz do par até a próxima rodada.",
    "Enviar uma foto extremamente provocante e sem filtro no chat agora."
]

ACTIVE_ROOMS = {}

GAME_LABELS = {
    "cards": "Baralho de Cartas",
    "dice": "Dados Eróticos",
    "time": "Contra o Relógio",
    "never": "Eu Nunca Picante"
}

def generate_room_id():
    while True:
        room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if room_id not in ACTIVE_ROOMS:
            return room_id

def get_initial_room_state():
    return {
        "state": {
            "players": {}, 
            "current_player": None,
            "target_player": None,
            "current_cards": {},
            "game_started": False,
            "play_mode": "separated", 
            "game_type": "cards", 
            "dice_category": "all", 
            "scores": {"H": 0, "M": 0},
            "has_double_turn": False,
            "game_over": False,
            "rounds_played": {"H": {"fase1": 0, "fase2": 0, "fase3": 0}, "M": {"fase1": 0, "fase2": 0, "fase3": 0}},
            "last_chosen_by": "",
            "creator_name": "",  
            "creator_gender": ""  
        },
        "session_cards": copy.deepcopy(ORIGINAL_CARDS),
        "session_dice": copy.deepcopy(ORIGINAL_DICE),
        "session_never": list(ORIGINAL_NEVER_CARDS),
        "session_time": list(ORIGINAL_CHALLENGES_TIME),
        "session_punishments": copy.deepcopy(ORIGINAL_PUNISHMENTS),
        "dice_pool_shuffle": []
    }

def discover_time(text):
    text_lower = text.lower()
    min_match = re.search(r'(\d+)\s*minuto', text_lower)
    if min_match: return int(min_match.group(1)) * 60
    sec_match = re.search(r'(\d+)\s*segundo', text_lower)
    if sec_match: return int(sec_match.group(1))
    return 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def handle_create_room():
    room_id = generate_room_id()
    ACTIVE_ROOMS[room_id] = get_initial_room_state()
    emit('room_created', {'room_id': room_id, 'game_type': 'cards'})

@socketio.on('check_room_status')
def handle_check_room(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id in ACTIVE_ROOMS:
        emit('room_status_checked', {
            'valid': True,
            'game_type': ACTIVE_ROOMS[room_id]["state"]["game_type"],
            'creator_name': ACTIVE_ROOMS[room_id]["state"]["creator_name"],
            'creator_gender': ACTIVE_ROOMS[room_id]["state"]["creator_gender"]
        })
    else:
        emit('room_status_checked', {'valid': False})

@socketio.on('join_game')
def handle_join(data):
    room_id = data.get('room_id', '').strip().upper()
    player_name = data.get('name', 'Anonimo').strip()
    gender = data.get('gender')
    game_type = data.get('game_type', 'cards')
    dice_category = data.get('dice_category', 'all')
    
    if room_id not in ACTIVE_ROOMS:
        emit('error', {'msg': 'Código de sala inválido!'})
        return

    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    join_room(room_id)
    
    if len(game_state["players"]) == 0:
        game_state["game_type"] = game_type
        game_state["dice_category"] = dice_category
        game_state["creator_name"] = player_name
        game_state["creator_gender"] = gender
        game_state["last_chosen_by"] = f"{player_name} definiu: {GAME_LABELS.get(game_type, game_type)}"

    existing_pid = None
    for pid, p in game_state["players"].items():
        if p["name"] == player_name and p["gender"] == gender:
            existing_pid = pid
            break

    if existing_pid:
        game_state["players"][request.sid] = game_state["players"].pop(existing_pid)
        if game_state["current_player"] == existing_pid: game_state["current_player"] = request.sid
        if game_state["target_player"] == existing_pid: game_state["target_player"] = request.sid
    else:
        if len(game_state["players"]) < 2:
            game_state["players"][request.sid] = {"name": player_name, "gender": gender, "ready": False}
        else:
            emit('error', {'msg': 'O casal já está na sala!'})
            return

    update_all_clients(room_id)

@socketio.on('player_ready')
def handle_ready(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if request.sid in game_state["players"]:
        game_state["players"][request.sid]["ready"] = True
        p_ids = list(game_state["players"].keys())
        
        if len(p_ids) == 2 and all(game_state["players"][uid]["ready"] for uid in p_ids):
            game_state["game_started"] = True
            game_state["game_over"] = False
            
            room["session_cards"] = copy.deepcopy(ORIGINAL_CARDS)
            room["session_dice"] = copy.deepcopy(ORIGINAL_DICE)
            room["session_never"] = list(ORIGINAL_NEVER_CARDS)
            room["session_time"] = list(ORIGINAL_CHALLENGES_TIME)
            game_state["current_cards"] = {}
            game_state["scores"] = {"H": 0, "M": 0}
            game_state["rounds_played"] = {
                "H": {"fase1": 0, "fase2": 0, "fase3": 0},
                "M": {"fase1": 0, "fase2": 0, "fase3": 0}
            }
            
            random.shuffle(p_ids)
            game_state["current_player"] = p_ids[0]
            game_state["target_player"] = p_ids[1]
            
            socketio.emit('start_roulette_animation', {
                'winner_id': game_state["current_player"],
                'winner_name': game_state["players"][game_state["current_player"]]["name"],
                'is_double': False
            }, to=room_id)
            
        update_all_clients(room_id)

@socketio.on('draw_card')
def handle_draw(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if request.sid != game_state["current_player"]: return

    fase = data.get('fase')
    tipo = data.get('type') 
    
    mandante_nome = game_state["players"][request.sid]["name"]
    alvo_nome = game_state["players"][game_state["target_player"]]["name"]
    genero_mandante = game_state["players"][request.sid]["gender"]

    session_cards = room["session_cards"]
    if fase in session_cards and tipo in session_cards[fase]:
        available_pools = [k for k in ["A", genero_mandante] if session_cards[fase][tipo][k]]
        if not available_pools:
            session_cards[fase][tipo] = copy.deepcopy(ORIGINAL_CARDS[fase][tipo])
            available_pools = [k for k in ["A", genero_mandante] if session_cards[fase][tipo][k]]
            
        chosen_pool = random.choice(available_pools)
        text = session_cards[fase][tipo][chosen_pool].pop(random.randint(0, len(session_cards[fase][tipo][chosen_pool]) - 1))
        text_formatado = text.replace("{mandante}", mandante_nome).replace("{alvo}", alvo_nome)
        
        pontos_fase = {"fase1": 1, "fase2": 2, "fase3": 4}[fase]
        fase_labels = {"fase1": "AQUECIMENTO", "fase2": "EXIBIÇÃO & VÍDEO", "fase3": "ORGÁSMO GUIADO"}
        
        game_state["current_cards"] = {
            "fase_key": f"cards_{fase}_{tipo}",
            "real_fase": fase,
            "type": f"{fase_labels[fase]} - {tipo.upper()}", 
            "text": text_formatado,
            "duration": discover_time(text),
            "points": pontos_fase
        }
        update_all_clients(room_id)

@socketio.on('roll_dice')
def handle_roll_dice(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if request.sid != game_state["current_player"]: return

    genero_alvo = game_state["players"][game_state["target_player"]]["gender"]
    nome_mandante = game_state["players"][request.sid]["name"]
    nome_alvo = game_state["players"][game_state["target_player"]]["name"]

    chosen_cat = game_state["dice_category"]
    if chosen_cat == "all":
        if not room.get("dice_pool_shuffle"):
            room["dice_pool_shuffle"] = ["acao_corpo", "posicao_local", "brinquedos_acessorios", "clima_intensidade"]
            random.shuffle(room["dice_pool_shuffle"])
        chosen_cat = room["dice_pool_shuffle"].pop(0)

    resultado = ""
    if chosen_cat == "acao_corpo":
        acao = random.choice(ORIGINAL_DICE["acao_corpo"]["acoes"])
        opcoes_validas = ORIGINAL_DICE["acao_corpo"]["corpo"]["A"] + ORIGINAL_DICE["acao_corpo"]["corpo"][genero_alvo]
        corpo = random.choice(opcoes_validas)
        resultado = f"🎲 [AÇÃO & CÂMERA]\n\n👉 {nome_mandante} deve: {acao.upper()} ➡️ {corpo.upper()} por 45 segundos ao vivo na tela!"
    
    elif chosen_cat == "posicao_local":
        loc = random.choice(ORIGINAL_DICE["posicao_local"]["locais"])
        pos = random.choice(ORIGINAL_DICE["posicao_local"]["posicoes_por_local"][loc])
        resultado = f"🎲 [ÂNGULO & POSIÇÃO]\n\n👉 Posicione a câmera:\n⚡ {pos.upper()}\n📍 Local: {loc.upper()}!"
        
    elif chosen_cat == "brinquedos_acessorios":
        acao = random.choice(ORIGINAL_DICE["brinquedos_acessorios"]["acoes"])
        opcoes_validas = ORIGINAL_DICE["brinquedos_acessorios"]["foco"]["A"] + ORIGINAL_DICE["brinquedos_acessorios"]["foco"][genero_alvo]
        foco = random.choice(opcoes_validas)
        resultado = f"🎲 [BRINQUEDOS & VÍDEO]\n\n👉 {nome_mandante} deve:\n⚡ {acao.upper()} ➡️ {foco.upper()}."
        
    elif chosen_cat == "clima_intensidade":
        estilo = random.choice(ORIGINAL_DICE["clima_intensidade"]["estilos"])
        restricao = random.choice(ORIGINAL_DICE["clima_intensidade"]["restricoes"])
        resultado = f"🎲 [CLIMA REMOTO]\n\n👉 Realizem as carícias no vídeo com o clima:\n🔥 {estilo.upper()}\n⚠️ Regra: {restricao.upper()}!"

    game_state["current_cards"] = {
        "fase_key": "dice",
        "real_fase": "fase2",
        "type": "🎲 DADOS ERÓTICOS À DISTÂNCIA",
        "text": resultado,
        "duration": 45 if chosen_cat == "acao_corpo" else 0,  
        "points": 2
    }
    update_all_clients(room_id)

@socketio.on('draw_time_challenge')
def handle_draw_time(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if request.sid != game_state["current_player"]: return

    if not room["session_time"]: room["session_time"] = list(ORIGINAL_CHALLENGES_TIME)

    mandante_nome = game_state["players"][request.sid]["name"]
    alvo_nome = game_state["players"][game_state["target_player"]]["name"]

    text = room["session_time"].pop(random.randint(0, len(room["session_time"]) - 1))
    text_formatado = text.replace("{mandante}", mandante_nome).replace("{alvo}", alvo_nome)
    
    game_state["current_cards"] = {
        "fase_key": "time",
        "real_fase": "fase2",
        "type": "⏱️ DESAFIO DE RESISTÊNCIA NA CÂMERA",
        "text": text_formatado,
        "duration": discover_time(text),
        "points": 3
    }
    update_all_clients(room_id)

@socketio.on('draw_never_question')
def handle_draw_never(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if not room["session_never"]: room["session_never"] = list(ORIGINAL_NEVER_CARDS)

    text = room["session_never"].pop(random.randint(0, len(room["session_never"]) - 1))
    
    game_state["current_cards"] = {
        "fase_key": "never",
        "real_fase": "fase1",
        "type": "🥂 EU NUNCA PICANTE",
        "text": f"{text}\n\n👉 Se você já fez isso, DÊ UM GOLE NA BEBIDA AO VIVO E CONFESSE!",
        "duration": 0,
        "points": 1
    }
    update_all_clients(room_id)

@socketio.on('trigger_punishment')
def handle_punishment(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    if not room["session_punishments"]: room["session_punishments"] = copy.deepcopy(ORIGINAL_PUNISHMENTS)
        
    mandante_nome = game_state["players"][request.sid]["name"]
    alvo_nome = game_state["players"][game_state["target_player"]]["name"]

    punish_text = room["session_punishments"].pop(random.randint(0, len(room["session_punishments"]) - 1))
    formatted_punish = punish_text.replace("{mandante}", mandante_nome).replace("{alvo}", alvo_nome)
    
    game_state["current_cards"] = {
        "fase_key": "punishment",
        "real_fase": "fase1",
        "type": "🛑 CASTIGO COMPULSÓRIO",
        "text": f"Você pulou a rodada!\nCumpra o seguinte castigo na câmera agora:\n\n{formatted_punish}",
        "duration": 0,  
        "points": 0
    }
    update_all_clients(room_id)

@socketio.on('request_cards_dataset')
def handle_request_dataset(data):
    room_id = data.get('room_id', '').strip().upper()
    update_all_clients(room_id)
    emit('receive_cards_dataset', {'deck': ORIGINAL_CARDS})

@socketio.on('add_custom_card')
def handle_add_custom(data):
    fase = data.get('phase')
    tipo = data.get('type')
    executor = data.get('executor')
    text = data.get('text', '').strip()
    room_id = data.get('room_id', '').strip().upper()
    
    if fase in ORIGINAL_CARDS and tipo in ORIGINAL_CARDS[fase] and executor in ['H', 'M', 'A'] and text:
        ORIGINAL_CARDS[fase][tipo][executor].append(text)
        if room_id in ACTIVE_ROOMS:
            ACTIVE_ROOMS[room_id]["session_cards"][fase][tipo][executor].append(text)
        handle_request_dataset({'room_id': room_id})

@socketio.on('delete_custom_card')
def handle_delete_custom(data):
    fase = data.get('phase')
    tipo = data.get('type')
    origin = data.get('origin')
    idx = data.get('index')
    room_id = data.get('room_id', '').strip().upper()
    
    if fase in ORIGINAL_CARDS and tipo in ORIGINAL_CARDS[fase] and origin in ['H', 'M', 'A']:
        try:
            removed = ORIGINAL_CARDS[fase][tipo][origin].pop(idx)
            if room_id in ACTIVE_ROOMS and removed in ACTIVE_ROOMS[room_id]["session_cards"][fase][tipo][origin]:
                ACTIVE_ROOMS[room_id]["session_cards"][fase][tipo][origin].remove(removed)
            handle_request_dataset({'room_id': room_id})
        except IndexError: pass

@socketio.on('end_game')
def handle_end_game(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"]: return
    game_state["game_over"] = True
    
    p_ids = list(game_state["players"].keys())
    p1_name = game_state["players"][p_ids[0]]["name"]
    p2_name = game_state["players"][p_ids[1]]["name"] if len(p_ids) > 1 else "Parceiro"
    p1_pts = game_state["scores"].get("H", 0)
    p2_pts = game_state["scores"].get("M", 0)
        
    if p1_pts > p2_pts:
        vencedor = f"🏆 {p1_name.upper()} MANDOU NA NOITE REMOTA!"
        sub = f"Com {p1_pts} pontos contra {p2_pts} de {p2_name}. Chegou a hora de cobrar o seu desejo ao vivo na câmera! 🔥"
    elif p2_pts > p1_pts:
        vencedor = f"🏆 {p2_name.upper()} MANDOU NA NOITE REMOTA!"
        sub = f"Com {p2_pts} pontos contra {p1_pts} de {p1_name}. Chegou a hora de cobrar o seu desejo ao vivo na câmera! 🔥"
    else:
        vencedor = "⚖️ EMPATE ARDENTE À DISTÂNCIA!"
        sub = f"Ambos terminaram com {p1_pts} pontos! Empate no prazer... Decidam na tela quem vai pagar o desejo agora! 😉👅"
        
    socketio.emit('game_update', {
        'is_my_turn': False,
        'card': {
            "fase_key": "game_over",
            "real_fase": "fase3",
            "type": "🏁 FIM DE JOGO À DISTÂNCIA",
            "text": f"{vencedor}\n\n{sub}",
            "duration": 0,
            "points": 0
        },
        'game_started': True,
        'game_over': True,
        'score_board': "Partida Encerrada!",
        'rounds_played': game_state["rounds_played"],
        'active_gender': "H"
    }, to=room_id)
    
    ACTIVE_ROOMS.pop(room_id, None)

@socketio.on('next_turn')
def handle_next_turn(data):
    room_id = data.get('room_id', '').strip().upper()
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    
    if not game_state["game_started"] or game_state["game_over"]: return
    executed = data.get('executed', False)
    points_to_add = game_state["current_cards"].get('points', 0) if executed else 0
    fase_atual = game_state["current_cards"].get('real_fase', 'fase1')
    gender_key = data.get('my_gender', 'H')

    game_state["scores"][gender_key] += points_to_add
    if executed and fase_atual in ["fase1", "fase2", "fase3"]:
        game_state["rounds_played"][gender_key][fase_atual] += 1
        
    p_ids = list(game_state["players"].keys())
    game_state["current_player"], game_state["target_player"] = game_state["target_player"], game_state["current_player"]
    game_state["current_cards"] = {}
    update_all_clients(room_id)

def update_all_clients(room_id):
    if room_id not in ACTIVE_ROOMS: return
    room = ACTIVE_ROOMS[room_id]
    game_state = room["state"]
    p_ids = list(game_state["players"].keys())
    
    p_h_name = "Homem"
    p_m_name = "Mulher"
    for pid in p_ids:
        if game_state["players"][pid]["gender"] == "H": p_h_name = game_state["players"][pid]["name"]
        if game_state["players"][pid]["gender"] == "M": p_m_name = game_state["players"][pid]["name"]

    score_text = f"📊 {p_h_name}: {game_state['scores'].get('H', 0)} pts | {p_m_name}: {game_state['scores'].get('M', 0)} pts"
    
    current_player_id = game_state["current_player"]
    current_name = game_state["players"][current_player_id]["name"] if current_player_id in game_state["players"] else "..."

    players_status = []
    for pid in p_ids:
        p = game_state["players"][pid]
        r_label = "Pronto" if p["ready"] else "Aguardando..."
        players_status.append(f"{p['name']}: {r_label}")

    for uid in p_ids:
        my_gender = game_state["players"][uid]["gender"]
        socketio.emit('game_update', {
            'is_my_turn': (uid == game_state["current_player"]),
            'mode': 'separated',
            'room_id': room_id,
            'game_type': game_state["game_type"],
            'dice_category': game_state["dice_category"],
            'current_player_name': current_name,
            'card': game_state["current_cards"],
            'game_started': game_state["game_started"],
            'game_over': game_state["game_over"],
            'score_board': score_text,
            'rounds_played': game_state["rounds_played"],
            'players_status': players_status,
            'am_i_ready': game_state["players"][uid]["ready"],
            'active_gender': my_gender
        }, room=uid)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
