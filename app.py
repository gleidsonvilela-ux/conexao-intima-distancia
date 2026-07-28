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

# 🌐 BARALHO MASSIVO - INTERAÇÃO À DISTÂNCIA (WHATSAPP, ÁUDIOS, FOTOS E VÍDEO RELÂMPAGO)
ORIGINAL_CARDS = {
    "fase1": {
        "verdade": {
            "H": [
                "De 0 a 10, quão ansioso {mandante} está hoje e o que {alvo} poderia te mandar em um áudio agora para chegar ao 10?",
                "Qual foi o pensamento mais safado que {mandante} teve com {alvo} hoje enquanto pensava na vida?",
                "Confesse no chat: você prefere receber uma foto de {alvo} totalmente nua ou de lingerie provocante com salto?",
                "Envie uma mensagem de texto privada para {alvo} confessando qual parte do corpo dela você mais queria estar tocando agora.",
                "Se você pudesse pedir uma foto surpresa de {alvo} usando qualquer peça do guarda-roupa dela hoje, qual seria?",
                "Qual foi o elogio mais safado que você queria ter mandado em um áudio hoje, mas guardou para o jogo?",
                "Qual das fotos secretas de {alvo} salvas no seu celular você mais olha quando está com saudades?",
                "Confesse: qual foi o momento da semana em que você sentiu o maior tesão repentino pensando em {alvo}?",
                "Se você pudesse escolher uma peça de roupa para eu tirar por foto agora, qual seria?",
                "Qual o ângulo de foto meu no WhatsApp que mais desperta seus pensamentos proibidos?",
                "Confesse: você já olhou uma foto minha recente e precisou fechar os olhos imaginando meu toque?",
                "Se a gente estivesse em um hotel agora com essa mesma luz, qual a primeira coisa que me pediria para fazer?",
                "Qual a frase mais provocante que eu já te mandei por mensagem e que ficou gravada na sua memória?",
                "Qual figurinha ou emoji safado do seu teclado você mais tem vontade de usar comigo hoje?",
                "Se eu te mandasse um áudio sussurrado de 5 segundos agora, qual palavra você gostaria de ouvir?"
            ],
            "M": [
                "Diga para {alvo} no áudio o que ele escreve ou fala no tom de voz que mais te deixa molhada a distância?",
                "Qual é o seu maior fetiche visual? Diga para {alvo} que tipo de foto ele pode te mandar agora que te ativa na hora.",
                "Se você pudesse fazer um pedido proibido para {alvo} cumprir por foto ou áudio agora, qual seria?",
                "Qual brinquedo erótico seu você mais usou pensando em {alvo} enquanto estavam longe?",
                "Qual foi a última conversa por mensagem nossa que te deixou com pensamentos pecaminosos o dia todo?",
                "Qual é o estilo de foto ou visual de {alvo} que mais desperta seus desejos no meio da semana?",
                "Se você pudesse receber um áudio de 10 segundos de {alvo} agora, qual frase safada você pediria para ele sussurrar?",
                "Qual foi o momento mais arriscado em que você leu uma mensagem safada minha e precisou disfarçar?",
                "Se eu te mandasse uma foto do meu peitoral nu agora no WhatsApp, qual seria a sua primeira reação?",
                "Diga a verdade: o tom de voz grave dele em um áudio de madrugada te faz arrepiar inteira?",
                "Qual peça de roupa dele você mais gosta de ver quando ele te manda uma selfie no dia a dia?",
                "Se pudéssemos parar tudo e ir para um quarto fechado pelos próximos 30 minutos, o que faremos?",
                "Qual o fetiche mais ousado que você tem vontade de realizar com ele no nosso próximo encontro?",
                "Você prefere mensagens provocantes ao longo do dia todo ou um áudio pesado direto à noite?"
            ],
            "A": [
                "Qual foi a foto ou áudio mais marcante e ousado que já trocaram no WhatsApp até hoje?",
                "Se a conexão caísse agora, qual seria a primeira mensagem proibida que você mandaria no chat?",
                "Vocês sentem que a saudade da distância aumenta a intensidade e o tesão na hora do reencontro presencial?",
                "Qual figurinha ou emoji safado do WhatsApp melhor resume o que vocês querem fazer um com o outro?",
                "Qual é a maior loucura que vocês já planejaram por mensagem para o próximo final de semana juntos?",
                "Se vocês tivessem que definir o clima da noite em uma única palavra pelo WhatsApp, qual seria?"
            ]
        },
        "desafio": {
            "H": [
                "{mandante} deve enviar um áudio no WhatsApp de 15 segundos com tom de voz bem grave e sussurrado, dizendo exatamente o que vai fazer com {alvo} no próximo encontro. 🎙️🔥",
                "{mandante} deve tirar uma foto do seu peitoral/abdômen (pode ser no espelho) e enviar como **Visualização Única** no WhatsApp de {alvo}. 📸",
                "{mandante}, puxe a gola da camisa ou fique sem camisa, tire uma foto com seu olhar mais dominante e envie no chat do WhatsApp.",
                "{mandante} deve gravar um áudio narrando em 1 minuto o início de um **Conto Erótico** imaginando um encontro surpresa de vocês dois em um hotel.",
                "{mandante} deve mandar uma foto do seu perfume ou relógio/acessório favorito no WhatsApp com a legenda: 'Guardando para quando eu te pegar'.",
                "{mandante}, tire uma foto aproximada dos seus lábios, morda o lábio inferior e envie como **Visualização Única** para {alvo}.",
                "{mandante} deve gravar um áudio de 10 segundos dando 3 suspiros bem graves e profundos no microfone do celular.",
                "{mandante}, abra a calça ou bermuda e mande uma foto da sua mão posicionada por cima da cueca no WhatsApp de {alvo}.",
                "{mandante} deve enviar uma mensagem no WhatsApp listando 3 coisas que ama ver no corpo de {alvo} quando ela se arruma.",
                "{mandante}, grave um vídeo de 5 segundos no WhatsApp mostrando a sua boca dizendo 'Você é minha' e envie em visualização única."
            ],
            "M": [
                "SPOILER REMOTO: {mandante} deve tirar uma foto do seu decote ou da lingerie e enviar como **Visualização Única** no WhatsApp de {alvo}. 📸🔞",
                "{mandante} deve gravar um áudio no WhatsApp no tom de voz mais dócil e safado dizendo o quanto quer o corpo de {alvo} hoje. 🎙️",
                "{mandante}, tire uma foto provocante da sua perna/coxa ou salto alto e envie no chat de {alvo} com uma provocação.",
                "{mandante} deve tirar uma selfie fazendo um biquinho sexy com batom ou mordendo os lábios e mandar no WhatsApp dele.",
                "{mandante} deve mandar um áudio de 10 segundos no WhatsApp dando 3 suspiros bem provocantes bem perto do microfone.",
                "{mandante}, tire uma foto de costas mostrando a curva do seu quadril ou da sua lingerie e mande em **Visualização Única**.",
                "{mandante} deve gravar um áudio de 15 segundos contando qual lingerie está usando por baixo da roupa agora.",
                "{mandante}, deslize a mão pela própria coxa, tire uma foto e mande no WhatsApp de {alvo} com a legenda: 'Imagina se fosse sua mão'.",
                "{mandante} deve enviar uma foto da sua boca com a ponta da língua para fora provocando ele no chat.",
                "{mandante}, grave um áudio curtinho rindo de forma manhosa e mandando um beijo estalado no microfone."
            ],
            "A": [
                "TRILHA SONORA MÚTUA: Ambos devem abrir o aplicativo de música e enviar o link da música mais sensual da sua playlist no chat agora.",
                "RELAXAMENTO À DISTÂNCIA: Gravarem simultaneamente um áudio de 15 segundos respirando fundo e mandarem um para o outro.",
                "TROCA DE FOTOS: Ambos devem tirar uma foto dos próprios olhos encarando a câmera e enviar no chat ao mesmo tempo.",
                "PROMESSA AGENDADA: Mandem uma mensagem no WhatsApp marcando exatamente o dia e horário do próximo encontro presencial."
            ]
        }
    },
    "fase2": {
        "verdade": {
            "H": [
                "O que te dá mais tesão na distância: ouvir os gemidos de {alvo} por áudio ou receber uma foto de visualização única?",
                "Se {alvo} te mandasse um vídeo curto de 10 segundos agora, qual parte do corpo dela você exigiria ver?",
                "Qual a sensação de saber que {alvo} está se tocando do outro lado da tela pensando unicamente em você?",
                "Qual o comando por áudio que você mais tem vontade de dar para ela quando a Fase 3 chegar?",
                "Se {alvo} te dissesse que tirou toda a roupa agora no quarto dela, qual seria seu primeiro pedido?",
                "Qual o maior tesão em receber uma foto ousada e ver ela sumir na tela de visualização única?",
                "Se você pudesse mandar ela usar um brinquedo erótico específico agora enquanto te ouve, qual seria?"
            ],
            "M": [
                "Qual foi a última vez que você se masturbou pensando em {alvo} e qual foi a cena exata que imaginou?",
                "Olhando para as mensagens de {alvo} agora, qual o nível de desejo de ver uma foto dele totalmente nu?",
                "Qual a sensação de enviar uma foto ousada sabendo o controle e a loucura que isso causa na mente dele?",
                "Você prefere quando ele comanda o seu toque por mensagens de áudio ou quando ele apenas assiste em silêncio?",
                "Qual brinquedo do seu estoque te deixa mais louca quando você usa ouvindo a voz dele no fone?",
                "Se ele te mandasse uma foto do membro rígido agora no WhatsApp, qual seria a sua frase de resposta?",
                "Qual parte do seu corpo você mais gosta de fotografar para deixar ele louco a distância?"
            ],
            "A": [
                "Vocês preferem quando a troca de provocações a distância é lenta ao longo do dia ou intensa de uma vez só à noite?",
                "Qual foi o momento mais arriscado ou inusitado em que mandaram um áudio/foto safada um para o outro?",
                "Quão mais quente fica a conversa quando os dois começam a beber um gole de vinho ou cerveja durante o jogo?",
                "Qual foi a foto mais ousada que vocês já apagaram por medo de alguém ver no celular?"
            ]
        },
        "desafio": {
            "H": [
                "{mandante} deve abrir a calça, tirar uma foto do seu membro rígido por cima ou por dentro da cueca e mandar como **Visualização Única** no WhatsApp. 🔞",
                "CHAMADA RELÂMPAGO: {mandante} deve ligar em vídeo no WhatsApp por **exatamente 45 segundos** para mostrar seu peitoral nu e desligar sem falar nada! 📹⚡",
                "{mandante} deve gravar um áudio de 30 segundos dando ordens sussurradas e firmes de como quer que {alvo} toque os próprios seios agora.",
                "{mandante} deve passar um cubo de gelo ou óleo no peitoral, tirar uma foto com a pele brilhando e mandar no WhatsApp.",
                "{mandante}, tire a cueca/shorts, faça uma foto do seu corpo nu do peito até as coxas e mande em visualização única.",
                "{mandante} deve gravar um áudio de 20 segundos descrevendo a sensação de estar ereto e imaginando o corpo de {alvo}.",
                "{mandante}, faça um vídeo curto de 5 segundos mostrando a sua mão acariciando o próprio abdômen e mande em visualização única.",
                "{mandante} deve enviar um áudio dando uma ordem direta: mande ela tirar uma peça de roupa e te provar por foto!"
            ],
            "M": [
                "{mandante} deve tirar o sutiã/blusa, fazer uma foto bem angulada dos seus seios nus e mandar como **Visualização Única** no WhatsApp de {alvo}. 📸",
                "CHAMADA RELÂMPAGO: {mandante} deve fazer uma chamada de vídeo no WhatsApp de **45 segundos** mostrando sua lingerie/corpo de cima a baixo e desligar! 📹⚡",
                "{mandante} deve gravar um áudio de 20 segundos gemendo baixo no microfone enquanto passa os dedos na própria intimidade.",
                "{mandante} deve tirar a calcinha, tirar uma foto apenas da calcinha na cama e enviar no WhatsApp com a legenda: 'Fiquei sem'.",
                "{mandante}, fique de quatro na cama, tire uma foto do seu bumbum nu ou de calcinha por trás e envie em visualização única.",
                "{mandante} deve pegar o seu vibrador ou sugador, ligar perto do microfone e gravar um áudio de 15 segundos com o som do brinquedo.",
                "{mandante}, passe um pouco de gel ou creme nas coxas, tire uma foto aproximada e mande no WhatsApp de {alvo}.",
                "{mandante} deve enviar uma foto do seu mamilo roçando na ponta dos seus dedos em visualização única."
            ],
            "A": [
                "FLAGRANTE DA NOITE: Ambos devem tirar um print da tela do próprio celular agora e enviar no chat para provar como estão acompanhando o jogo.",
                "RESTRIÇÃO DE ÁUDIO: Pelas próximas 2 rodadas, todas as respostas só podem ser enviadas por **mensagens de voz sussurradas** no WhatsApp.",
                "SEM MÃOS NO CHAT: Pelas próximas 2 rodadas, é proibido digitar texto. Usem apenas a gravação de áudio do WhatsApp!",
                "SINAL DE ILUMINAÇÃO: Apaguem as luzes do quarto agora e mandem uma foto apenas com a iluminação do celular refletindo na pele."
            ]
        }
    },
    "fase3": {
        "verdade": {
            "H": [
                "Qual palavra ou comando de voz seu você sabe que faz {alvo} chegar ao limite mais rápido?",
                "Qual a sensação de saber que a sua voz no fone de ouvido é o suficiente para fazer ela ter um orgasmo?",
                "Quão intenso é para você se masturbar ouvindo os sussurros de {alvo} gravados no áudio?",
                "Qual o maior fetiche que você tem em ver uma foto do pós-orgasmo dela no WhatsApp?"
            ],
            "M": [
                "Qual palavra sussurrada por {alvo} no áudio desarma totalmente você durante a sua masturbação?",
                "O fetiche de mandar uma foto do pós-orgasmo para ele aumenta o seu nível de tesão?",
                "Qual o ritmo do brinquedo ou dos dedos que mais combina quando você escuta a voz dele no fone?",
                "Quão perto do celular você deixa o rosto quando sente que o clímax está chegando?"
            ],
            "A": [
                "Quão mais forte fica a ansiedade do reencontro presencial depois de cumprirem esta Fase 3 à distância?",
                "Qual é a primeira loucura que vocês prometem fazer na cama no segundo em que abrirem a porta do quarto?",
                "Vocês concordam que o sexo à distância através de mídias e voz deixa o reencontro 10 vezes mais explosivo?"
            ]
        },
        "desafio": {
            "H": [
                "COMANDO DOMINANTE: {mandante} deve mandar um áudio de 45 segundos no WhatsApp dando instruções detalhadas de como {alvo} deve se masturbar até suspirar alto. 🎙️🔥",
                "{mandante} deve se masturbar agora ouvindo os áudios de {alvo}. Assim que gozar, envie uma mensagem de texto simples dizendo: 'Gozei pensando em você'.",
                "VÍDEO RELÂMPAGO FINAL: {mandante} deve gravar um vídeo curto de 10 segundos no WhatsApp focando no seu peitoral/membro e mandar em visualização única.",
                "{mandante} deve gravar um áudio no tom mais dominante possível dizendo exatamente o momento em que ela tem permissão para gozar.",
                "{mandante}, tire uma foto do seu rosto e peitoral logo após se satisfazer e mande em visualização única no WhatsApp de {alvo}."
            ],
            "M": [
                "ORGASMO GUIADO: {mandante} deve se tocar usando os dedos ou brinquedo focado no clitóris. Assim que atingir o clímax, mande um áudio de 10 segundos arfando no microfone. 🎙️💦",
                "FOTO DO CLÍMAX: {mandante} deve tirar uma foto da sua intimidade molhada ou do seu rosto logo após gozar e mandar como **Visualização Única** no WhatsApp.",
                "VÍDEO RELÂMPAGO FINAL: {mandante} deve gravar um vídeo curto de 10 segundos no WhatsApp mostrando o uso do brinquedo/dedos e mandar em visualização única.",
                "{mandante} deve ligar o sugador/vibrador no nível máximo, aproximar do microfone do WhatsApp e mandar um áudio de 15 segundos do seu suspiro no ápice.",
                "{mandante}, grave um áudio de 5 segundos sussurrando bem fundo no fone dele: 'Sou toda sua'."
            ],
            "A": [
                "CLÍMAX SINCRONIZADO REMOTO: Esqueçam as cartas. Liguem uma **Chamada de Áudio de 3 minutos** no WhatsApp e masturbem-se juntos ouvindo a respiração um do outro até os dois gozarem!",
                "PROMESSA DO REENCONTRO: Mande uma mensagem de texto no WhatsApp detalhando a primeira coisa sem limites que você vai fazer assim que abrirem a porta do quarto no próximo encontro.",
                "PÓS-ORGASMO MÚTUO: Mandem um áudio de 10 segundos cada um dizendo o quanto amam a conexão de vocês, mesmo a quilômetros de distância."
            ]
        }
    }
}

ORIGINAL_DICE = {
    "acao_corpo": {
        "acoes": [
            "Mandar um áudio sussurrado no WhatsApp sobre",
            "Tirar uma foto de visualização única mostrando",
            "Fazer uma chamada de vídeo relâmpago de 30 segundos focando em",
            "Gravar um vídeo curto de 10 segundos destacando",
            "Enviar uma foto em close bem de perto aproximando",
            "Gravar um áudio de 15 segundos respirando fundo sobre",
            "Mandar uma mensagem de texto bem explícita descrevendo"
        ],
        "corpo": {
            "H": ["o peitoral nu", "o abdômen rígido", "o membro por dentro da cueca", "os lábios no microfone", "o pescoço suado"],
            "M": ["os mamilos nus", "a lingerie sexy", "a intimidade molhada", "as coxas no espelho", "a curva da bunda"],
            "A": ["o pescoço", "a virilha", "os lábios", "as mãos"]
        }
    },
    "posicao_local": {
        "locais": ["na cama com luz apagada", "na frente do espelho do banheiro", "na cadeira de frente para o celular", "deitado(a) no chão do quarto", "na beira da cama"],
        "posicoes_por_local": {
            "na cama com luz apagada": ["Tirar foto deitada(o) de costas", "Gravar áudio de conchinha na cama", "Foto aproximada apenas da pele sob a colcha"],
            "na frente do espelho do banheiro": ["Tirar foto do corpo inteiro no espelho", "Foto do ângulo de costas no espelho", "Foto do rosto mordendo os lábios no espelho"],
            "na cadeira de frente para o celular": ["Foto sentada(o) na ponta da cadeira", "Áudio de voz marcante na cadeira", "Foto das pernas/coxas na cadeira"],
            "deitado(a) no chão do quarto": ["Foto do ângulo vindo de cima", "Áudio sussurrado encostado no chão"],
            "na beira da cama": ["Foto do quadril elevado", "Áudio arfando na beirada da cama"]
        }
    },
    "brinquedos_acessorios": {
        "acoes": [
            "Mandar foto usando a lingerie/cueca favorita em",
            "Gravar áudio usando o vibrador/sugador ligado ao fundo em",
            "Tirar foto com fone de ouvido e olhar provocante para",
            "Mandar foto de visualização única com um acessório especial em",
            "Gravar um áudio aproximando o brinquedo erótico de"
        ],
        "foco": {
            "H": ["o membro ereto", "o abdômen", "o peitoral"],
            "M": ["o clitóris", "os mamilos", "a bunda nua"],
            "A": ["a virilha", "o pescoço", "as coxas"]
        }
    },
    "clima_intensidade": {
        "estilos": [
            "Tom de voz sussurrado e extremamente dominante",
            "Provocação total: mande a foto, mas proíba o par de se tocar por 5 minutos",
            "Comunicação apenas por emojis e figurinhas de fetiche no WhatsApp",
            "Modo silêncio total: responda apenas com fotos sem escrever nada",
            "Ritmo acelerado: mande a mídia em menos de 20 segundos!"
        ],
        "restricoes": [
            "usando apenas fotos de visualização única (View Once)",
            "sem poder digitar nada (apenas mensagens de voz)",
            "com a luz do quarto totalmente apagada",
            "usando apenas fones de ouvido no volume máximo",
            "sem poder usar o filtro da câmera"
        ]
    }
}

ORIGINAL_CHALLENGES_TIME = [
    "{mandante} deve gravar um áudio de 60 segundos no WhatsApp narrando um desejo proibido sem pausar para respirar!",
    "{mandante} deve enviar uma foto de visualização única a cada 15 segundos durante 1 minuto (4 fotos seguidas no WhatsApp).",
    "{mandante} deve ligar em áudio no WhatsApp e dar 3 suspiros bem provocantes ininterruptos durante 45 segundos.",
    "{mandante} tem 30 segundos para tirar uma foto do seu corpo sem camisa/sem lingerie e mandar no chat do WhatsApp!",
    "{mandante} deve mandar 3 áudios seguidos de 10 segundos sussurrando frases afiadas no ouvido de {alvo} em menos de 1 minuto."
]

ORIGINAL_NEVER_CARDS = [
    "Eu nunca tirei uma foto ousada para enviar para o meu par no meio do expediente de trabalho.",
    "Eu nunca me masturbei assistindo a um vídeo ou áudio antigo nosso enquanto estávamos longe.",
    "Eu nunca fiquei com tanta vontade do meu par a distância que precisei parar o que estava fazendo para mandar um áudio proibido.",
    "Eu nunca tirei uma foto secreta no espelho do banheiro de um restaurante só para mandar para o meu par.",
    "Eu nunca fingi que estava dormindo no chat só para ver se o meu par mandava uma foto surpresa provocante.",
    "Eu nunca me toquei ouvindo apenas a respiração do meu par durante uma ligação noturna."
]

ORIGINAL_PUNISHMENTS = [
    "Enviar uma foto de visualização única sem filtro no WhatsApp agora mesmo.",
    "Ficar sem mandar nenhuma mensagem de texto e responder apenas por áudios de voz pelas próximas 2 rodadas.",
    "Mandar um áudio de 10 segundos dando 3 gemidos baixinhos no microfone do celular.",
    "Tirar mais uma peça de roupa e mandar uma foto do detalhe no chat do WhatsApp.",
    "Confessar em um áudio de 20 segundos a última cena nossa em que você mais sentiu tesão."
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
        fase_labels = {"fase1": "PROVOCAÇÃO REMOTA", "fase2": "MÍDIAS & AÇÃO", "fase3": "CLÍMAX GUIADO"}
        
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
        resultado = f"🎲 [AÇÃO & MÍDIA]\n\n👉 {nome_mandante} deve: {acao.upper()} ➡️ {corpo.upper()} de {nome_alvo}!"
    
    elif chosen_cat == "posicao_local":
        loc = random.choice(ORIGINAL_DICE["posicao_local"]["locais"])
        pos = random.choice(ORIGINAL_DICE["posicao_local"]["posicoes_por_local"][loc])
        resultado = f"🎲 [FOTO / ÂNGULO]\n\n👉 Tire a foto ou faça a ação:\n⚡ {pos.upper()}\n📍 Local: {loc.upper()}!"
        
    elif chosen_cat == "brinquedos_acessorios":
        acao = random.choice(ORIGINAL_DICE["brinquedos_acessorios"]["acoes"])
        opcoes_validas = ORIGINAL_DICE["brinquedos_acessorios"]["foco"]["A"] + ORIGINAL_DICE["brinquedos_acessorios"]["foco"][genero_alvo]
        foco = random.choice(opcoes_validas)
        resultado = f"🎲 [BRINQUEDOS & FOTOS]\n\n👉 {nome_mandante} deve:\n⚡ {acao.upper()} ➡️ {foco.upper()}."
        
    elif chosen_cat == "clima_intensidade":
        estilo = random.choice(ORIGINAL_DICE["clima_intensidade"]["estilos"])
        restricao = random.choice(ORIGINAL_DICE["clima_intensidade"]["restricoes"])
        resultado = f"🎲 [CLIMA REMOTO]\n\n👉 Envie as mídias da rodada no clima:\n🔥 {estilo.upper()}\n⚠️ Regra: {restricao.upper()}!"

    game_state["current_cards"] = {
        "fase_key": "dice",
        "real_fase": "fase2",
        "type": "🎲 DADOS ERÓTICOS À DISTÂNCIA",
        "text": resultado,
        "duration": 0,  
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
        "type": "⏱️ DESAFIO DE RESISTÊNCIA REMOTA",
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
        "text": f"{text}\n\n👉 Se você já fez isso, DÊ UM GOLE NA BEBIDA E MANDE UM EMOJI NO CHAT!",
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
        "text": f"Você pulou a rodada!\nCumpra o seguinte castigo no WhatsApp agora:\n\n{formatted_punish}",
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
        sub = f"Com {p1_pts} pontos contra {p2_pts} de {p2_name}. Chegou a hora de cobrar o seu desejo pelo WhatsApp! 🔥"
    elif p2_pts > p1_pts:
        vencedor = f"🏆 {p2_name.upper()} MANDOU NA NOITE REMOTA!"
        sub = f"Com {p2_pts} pontos contra {p1_pts} de {p1_name}. Chegou a hora de cobrar o seu desejo pelo WhatsApp! 🔥"
    else:
        vencedor = "⚖️ EMPATE ARDENTE À DISTÂNCIA!"
        sub = f"Ambos terminaram com {p1_pts} pontos! Empate no prazer... Decidam no chat quem vai pagar o desejo agora! 😉👅"
        
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
